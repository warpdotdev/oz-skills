"""humanizer_metrics — детерминированные метрики живости текста.

Это грепабельная половина режима «Аудит» из SKILL.md: то, что считается
машиной, а не LLM. Используется и как локальный буст для Claude Code, и как
движок eval-харнеса (eval/run_eval.py), и как self-test самого скилла
(scripts/lint_skill.py).

Семантику (кальки, ирония, translationese, голос) тут не ловим — для этого
нужен сам скилл. Скрипты не работают в claude.ai web; скилл от них не зависит.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace

from .burstiness import RhythmStats, rhythm, rhythm_verdict
from .lexical import LexicalStats, lexical_stats
from .markers import (
    GENRE_MUTED_BANS,
    GENRE_MUTED_CATEGORIES,
    GENRES,
    MarkerHit,
    effective_hard_bans,
    marker_verdict,
    mute_by_genre,
    scan_hard_bans,
    scan_markers,
)
from .morphology import MorphStats, morph_stats, morph_verdict
from .repeats import RepeatStats, repeat_stats
from .structure import StructureStats, structure_stats, structure_verdict
from .score import ScoreResult, cleanliness_score

__all__ = [
    "Report",
    "analyze",
    "ScanReport",
    "scan_report",
    "cyrillic_share",
    "RhythmStats",
    "MorphStats",
    "StructureStats",
    "LexicalStats",
    "RepeatStats",
    "MarkerHit",
    "ScoreResult",
    "cleanliness_score",
    "rhythm",
    "morph_stats",
    "structure_stats",
    "lexical_stats",
    "repeat_stats",
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
    lexical: LexicalStats
    repeats: RepeatStats

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
            "lexical": self.lexical.as_dict(),
            "repeats": self.repeats.as_dict(),
        }


# --- Код и цитаты не текст автора ------------------------------------------
# Разбор границ Markdown живёт в markdown.py (один построчный проход по
# CommonMark и таблица тестов), здесь только две проекции текста.
from .markdown import GAP, QUOTE_MAX_WORDS, mask_foreign, strip_foreign  # noqa: E402
from .facts import Facts, FactsDiff, diff_facts, extract_facts, facts_verdict  # noqa: E402


def analyze(text: str) -> Report:
    """Полный детерминированный прогон текста."""
    lexical = mask_foreign(text)
    prose = strip_foreign(text)
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
        lexical=lexical_stats(prose),
        repeats=repeat_stats(prose),
    )


# --- Один конвейер для CLI, MCP и гейта CI --------------------------------
# scan.py (текст и --json), mcp_server.py и scan_gate.py считают отчёт здесь:
# балл по жанру, частотные баны, жанровый фильтр, доля кириллицы. Раньше каждый
# считал сам, и они разошлись (JSON без позиций, MCP без предупреждения о языке).
NON_RUSSIAN_SHARE = 0.3
NON_RUSSIAN_WARNING = "текст не похож на русский, метрики не применимы"


def cyrillic_share(text: str) -> float:
    """Доля кириллицы среди букв прозы: ниже NON_RUSSIAN_SHARE текст не русский.
    Код и цитаты в счёт не идут (strip_foreign): русский гайд с большим блоком
    Python иначе выглядел бы английским и выпадал из проверки."""
    letters = re.findall(r"[^\W\d_]", strip_foreign(text))
    if not letters:
        return 0.0
    cyr = sum(1 for ch in letters if "а" <= ch.lower() <= "я" or ch.lower() == "ё")
    return cyr / len(letters)


def _hits(hits: list[MarkerHit]) -> list[dict]:
    return [{"category": h.category, "name": h.marker, "count": h.count,
             "positions": list(h.positions)} for h in hits]


@dataclass
class ScanReport:
    report: Report
    genre: str
    score: ScoreResult
    hard_bans: list[MarkerHit]   # после частотных порогов и жанрового фильтра
    markers: list[MarkerHit]     # после жанрового фильтра
    muted_bans: int
    muted_markers: int
    cyrillic: float

    @property
    def non_russian(self) -> bool:
        return self.cyrillic < NON_RUSSIAN_SHARE

    @property
    def hard_ban_count(self) -> int:
        return sum(h.count for h in self.hard_bans)

    @property
    def marker_count(self) -> int:
        return sum(h.count for h in self.markers)

    def as_dict(self) -> dict:
        rep = self.report
        out = {
            "score": self.score.score,
            "band": self.score.band,
            "penalties": [{"reason": r, "points": p} for r, p in self.score.penalties],
            "notes": list(self.score.notes),
            "genre": self.genre,
            "words": rep.rhythm.words,
            "hard_bans": _hits(self.hard_bans),
            "hard_ban_count": self.hard_ban_count,
            "markers": _hits(self.markers),
            "marker_count": self.marker_count,
            "muted_by_genre": {"hard_bans": self.muted_bans, "markers": self.muted_markers},
            "rhythm": rep.rhythm.as_dict(),
            "morph": rep.morph.as_dict(),
            "structure": rep.structure.as_dict(),
            "lexical": rep.lexical.as_dict(),
            "repeats": rep.repeats.as_dict(),
        }
        if self.non_russian:
            out["warning"] = NON_RUSSIAN_WARNING
        return out


def scan_report(text: str, genre: str | None = None) -> ScanReport:
    """Полный отчёт сканера по жанру. Без жанра строгий режим marketing."""
    genre = genre or "marketing"
    if genre not in GENRES:
        raise ValueError(f"неизвестный жанр {genre!r}, допустимы: {', '.join(GENRES)}")
    rep = analyze(text)
    # Частотные баны («Является» до порога 1/500 слов) не валят exit и не
    # показываются как ⛔: они остаются в мягких маркерах.
    freq = effective_hard_bans(rep.hard_bans, rep.rhythm.words)
    # Жанровый фильтр: в научном, юридическом, художественном и новостном
    # регистре часть банов законна (см. markers.GENRE_MUTED_BANS).
    bans = mute_by_genre(freq, genre, GENRE_MUTED_BANS)
    soft = mute_by_genre(rep.markers, genre, GENRE_MUTED_CATEGORIES)
    return ScanReport(report=rep, genre=genre, score=cleanliness_score(rep, genre),
                      hard_bans=bans, markers=soft,
                      muted_bans=len(freq) - len(bans), muted_markers=len(rep.markers) - len(soft),
                      cyrillic=cyrillic_share(text))
