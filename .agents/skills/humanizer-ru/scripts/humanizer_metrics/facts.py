"""Факт-замок как скрипт: что из фактов исходника дожило до результата.

Скилл обещает переносить числа, даты, имена, названия и ссылки без искажений и
не добавлять новых. Инструкция модели это одно, проверка другое: этот модуль
вынимает из двух текстов «факты» и сравнивает множества. Не семантика и не
фактчек: только сохранность того, что уже было, и появление того, чего не было.

Классы фактов:
- число: значение с сохранением знака, десятичного разделителя, диапазона и даты;
- величина: число вместе с распознанной единицей (проценты, рубли, масштабы);
- число словами: крупные числительные («сорок», «тысяча»), их не пересказывают;
- месяц: названия месяцев как замена дате;
- ссылка: URL и адреса вида domain.tld/path;
- код: содержимое инлайн-кода в бэктиках;
- имя: слово с заглавной не в начале предложения, а в начале предложения по
  тегам pymorphy3 Name/Surn/Geox/Orgn/Patr и незнакомые словарю слова, плюс
  любая латиница с заглавной («Excel», «GPT-4»).

Мелкие количества («два», «половина», «вдвое») факты мягкие: в русском они
идиоматичны («с одной стороны») и обычно пересказывают число исходника. Они
считаются, но не валят проверку.

Оговорки: «обычно», «примерно», «может», «от 5000». Снятая оговорка делает
из «обычно помогает» обещание «помогает»; она попадает в потери.

Утверждения: слова-кванторы, которые звучат как пафос, а несут факт:
«первый в России», «единственный», «впервые», «рекордный», «до сих пор».
Срезать «первый в России сервис» до «сервис» значит исказить исходник, а
не оживить его. Потерянный квантор попадает в список потерь, появившийся
выносится отдельным предупреждением: кванторы идиоматичны («первый шаг»,
«самое время»), поэтому валить проверку автоматически нельзя, но глазами
такое место обязано проверить.

Разметка: заголовки, пункты списков, строки таблиц и блочные HTML-теги. Правка
текста не должна съедать структуру документа: пропавший заголовок или пункт
попадает в потери. Снятое выделение (жирный, курсив, <strong>, <em>) только
предупреждение: шаблонный жирный сам бывает маркером, его снимают нарочно.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .morphology import get_morph

PROPER_TAGS = {"Name", "Surn", "Geox", "Orgn", "Patr"}

MONTH_RE = re.compile(
    r"\b(январ|феврал|март|апрел|июн|июл|август|сентябр|октябр|ноябр|декабр)[а-я]*\b",
    re.IGNORECASE,
)
URL_RE = re.compile(r"https?://[^\s)>\]»]+|\b[a-z0-9-]+\.(?:ru|com|org|net|io|tech|dev|ai|su|рф)(?:/[^\s)>\]»]*)?",
                    re.IGNORECASE)
CODE_RE = re.compile(r"`([^`\n]+)`")
TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z\d\-]*|[А-Яа-яЁё][А-Яа-яЁё\-]*|\d[\d.,:/-]*")

# Keep numeric structure. Dates/ranges are deliberately not evaluated as arithmetic.
NUMBER_RE = re.compile(r"(?<![A-Za-z0-9_])[-+−]?(?:\d{1,3}(?:[ \u00a0\u202f]\d{3})+|\d+)(?:[.,:/-]\d+)*")
UNIT_RE = re.compile(r"\s*(%|процентн[а-яё]*\s+пункт[а-яё]*|процент(?:а|ов|у|ом|е|ы|ам|ами|ах)?|₽|руб(?:\.|л[а-яё]*)?|млн\.?|миллион[а-яё]*|млрд\.?|миллиард[а-яё]*|тыс\.?|тысяч[а-яё]*)(?![а-яёa-z])", re.I)


def numeric_facts(text: str) -> dict[str, str]:
    result = {}
    for match in NUMBER_RE.finditer(text):
        value = re.sub(r"[ \u00a0\u202f]", "", match.group()).replace(",", ".").replace("−", "-").lstrip("+")
        if re.fullmatch(r"-?\d+", value):
            value = str(int(value))
        result["число:" + value] = match.group()
        end = match.end()
        units = []
        # Scale + currency, e.g. "5 млн рублей". One scale and one unit at most.
        for _ in range(2):
            unit_match = UNIT_RE.match(text, end)
            if not unit_match:
                break
            raw = unit_match.group(1).lower()
            unit = ("п.п." if raw.startswith("процентн") else "%" if raw == "%" or raw.startswith("процент") else
                    "руб" if raw == "₽" or raw.startswith("руб") else
                    "млн" if raw.startswith(("млн", "миллион")) else
                    "млрд" if raw.startswith(("млрд", "миллиард")) else "тыс")
            units.append(unit)
            end = unit_match.end()
            if unit in ("%", "п.п.", "руб"):
                break
        if units:
            result["величина:" + value + " " + " ".join(units)] = text[match.start():end]
    return result


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
    "главный",
}
CLAIM_PHRASE_RE = re.compile(r"\bдо сих пор\b|\bв мире\b|\bв россии\b", re.IGNORECASE)
# Оговорки при факте: задают его точность («обычно», «примерно», «от 5000»).
# Скилл снимал их в 5 ответах из 25 (eval/MODERN-SKILL-CHECK.md), и строка в
# промпте не помогла, поэтому пропавшая оговорка попадает в список потерь.
# «Может показаться» это оговорка мнения, её снимать можно.
# «Риск», «один из», «только», «если», «по данным» тоже оговорки: без них
# «риск переделок» становится «переделками», условие обещанием, а чужая
# цифра своей (eval/NEW_CASES_CHECK.md).
HEDGE_RE = re.compile(
    r"\b(?:может\s+быть|мо(?:жет|гут)(?!\s+показаться)|обычно|как\s+правило|часто|иногда|"
    r"примерно|приблизительно|около|почти|в\s+среднем|не\s+обязательно|не\s+всегда|"
    r"вероятно|скорее\s+всего|по\s+оценкам|предположительно|ожида\w*|"
    r"риск\w*|(?:один|одн(?:им|ой|ого|ом|у|а|о|и|их))\s+из|только|лишь|если|по\s+данным|"
    r"(?:от|до|свыше|более|менее|больше|меньше)(?=\s+\d))\b",
    re.IGNORECASE)
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
    hedges: set[str] = field(default_factory=set)  # "оговорка:обычно", "оговорка:от"


@dataclass
class FactsDiff:
    lost: list[str]      # были в исходнике, пропали
    added: list[str]     # появились в результате, в исходнике не было
    kept: int            # жёстких фактов исходника дожило
    soft_added: list[str]
    claims_added: list[str] = field(default_factory=list)  # кванторы, которых в исходнике не было
    emphasis_lost: list[str] = field(default_factory=list)  # снятое выделение, только предупреждение

    @property
    def ok(self) -> bool:
        return not self.added

    def as_dict(self) -> dict:
        return {"ok": self.ok, "lost": self.lost, "added": self.added,
                "kept": self.kept, "soft_added": self.soft_added,
                "claims_added": self.claims_added, "emphasis_lost": self.emphasis_lost,
                "status": "review_required" if (self.lost or self.added or self.claims_added
                                                or self.soft_added or self.emphasis_lost) else "no_detected_changes",
                "semantic_verified": False,
                "scope": "Сопоставление извлечённых элементов; смысл и связь чисел с утверждениями не проверены."}


def _norm(word: str) -> str:
    low = word.lower().replace("ё", "е").strip("-")
    return get_morph().parse(low)[0].normal_form.replace("ё", "е")


# Начало строки и всё, что Markdown ставит перед первым словом: маркер списка
# («-», «*», «•», «1.», «2)»), цитата «>», решётки заголовка, «**» жирного,
# эмодзи-буллет. Без этого «- Говорить» или «**Тема**» давали «имя:говорить».
LINE_LEAD_RE = re.compile(r"^[ \t]*(?:(?:\d{1,3}[.)]|[^\w\s«\"'(\[])[ \t]*)*", re.MULTILINE)


def _sentence_starts(text: str) -> set[int]:
    starts = {0}
    # После двоеточия, тире, открывающей кавычки и скобки заглавная тоже бывает
    # у обычного слова («Совет: Не паникуйте», «(Например: …)»). Имя из словаря
    # (теги Name, Geox, Orgn) и незнакомое словарю слово ловятся и там.
    for m in re.finditer(r"[.!?…:;—–][*_]*\s+[*_«\"„“(]*|[«\"„“(]|\n", text):
        starts.add(m.end())
    for m in LINE_LEAD_RE.finditer(text):
        starts.add(m.end())
    return starts


def _is_proper(word: str, at_start: bool) -> bool:
    if not word[:1].isupper():
        return False
    if word.isascii():
        return True
    p = get_morph().parse(word.lower())[0]
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
    for m in HEDGE_RE.finditer(body):
        h = re.sub(r"\s+", " ", m.group(0).lower())
        h = ("может" if h in ("могут", "может") else "ожидается" if h.startswith("ожида") else
             "риск" if h.startswith("риск") else "один из" if h.endswith(" из") else h)
        f.hedges.add("оговорка:" + h)
    for m in CLAIM_PHRASE_RE.finditer(body):
        f.claims.add("утверждение:" + m.group(0).lower().replace("ё", "е"))
    f.hard.update(numeric_facts(body))
    # Начало предложения с допуском в символ: множество, а не перебор, иначе
    # на длинном тексте проверка квадратичная (100 КБ шли секунды).
    starts = {s + d for s in _sentence_starts(body) for d in (-1, 0, 1)}
    for m in TOKEN_RE.finditer(body):
        tok = m.group(0)
        if tok[0].isdigit():
            continue
        norm = _norm(tok)
        f.words.add(norm)
        if norm in SOFT_QUANTITIES:
            f.soft.add(norm)
        elif norm in CLAIM_WORDS:
            f.claims.add("утверждение:" + norm)
        elif norm in HARD_NUMERALS:
            f.hard.add("число словами:" + norm)
        elif _is_proper(tok, m.start() in starts):
            f.hard.add("имя:" + norm)
    return f


def _alias_covered(fact: str, before_words: set[str]) -> bool:
    if not fact.startswith("имя:"):
        return False
    name = fact[4:]
    return any(alias in before_words for alias in ALIASES.get(name, ()))


FENCE_RE = re.compile(r"^[ \t]{0,3}(?:`{3,}|~{3,}).*?^[ \t]{0,3}(?:`{3,}|~{3,})[ \t]*$", re.MULTILINE | re.DOTALL)
STRUCTURE_RE = {
    "заголовок": re.compile(r"^[ \t]{0,3}#{1,6}[ \t]+\S|<h[1-6][\s>]", re.MULTILINE | re.IGNORECASE),
    "пункт списка": re.compile(r"^[ \t]*(?:[-*+•]|\d{1,3}[.)])[ \t]+\S|<li[\s>]", re.MULTILINE | re.IGNORECASE),
    "строка таблицы": re.compile(r"^[ \t]*\|.*\|[ \t]*$|<tr[\s>]", re.MULTILINE | re.IGNORECASE),
    "блок HTML": re.compile(r"<(?:p|div|blockquote|ul|ol|table|section|pre)[\s>]", re.IGNORECASE),
}
EMPHASIS_RE = {
    "жирный": re.compile(r"\*\*[^*\n]+\*\*|__[^_\n]+__|<(?:strong|b)[\s>]", re.IGNORECASE),
    "курсив": re.compile(r"(?<![*\w])\*[^*\s][^*\n]*\*(?![*\w])|<(?:em|i)[\s>]", re.IGNORECASE),
}


def markup_counts(text: str) -> tuple[dict[str, int], dict[str, int]]:
    body = FENCE_RE.sub("", text)
    return ({k: len(r.findall(body)) for k, r in STRUCTURE_RE.items()},
            {k: len(r.findall(body)) for k, r in EMPHASIS_RE.items()})


def diff_facts(before: str, after: str) -> FactsDiff:
    b, a = extract_facts(before), extract_facts(after)
    lost = sorted(b.hard - a.hard) + sorted(b.claims - a.claims) + sorted(b.hedges - a.hedges)
    (bs, be), (as_, ae) = markup_counts(before), markup_counts(after)
    lost += [f"разметка:{k} {bs[k]}→{as_[k]}" for k in bs if as_[k] < bs[k]]
    emphasis = [f"выделение:{k} {be[k]}→{ae[k]}" for k in be if ae[k] < be[k]]
    added = sorted(x for x in a.hard - b.hard if not _alias_covered(x, b.words))
    return FactsDiff(lost=lost, added=added, kept=len(b.hard & a.hard),
                     soft_added=sorted(a.soft - b.soft),
                     claims_added=sorted(a.claims - b.claims),
                     emphasis_lost=emphasis)


def facts_verdict(d: FactsDiff) -> str:
    scope = "Смысл, единицы вне словаря и связь чисел с утверждениями требуют ручной сверки."
    if d.added:
        return f"⚠ появились элементы, которых нет в исходнике: {len(d.added)}. {scope}"
    if d.lost:
        return f"⚠ потеряно элементов исходника: {len(d.lost)}. Проверьте, намеренно ли. {scope}"
    if d.claims_added or d.soft_added or d.emphasis_lost:
        return f"⚠ появились кванторы или количества; проверьте контекст. {scope}"
    return f"Совпало извлечённых элементов: {d.kept}; изменений в них не найдено. {scope}"
