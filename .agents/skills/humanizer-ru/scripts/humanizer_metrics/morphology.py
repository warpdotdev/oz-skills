"""Морфология: соотношение существительных к глаголам через pymorphy3.

Закрывает пункт чеклиста «соотношение существительных к глаголам ≤ 2.5:1» —
тот, который LLM не умеет считать на глаз. У AI-русского ~3:1, у людей ~2:1
(SKILL.md, паттерн #14, Biber framework). Чем выше отношение, тем «номинальнее»
текст, тем сильнее канцелярит.
"""

from __future__ import annotations

import functools
from dataclasses import dataclass

import pymorphy3
from razdel import tokenize


@functools.lru_cache(maxsize=1)
def _morph() -> "pymorphy3.MorphAnalyzer":
    return pymorphy3.MorphAnalyzer()


@dataclass
class MorphStats:
    nouns: int
    verbs: int           # глаголы + инфинитивы + деепричастия + причастия как глагольные формы
    noun_verb_ratio: float
    nominalizations: int  # отглагольные существительные (потенциальный канцелярит)
    tokens: int

    def as_dict(self) -> dict:
        return self.__dict__.copy()


# Что считаем «глагольным» — pymorphy3 теги (OpenCorpora):
_VERBAL = {"VERB", "INFN", "GRND", "PRTF", "PRTS"}
_NOUN = {"NOUN"}
_NOMINAL_SUFFIXES = ("ение", "ание", "ания", "ения", "ация", "изация", "ировка", "ость", "остей")


def _is_cyrillic_word(tok: str) -> bool:
    return any("а" <= c.lower() <= "я" or c.lower() == "ё" for c in tok)


def morph_stats(text: str) -> MorphStats:
    m = _morph()
    nouns = verbs = nominal = total = 0
    for t in tokenize(text):
        w = t.text
        if not _is_cyrillic_word(w):
            continue
        total += 1
        p = m.parse(w)[0]
        pos = p.tag.POS
        if pos in _NOUN:
            nouns += 1
            lemma = p.normal_form
            if lemma.endswith(_NOMINAL_SUFFIXES):
                nominal += 1
        elif pos in _VERBAL:
            verbs += 1
    ratio = (nouns / verbs) if verbs else float(nouns)
    return MorphStats(
        nouns=nouns,
        verbs=verbs,
        noun_verb_ratio=round(ratio, 2),
        nominalizations=nominal,
        tokens=total,
    )


NV_TARGET = 2.5  # из чеклиста SKILL.md


def morph_verdict(s: MorphStats) -> str:
    if s.noun_verb_ratio <= NV_TARGET:
        return f"✓ сущ./глаг. = {s.noun_verb_ratio} (цель ≤{NV_TARGET})"
    return f"⚠ сущ./глаг. = {s.noun_verb_ratio} (цель ≤{NV_TARGET}, канцелярит); номинализаций: {s.nominalizations}"
