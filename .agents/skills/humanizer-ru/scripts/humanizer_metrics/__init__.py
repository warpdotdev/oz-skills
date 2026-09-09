"""humanizer_metrics — детерминированные метрики живости текста.

Это грепабельная половина режима «Аудит» из SKILL.md: то, что считается
машиной, а не LLM. Используется и как локальный буст для Claude Code, и как
движок eval-харнеса (eval/run_eval.py), и как self-test самого скилла
(scripts/lint_skill.py).

Семантику (кальки, ирония, translationese, голос) тут не ловим — для этого
нужен сам скилл. Скрипты не работают в claude.ai web; скилл от них не зависит.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from .burstiness import RhythmStats, rhythm, rhythm_verdict
from .markers import (
    MarkerHit,
    marker_verdict,
    scan_hard_bans,
    scan_markers,
)
from .morphology import MorphStats, morph_stats, morph_verdict
from .structure import StructureStats, structure_stats, structure_verdict
from .score import ScoreResult, cleanliness_score

__all__ = [
    "Report",
    "analyze",
    "RhythmStats",
    "MorphStats",
    "StructureStats",
    "MarkerHit",
    "ScoreResult",
    "cleanliness_score",
    "rhythm",
    "morph_stats",
    "structure_stats",
    "scan_hard_bans",
    "scan_markers",
    "mask_foreign",
    "strip_foreign",
    "GAP",
    "QUOTE_MAX_WORDS",
]


@dataclass
class Report:
    hard_bans: list[MarkerHit]
    markers: list[MarkerHit]
    rhythm: RhythmStats
    morph: MorphStats
    structure: StructureStats

    @property
    def hard_ban_count(self) -> int:
        return sum(h.count for h in self.hard_bans)

    @property
    def marker_count(self) -> int:
        return sum(h.count for h in self.markers)

    def as_dict(self) -> dict:
        return {
            "hard_ban_count": self.hard_ban_count,
            "hard_bans": [(h.marker, h.count) for h in self.hard_bans],
            "marker_count": self.marker_count,
            "markers": [(h.category, h.marker, h.count) for h in self.markers],
            "rhythm": self.rhythm.as_dict(),
            "morph": self.morph.as_dict(),
            "structure": self.structure.as_dict(),
        }


# --- Код и цитаты не текст автора ------------------------------------------
# Разбор границ Markdown живёт в markdown.py (один построчный проход по
# CommonMark и таблица тестов), здесь только две проекции текста.
from .markdown import GAP, QUOTE_MAX_WORDS, mask_foreign, strip_foreign  # noqa: E402
from .facts import Facts, FactsDiff, diff_facts, extract_facts, facts_verdict  # noqa: E402

mask_code_and_quotes = mask_foreign
strip_code = strip_foreign


def analyze(text: str) -> Report:
    """Полный детерминированный прогон текста."""
    lexical = mask_code_and_quotes(text)
    prose = strip_code(text)
    stats = rhythm(prose)
    # Тире внутри короткой цитаты («Война — и мир») не типографика автора:
    # считаем его по заглушенному тексту, ритм по прозе с цитатами.
    stats = replace(stats, em_dash=lexical.count("—"))
    return Report(
        hard_bans=scan_hard_bans(lexical),
        markers=scan_markers(lexical),
        rhythm=stats,
        morph=morph_stats(prose),
        structure=structure_stats(prose),
    )
