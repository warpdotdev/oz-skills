"""Границы чужого текста в Markdown: код, цитаты, короткие «ёлочки».

Сканер измеряет слова автора. Листинг кода, markdown-цитата через «>» и короткая
цитата в ёлочках это чужие слова, их баны и маркеры не в счёт. Два релиза
подряд границы чинились регулярками по одному примеру, и каждый раз соседний
вариант той же ошибки оставался (ограда внутри строки кода, закрытие оградой
длиннее открывающей, продолжение цитаты без «>»). Здесь один построчный разбор
состояния по правилам CommonMark и таблица тестов на варианты в
scripts/test_markers.py.

Две проекции одного текста:
- lexical: чужое заменено заглушкой GAP посимвольно, переводы строк на месте.
  Смещения и номера строк совпадают с исходником, фразовые регексы не
  склеивают слова через заглушку (она не буква).
- prose: чужое вырезано целиком. Для ритма, морфологии и структуры: заглушки
  ломали бы длину предложений и подсчёт абзацев.

Правила:
- Ограда кода: 3+ обратных кавычек или тильд с отступом до 3 пробелов в начале
  строки. Закрывает ограда того же символа НЕ КОРОЧЕ открывающей. Кавычки внутри
  строки кода оградой не являются. Незакрытая ограда не маскируется вовсе:
  для сканера ложное срабатывание дешевле спрятанного абзаца.
- Цитата: строка с «>» в начале (отступ до 3 пробелов). Ленивое продолжение:
  следующие непустые строки без «>» остаются цитатой, пока не встретится
  пустая строка, заголовок, пункт списка или ограда.
- Инлайн-код: серия обратных кавычек закрывается серией той же длины в
  пределах строки (`x`, ``a`b``).
- Короткая цитата в ёлочках (до QUOTE_MAX_WORDS слов) заглушается только в
  lexical: так цитируют слово или оборот. Длинная остаётся под сканером, это
  прямая речь или пересказ, её маркеры на совести автора. В prose ёлочки не
  трогаем, они внутри предложений автора.
"""

from __future__ import annotations

import re

GAP = "·"
QUOTE_MAX_WORDS = 12

_FENCE_OPEN = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
_FENCE_CLOSE = re.compile(r"^ {0,3}(`{3,}|~{3,})\s*$")
_QUOTE_LINE = re.compile(r"^ {0,3}>")
# Строки, которые прерывают ленивое продолжение цитаты (CommonMark 5.1):
# заголовок, пункт списка, горизонтальная линия, ограда.
_BLOCK_START = re.compile(r"^ {0,3}(?:#{1,6}\s|[-*+]\s|\d{1,9}[.)]\s|(?:-{3,}|\*{3,}|_{3,})\s*$|`{3,}|~{3,})")
_INLINE_CODE = re.compile(r"(`+)(?!`)([^`\n]+?)\1(?!`)")
_QUOTE_MARKS = re.compile(r"«[^«»]*»")


def _blank(s: str) -> str:
    return re.sub(r"[^\n]", GAP, s)


def _fence_ranges(lines: list[str]) -> list[tuple[int, int]]:
    """Пары (первая, последняя) строк закрытых блоков кода, включая ограды."""
    ranges: list[tuple[int, int]] = []
    i = 0
    while i < len(lines):
        m = _FENCE_OPEN.match(lines[i])
        # Инфо-строка ограды из кавычек не может содержать кавычки (CommonMark).
        if not m or (m.group(1)[0] == "`" and "`" in m.group(2)):
            i += 1
            continue
        ch, need = m.group(1)[0], len(m.group(1))
        j = i + 1
        while j < len(lines):
            c = _FENCE_CLOSE.match(lines[j])
            if c and c.group(1)[0] == ch and len(c.group(1)) >= need:
                break
            j += 1
        if j >= len(lines):
            i += 1  # незакрытая ограда: обычная строка
            continue
        ranges.append((i, j))
        i = j + 1
    return ranges


def _quote_lines(lines: list[str], in_code: set[int]) -> set[int]:
    quoted: set[int] = set()
    inside = False
    for i, line in enumerate(lines):
        if i in in_code:
            inside = False
            continue
        if _QUOTE_LINE.match(line):
            inside = True
            quoted.add(i)
        elif inside and line.strip() and not _BLOCK_START.match(line):
            quoted.add(i)  # ленивое продолжение абзаца цитаты
        else:
            inside = False
    return quoted


def _classify(text: str) -> tuple[list[str], set[int], set[int]]:
    lines = text.split("\n")
    in_code: set[int] = set()
    for a, b in _fence_ranges(lines):
        in_code.update(range(a, b + 1))
    return lines, in_code, _quote_lines(lines, in_code)


def _blank_short_quote(m: re.Match[str]) -> str:
    inner = m.group(0)[1:-1]
    return _blank(m.group(0)) if len(inner.split()) <= QUOTE_MAX_WORDS else m.group(0)


def mask_foreign(text: str) -> str:
    """lexical: код, цитаты и короткие ёлочки заглушены, смещения сохранены."""
    lines, in_code, quoted = _classify(text)
    out: list[str] = []
    for i, line in enumerate(lines):
        if i in in_code or i in quoted:
            out.append(_blank(line))
        else:
            out.append(_INLINE_CODE.sub(lambda m: _blank(m.group(0)), line))
    return _QUOTE_MARKS.sub(_blank_short_quote, "\n".join(out))


def strip_foreign(text: str) -> str:
    """prose: код и цитаты вырезаны, инлайн-код удалён, ёлочки на месте."""
    lines, in_code, quoted = _classify(text)
    kept = [_INLINE_CODE.sub("", line) for i, line in enumerate(lines)
            if i not in in_code and i not in quoted]
    return "\n".join(kept)
