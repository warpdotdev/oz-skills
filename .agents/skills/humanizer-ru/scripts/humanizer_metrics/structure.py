"""Структурные метрики уровня документа: burstiness абзацев и listicle-сигнатура.

Дополняет burstiness.py (там ритм ПРЕДЛОЖЕНИЙ) тем, что детекторы оценивают на
УРОВНЕ ДОКУМЕНТА: одинаковая длина абзацев и засилье однотипных списков выдают
шаблонную генерацию, даже когда каждое предложение по отдельности вычищено.

Эти сигналы целят в многосекционный/листикл-текст (посты, гайды). На прозе
одним блоком они инертны (мало абзацев, нет списков) и в score не вносят штраф,
поэтому не задевают калибровку основного корпуса.
"""

from __future__ import annotations

import re
import statistics
from dataclasses import dataclass

from razdel import sentenize

from .morphology import _morph

# Строка-пункт списка: маркер «- * •» или «1. / 1)» в начале строки.
_LIST_RE = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+\S")

# Заголовок: markdown-решётки либо короткая строка без конечной пунктуации,
# за которой идёт пустая строка или абзац.
_HEADING_RE = re.compile(r"^\s*(?:#{1,6}\s+)?(\S.{0,79})$")
_WORD_RE = re.compile(r"[А-Яа-яЁё][А-Яа-яЁё-]*")
# Имя собственное капитализируется законно: тег pymorphy3 или незнакомое
# словарю слово (Стэнфорд, Хогвартс). Считаем только заглавные у нарицательных.
_PROPER_TAGS = {"Name", "Surn", "Geox", "Orgn", "Patr"}
# Служебные слова в заголовках пишутся строчными и в английском Title Case,
# поэтому их регистр ничего не говорит.
_STOPWORDS = {"и", "в", "на", "с", "к", "по", "для", "из", "о", "об", "а", "но", "или", "у", "за"}


@dataclass
class StructureStats:
    paragraphs: int          # число непустых абзацев (разделитель — пустая строка)
    para_mean_sent: float    # средняя длина абзаца в предложениях
    para_cv: float           # коэффициент вариации длин абзацев (burstiness абзацев)
    list_items: int          # строк-пунктов списка
    listicle_share: float    # доля строк-пунктов среди непустых строк
    title_case_headings: int  # заголовки в английском Title Case (паттерн #56)
    truncated_ending: bool    # текст оборван на полуслове (паттерн #57)

    def as_dict(self) -> dict:
        return self.__dict__.copy()


def _is_common_noun_capitalized(word: str) -> bool:
    """Слово с заглавной, которое словарь знает как нарицательное: «Жизнь»,
    «Образование». Имена собственные и незнакомые словарю слова не в счёт."""
    if not word[:1].isupper():
        return False
    if word.lower() in _STOPWORDS:
        return False
    p = _morph().parse(word.lower())[0]
    if not p.is_known:
        return False
    return not (_PROPER_TAGS & set(p.tag.grammemes))


def count_title_case_headings(text: str) -> int:
    """Заголовки, где с заглавной стоит не только первое слово: «Ранняя Жизнь
    и Образование». В русском так не пишут, это калька с английского."""
    hits = 0
    lines = text.splitlines()
    for i, raw in enumerate(lines):
        s = raw.strip()
        if not s:
            continue
        is_md_heading = s.startswith("#")
        # Строка без конечной пунктуации, короткая, за ней пусто: тоже заголовок.
        looks_like_heading = (
            len(s) <= 80 and s[-1] not in ".!?:;,"
            and (i + 1 >= len(lines) or not lines[i + 1].strip())
            and not _LIST_RE.match(raw)
        )
        if not (is_md_heading or looks_like_heading):
            continue
        words = _WORD_RE.findall(s)
        if len(words) < 3:
            continue  # на двух словах отличить заголовок от имени нельзя
        if sum(1 for w in words[1:] if _is_common_noun_capitalized(w)) >= 2:
            hits += 1
    return hits


def is_truncated(text: str) -> bool:
    """Текст оборван на полуслове: модель упёрлась в лимит токенов, а человек
    скопировал как есть. Последняя содержательная строка прозы обязана
    заканчиваться знаком конца предложения."""
    lines = [ln.rstrip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return False
    last = lines[-1]
    if last.startswith("#") or _LIST_RE.match(last) or last.startswith(("|", ">", "```")):
        return False  # заголовок, пункт списка, таблица: пунктуация не нужна
    if len(_WORD_RE.findall(last)) < 4:
        return False  # подпись, дата, короткая пометка
    return last[-1] not in ".!?…:»)\"'*_"


def structure_stats(text: str) -> StructureStats:
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    sent_lens = [len(list(sentenize(p))) for p in paras]
    sent_lens = [n for n in sent_lens if n > 0]
    n = len(sent_lens)

    mean = statistics.mean(sent_lens) if sent_lens else 0.0
    stdev = statistics.pstdev(sent_lens) if n > 1 else 0.0
    cv = (stdev / mean) if mean else 0.0

    lines = [ln for ln in text.splitlines() if ln.strip()]
    list_items = sum(1 for ln in lines if _LIST_RE.match(ln))
    share = (list_items / len(lines)) if lines else 0.0

    return StructureStats(
        paragraphs=n,
        para_mean_sent=round(mean, 1),
        para_cv=round(cv, 3),
        list_items=list_items,
        listicle_share=round(share, 3),
        title_case_headings=count_title_case_headings(text),
        truncated_ending=is_truncated(text),
    )


# Пороги (эвристика, согласована с логикой burstiness.py для предложений).
# Срабатывают только на достаточно длинном/структурированном тексте, чтобы не
# штрафовать короткую прозу одним-двумя абзацами.
PARA_CV_AI = 0.35          # ниже = слишком ровные по длине абзацы
PARA_MIN_COUNT = 6         # по нескольким коротким абзацам cv ненадёжен (малая
                           # выборка), судим о ритме абзацев только на длинном тексте
LISTICLE_SHARE_AI = 0.30   # доля строк-пунктов выше — текст «листиклом»
LISTICLE_MIN_ITEMS = 6     # и не меньше стольких пунктов (порог шаблонности)


def structure_verdict(s: StructureStats) -> str:
    parts = []
    if s.paragraphs >= PARA_MIN_COUNT and s.para_cv < PARA_CV_AI:
        parts.append(f"⚠ ровные абзацы (CV={s.para_cv}, цель ≥{PARA_CV_AI})")
    else:
        parts.append(f"✓ абзацы: {s.paragraphs}, CV={s.para_cv}")
    if s.list_items >= LISTICLE_MIN_ITEMS and s.listicle_share > LISTICLE_SHARE_AI:
        parts.append(f"⚠ листикл ({s.list_items} пунктов, {int(s.listicle_share*100)}% строк)")
    elif s.list_items:
        parts.append(f"пунктов списка: {s.list_items}")
    if s.title_case_headings:
        parts.append(f"⚠ Title Case в заголовках: {s.title_case_headings} (#56)")
    if s.truncated_ending:
        parts.append("⚠ обрыв на полуслове (#57)")
    return "; ".join(parts)
