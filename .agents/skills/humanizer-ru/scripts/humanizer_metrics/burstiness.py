"""Ритм и типографика: то, что скилл велит измерять дисперсией, а не на глаз.

Закрывает пункты чеклиста «вариативность длины предложений — не средняя, а
ДИСПЕРСИЯ» и «ноль длинных тире». Burstiness тут — статистический прокси, не сам
детектор: высокий разброс длины предложений коррелирует с человеческим письмом
(SKILL.md, раздел «Что ловят детекторы»).
"""

from __future__ import annotations

import re
import statistics
from dataclasses import dataclass

from razdel import sentenize, tokenize


@dataclass
class RhythmStats:
    sentences: int
    words: int
    mean_len: float          # средняя длина предложения в словах
    stdev_len: float         # стандартное отклонение длины
    cv_len: float            # коэффициент вариации = stdev/mean (главный показатель)
    min_len: int
    max_len: int
    short_share: float       # доля предложений < 5 слов
    long_share: float        # доля предложений > 25 слов
    em_dash: int             # длинных тире «—»
    ellipsis: int            # многоточий
    parentheses: int         # скобочных ремарок
    questions: int           # вопросительных предложений
    staccato_runs: int = 0   # цепочек из 3+ обрывков подряд (каталог #49)
    staccato_max: int = 0    # длина самой длинной такой цепочки

    def as_dict(self) -> dict:
        return self.__dict__.copy()


_WORD_RE = re.compile(r"[А-Яа-яЁёA-Za-z0-9]")


def _word_count(sentence: str) -> int:
    return sum(1 for t in tokenize(sentence) if _WORD_RE.search(t.text))


# Рваная медитативность (каталог #49): «Короткие. Точные. Отдельные.» Цепочка
# из трёх и более утверждений по 1-3 слова подряд. Не считаются реплики диалога
# (строка с тире или кавычки в начале), восклицания, вопросы, подводки с
# двоеточием, пункты списков и заголовки: там обрывки законны. Порог выбран по
# 400 постам Пикабу: доля обрывков в тексте срабатывала на 5-12% живых текстов
# и отвергнута, цепочка из трёх подряд даёт 4 из 400 (eval/OVERCORRECTION_CHECK.md).
STACCATO_MAX_WORDS = 3
STACCATO_MIN_RUN = 3
_DIALOG_RE = re.compile(r"^\s*[-–—«\"']")
_SKIP_LINE_RE = re.compile(r"^\s*(?:(?:[-*•]|\d+[.)])\s+|#)")


def staccato_runs(text: str) -> tuple[int, int]:
    """(число цепочек, длина самой длинной). Цепочка не переходит через строку."""
    runs: list[int] = []
    for line in text.replace("\\", "").split("\n"):
        if not line.strip() or _SKIP_LINE_RE.match(line):
            continue
        cur = 0
        for s in sentenize(line):
            st = s.text.strip()
            n = _word_count(st)
            if not n:
                continue
            if n <= STACCATO_MAX_WORDS and not _DIALOG_RE.match(st) and st[-1] not in "?!:;":
                cur += 1
            else:
                if cur >= STACCATO_MIN_RUN:
                    runs.append(cur)
                cur = 0
        if cur >= STACCATO_MIN_RUN:
            runs.append(cur)
    return len(runs), max(runs, default=0)


def rhythm(text: str) -> RhythmStats:
    sents = [s.text for s in sentenize(text)]
    lengths = [_word_count(s) for s in sents]
    lengths = [n for n in lengths if n > 0]
    n = len(lengths)
    total_words = sum(lengths)

    runs, longest = staccato_runs(text)
    mean = statistics.mean(lengths) if lengths else 0.0
    stdev = statistics.pstdev(lengths) if n > 1 else 0.0
    cv = (stdev / mean) if mean else 0.0

    return RhythmStats(
        sentences=n,
        words=total_words,
        mean_len=round(mean, 1),
        stdev_len=round(stdev, 1),
        cv_len=round(cv, 3),
        min_len=min(lengths) if lengths else 0,
        max_len=max(lengths) if lengths else 0,
        short_share=round(sum(1 for x in lengths if x < 5) / n, 3) if n else 0.0,
        long_share=round(sum(1 for x in lengths if x > 25) / n, 3) if n else 0.0,
        em_dash=text.count("—"),
        ellipsis=text.count("…") + len(re.findall(r"\.\.\.", text)),
        parentheses=text.count("("),
        questions=sum(1 for s in sents if s.rstrip().endswith("?")),
        staccato_runs=runs,
        staccato_max=longest,
    )


# Эвристические пороги (откалиброваны под русский грубо, см. eval/RESULTS.md).
# cv_len < 0.35: слишком ровный ритм, признак AI. Один порог на вердикт и на
# штраф в score.py: раньше вердикт ставил ✓ с 0.35, а штраф шёл до 0.45, и
# текст получал «ритм рваный» вместе с минусом за ровный ритм.
CV_HUMAN_TARGET = 0.35


def rhythm_verdict(s: RhythmStats, dash_ok: bool = False) -> str:
    """dash_ok=True для жанров, где длинное тире законно (научный,
    юридический, художественный): тогда оно показывается фактом, не ⚠."""
    if s.em_dash > 0 and dash_ok:
        dash = f"тире: {s.em_dash} (законно для жанра)"
    elif s.em_dash > 0:
        dash = f"⚠ {s.em_dash} длинных тире (норма 0)"
    else:
        dash = "✓ тире чисто"
    if s.cv_len < CV_HUMAN_TARGET:
        rhythm_v = f"⚠ ровный ритм (CV={s.cv_len}, цель ≥{CV_HUMAN_TARGET})"
    else:
        rhythm_v = f"✓ ритм рваный (CV={s.cv_len})"
    return f"{rhythm_v}; {dash}"
