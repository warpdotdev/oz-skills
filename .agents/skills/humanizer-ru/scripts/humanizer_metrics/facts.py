"""Факт-замок как скрипт: что из фактов исходника дожило до результата.

Скилл обещает переносить числа, даты, имена, названия и ссылки без искажений и
не добавлять новых. Инструкция модели это одно, проверка другое: этот модуль
вынимает из двух текстов «факты» и сравнивает множества. Не семантика и не
фактчек: только сохранность того, что уже было, и появление того, чего не было.

Классы фактов:
- число: любой токен с цифрой (проценты, годы, суммы), нормализован до цифр;
- число словами: крупные числительные («сорок», «тысяча»), их не пересказывают;
- месяц: названия месяцев как замена дате;
- ссылка: URL и адреса вида domain.tld/path;
- код: содержимое инлайн-кода в бэктиках;
- имя: слово с заглавной не в начале предложения (с pymorphy3 точнее: теги
  Name/Surn/Geox/Orgn/Patr и незнакомые словарю слова), плюс любая латиница с
  заглавной («Excel», «GPT-4»).

Мелкие количества («два», «половина», «вдвое») факты мягкие: в русском они
идиоматичны («с одной стороны») и обычно пересказывают число исходника. Они
считаются, но не валят проверку.

Утверждения: слова-кванторы, которые звучат как пафос, а несут факт:
«первый в России», «единственный», «впервые», «рекордный», «до сих пор».
Срезать «первый в России сервис» до «сервис» значит исказить исходник, а
не оживить его. Потерянный квантор попадает в список потерь, появившийся
выносится отдельным предупреждением: кванторы идиоматичны («первый шаг»,
«самое время»), поэтому валить проверку автоматически нельзя, но глазами
такое место обязано проверить.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

try:
    import pymorphy3

    _MORPH = pymorphy3.MorphAnalyzer()
except ImportError:  # без словаря сравниваем по основе, грубее, но работает
    _MORPH = None

PROPER_TAGS = {"Name", "Surn", "Geox", "Orgn", "Patr"}

MONTH_RE = re.compile(
    r"\b(январ|феврал|март|апрел|июн|июл|август|сентябр|октябр|ноябр|декабр)[а-я]*\b",
    re.IGNORECASE,
)
URL_RE = re.compile(r"https?://[^\s)>\]»]+|\b[a-z0-9-]+\.(?:ru|com|org|net|io|tech|dev|ai|su|рф)(?:/[^\s)>\]»]*)?",
                    re.IGNORECASE)
CODE_RE = re.compile(r"`([^`\n]+)`")
TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z\d\-]*|[А-Яа-яЁё][А-Яа-яЁё\-]*|\d[\d.,:/-]*")

SOFT_QUANTITIES = {
    "один", "два", "две", "три", "оба", "обе", "пара",
    "второй", "третий",
    "вдвое", "втрое", "дважды", "трижды",
    "половина", "треть", "четверть", "полтора",
}
HARD_NUMERALS = {
    "четыре", "пять", "шесть", "семь", "восемь", "девять", "десять",
    "одиннадцать", "двенадцать", "пятнадцать", "двадцать", "тридцать",
    "сорок", "пятьдесят", "шестьдесят", "семьдесят", "восемьдесят",
    "девяносто", "сто", "двести", "триста", "тысяча", "миллион", "миллиард",
    "десяток", "сотня", "дюжина",
}
# Кванторы-утверждения: громкие слова, за которыми стоит проверяемый факт.
CLAIM_WORDS = {
    "первый", "единственный", "впервые", "самый", "рекордный", "крупнейший",
    "старейший", "никогда", "никто", "навсегда", "беспрецедентный",
}
CLAIM_PHRASE_RE = re.compile(r"\bдо сих пор\b|\bв мире\b|\bв россии\b", re.IGNORECASE)
# Одна сущность под разными именами не считается новым фактом.
ALIASES = {
    "ai": ("искусственный", "интеллект", "ии", "нейросеть", "модель"),
    "ии": ("искусственный", "интеллект", "ai", "нейросеть", "модель"),
    "llm": ("модель", "нейросеть", "ai", "ии"),
}


@dataclass
class Facts:
    hard: set[str] = field(default_factory=set)   # "число:13", "имя:стэнфорд", "ссылка:…"
    soft: set[str] = field(default_factory=set)   # "два", "половина"
    words: set[str] = field(default_factory=set)  # все слова в нормальной форме, для алиасов
    claims: set[str] = field(default_factory=set)  # "утверждение:первый", "утверждение:до сих пор"


@dataclass
class FactsDiff:
    lost: list[str]      # были в исходнике, пропали
    added: list[str]     # появились в результате, в исходнике не было
    kept: int            # жёстких фактов исходника дожило
    soft_added: list[str]
    claims_added: list[str] = field(default_factory=list)  # кванторы, которых в исходнике не было

    @property
    def ok(self) -> bool:
        return not self.added

    def as_dict(self) -> dict:
        return {"ok": self.ok, "lost": self.lost, "added": self.added,
                "kept": self.kept, "soft_added": self.soft_added,
                "claims_added": self.claims_added}


def _norm(word: str) -> str:
    low = word.lower().replace("ё", "е").strip("-")
    if _MORPH is None:
        return low[:5]
    return _MORPH.parse(low)[0].normal_form.replace("ё", "е")


def _sentence_starts(text: str) -> set[int]:
    starts = {0}
    for m in re.finditer(r"[.!?…]\s+|^[>\-*]\s+|«|\n", text):
        starts.add(m.end())
    return starts


def _is_proper(word: str, at_start: bool) -> bool:
    if not word[:1].isupper():
        return False
    if word.isascii():
        return True
    if _MORPH is None:
        return not at_start
    p = _MORPH.parse(word.lower())[0]
    if PROPER_TAGS & set(p.tag.grammemes):
        return True
    if not p.is_known:
        return True
    return not at_start


def extract_facts(text: str) -> Facts:
    f = Facts()
    for m in URL_RE.finditer(text):
        url = re.sub(r"^https?://(?:www\.)?", "", m.group(0).rstrip(".,;:").lower()).rstrip("/")
        f.hard.add("ссылка:" + url)
    for m in CODE_RE.finditer(text):
        f.hard.add("код:" + m.group(1).strip())
    body = CODE_RE.sub(" ", URL_RE.sub(" ", text))
    for m in MONTH_RE.finditer(body):
        f.hard.add("месяц:" + m.group(1).lower())
    for m in CLAIM_PHRASE_RE.finditer(body):
        f.claims.add("утверждение:" + m.group(0).lower().replace("ё", "е"))
    starts = _sentence_starts(body)
    for m in TOKEN_RE.finditer(body):
        tok = m.group(0)
        if tok[0].isdigit():
            digits = re.sub(r"\D", "", tok)
            if digits:
                f.hard.add("число:" + (digits.lstrip("0") or "0"))
            continue
        norm = _norm(tok)
        f.words.add(norm)
        if norm in SOFT_QUANTITIES:
            f.soft.add(norm)
        elif norm in CLAIM_WORDS:
            f.claims.add("утверждение:" + norm)
        elif norm in HARD_NUMERALS:
            f.hard.add("число словами:" + norm)
        elif _is_proper(tok, any(abs(m.start() - s) <= 1 for s in starts)):
            f.hard.add("имя:" + norm)
    return f


def _alias_covered(fact: str, before_words: set[str]) -> bool:
    if not fact.startswith("имя:"):
        return False
    name = fact[4:]
    return any(alias in before_words for alias in ALIASES.get(name, ()))


def diff_facts(before: str, after: str) -> FactsDiff:
    b, a = extract_facts(before), extract_facts(after)
    lost = sorted(b.hard - a.hard) + sorted(b.claims - a.claims)
    added = sorted(x for x in a.hard - b.hard if not _alias_covered(x, b.words))
    return FactsDiff(lost=lost, added=added, kept=len(b.hard & a.hard),
                     soft_added=sorted(a.soft - b.soft),
                     claims_added=sorted(a.claims - b.claims))


def facts_verdict(d: FactsDiff) -> str:
    if d.added:
        return f"✗ новых фактов без источника: {len(d.added)} (выдумка хуже канцелярита)"
    if d.lost:
        return f"⚠ факты исходника на месте, но {len(d.lost)} потеряно: проверьте, намеренно ли"
    if d.claims_added:
        return (f"⚠ факты целы, но появилось утверждений без источника: {len(d.claims_added)} "
                "(«впервые», «единственный» это факт, а не украшение)")
    return f"✓ факт-замок цел: {d.kept} фактов исходника перенесено, новых нет"
