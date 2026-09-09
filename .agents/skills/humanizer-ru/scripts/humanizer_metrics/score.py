"""Score чистоты: сворачивает детерминированные сигналы в одно число 0-100.

Выше = текст читается живее/человечнее. Это НЕ детектор и НЕ вероятность ИИ:
просто агрегат уже считаемых метрик (хард-баны, маркеры, ритм, морфология),
поданный как обратная связь «было/стало». Опирается на пороги, которые уже
откалиброваны в burstiness/morphology и задокументированы в eval/RESULTS.md.

Пороги штрафов подобраны на eval/corpus (human → высокий score, raw-AI →
низкий, humanized → между). Калибровочный прогон: см. eval/run_eval.py.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .burstiness import CV_HUMAN_TARGET
from .markers import (GENRE_MUTED_BANS, GENRE_MUTED_CATEGORIES,
                      effective_hard_bans, mute_by_genre)
from .morphology import NV_TARGET
from .structure import (
    LISTICLE_MIN_ITEMS,
    LISTICLE_SHARE_AI,
    PARA_CV_AI,
    PARA_MIN_COUNT,
)

# Тире — отдельный случай: оно и хард-бан, и штатная русская пунктуация
# (Википедия, диапазоны, «это —»). Поэтому в score не рубим потолком, а
# штрафуем по плотности с допуском. Имя берём из HARD_BANS markers.py.
EM_DASH_NAME = "Длинное тире"
COPY_PASTE_CATEGORY = "Артефакты копипасты"

# Полосы. Совпадают с порогами вмешательства из SKILL.md.
BAND_CLEAN = 85   # ≥ — следы ИИ не мешают, не править
BAND_EDIT = 60    # ≥ — точечная правка; < — полный рерайт

# Доля ЛЮДЕЙ, у которых текст такой длины совсем без банов и без маркеров.
# Измерено на 14 973 человеческих текстах (Пикабу, M4, AINL), см. eval/.
#
# Зачем это здесь. Score мерит расстояние до нуля, а не до человека, и молча
# внушает, что цель это сто из ста. Человек нулём почти не бывает: на тексте в
# три сотни слов идеально чистых людей 15%, а не 100%. То есть высшая оценка
# означает попадание в редкий хвост распределения. Один такой текст неотличим;
# корпус из тысячи таких текстов отличим тривиально, потому что у людей хвост
# есть, а у вычищенного корпуса его нет.
#
# Штрафовать за чистоту мы не будем: это сломало бы сравнение «было и стало».
# Вместо этого при нулевом счёте отдаём заметку, чтобы цель читалась как
# «попади в типичную частоту», а не как «вычисти всё».
HUMAN_ZERO_SHARE: tuple[tuple[int, float], ...] = ((100, 42.2), (200, 21.0), (400, 15.1))
STERILE_MIN_WORDS = 100


@dataclass
class ScoreResult:
    score: int                       # 0-100, выше = чище
    band: str                        # "чисто" | "правка" | "рерайт"
    penalties: list[tuple[str, int]]  # (причина, -очки) — это и есть verbose-отчёт
    notes: list[str] = field(default_factory=list)  # замечания без штрафа

    def as_dict(self) -> dict:
        return {
            "score": self.score,
            "band": self.band,
            "penalties": [{"reason": r, "points": p} for r, p in self.penalties],
            "notes": list(self.notes),
        }


def _band(score: float) -> str:
    if score >= BAND_CLEAN:
        return "чисто"
    if score >= BAND_EDIT:
        return "правка"
    return "рерайт"


def _per100(count: int, words: int) -> float:
    return (count / words * 100) if words else 0.0


def cleanliness_score(report, genre: str | None = None) -> ScoreResult:
    """Считает score 0-100 из готового Report (см. humanizer_metrics.analyze).

    genre снимает штрафы за маркеры, законные для регистра (научный,
    юридический, художественный). Без genre режим строгий, как раньше.
    """
    words = report.rhythm.words or 1
    markers = mute_by_genre(report.markers, genre, GENRE_MUTED_CATEGORIES)
    dash_muted = EM_DASH_NAME in GENRE_MUTED_BANS.get(genre or "", set())
    penalties: list[tuple[str, int]] = []
    notes: list[str] = []
    score = 100.0

    # 1. Фразовые хард-баны (кроме тире). Однозначные AI-обороты: дорого.
    #    Частотные баны («Является») штрафуются только выше порога плотности.
    eff_bans = mute_by_genre(
        effective_hard_bans(report.hard_bans, report.rhythm.words),
        genre, GENRE_MUTED_BANS)
    hard_phrase = sum(h.count for h in eff_bans if h.marker != EM_DASH_NAME)
    if hard_phrase:
        pen = min(45, 12 * hard_phrase)
        score -= pen
        penalties.append((f"хард-баны (фразы): {hard_phrase}", -pen))

    # 2. Артефакты копипасты из чат-бота: текст буквально вставлен из ответа ИИ.
    copy_paste = sum(h.count for h in markers if h.category == COPY_PASTE_CATEGORY)
    if copy_paste:
        pen = 60
        score -= pen
        penalties.append((f"артефакты копипасты: {copy_paste}", -pen))

    # 3. Мягкие маркеры (кроме копипасты) по плотности на 100 слов.
    soft = sum(h.count for h in markers if h.category != COPY_PASTE_CATEGORY)
    if soft:
        pen = min(30, round(2 * _per100(soft, words)))
        if pen:
            score -= pen
            penalties.append((f"маркеры: {soft} ({_per100(soft, words):.1f}/100 слов)", -pen))

    # 4. Длинное тире по плотности с допуском ~2 на 100 слов: «—» штатно
    #    используется в русском (Википедия, «это —», диапазоны). Штраф мягкий,
    #    потому что на изданной прозе оно частая норма; сам бан держится на
    #    парном замере (markers.py, комментарий про парный замер).
    dash_density = 0.0 if dash_muted else _per100(report.rhythm.em_dash, words)
    if dash_density > 2.0:
        pen = min(8, round(3 * (dash_density - 2.0)))
        if pen:
            score -= pen
            penalties.append((f"тире: {report.rhythm.em_dash} ({dash_density:.1f}/100 слов)", -pen))

    # 5. Ровный ритм: чем ниже CV относительно цели 0.45, тем больше штраф.
    cv = report.rhythm.cv_len
    if report.rhythm.sentences >= 4 and cv < CV_HUMAN_TARGET:
        pen = min(20, round((CV_HUMAN_TARGET - cv) / CV_HUMAN_TARGET * 30))
        if pen:
            score -= pen
            penalties.append((f"ровный ритм (CV={cv}, цель ≥{CV_HUMAN_TARGET})", -pen))

    # 6. Номинальность: сущ./глаг. выше цели 2.5 = канцелярит. Слабый сигнал и
    #    главный источник ложных срабатываний (энциклопедический/юр. регистр
    #    легитимно номинален), поэтому штраф мягкий и низко ограничен.
    nv = report.morph.noun_verb_ratio
    if nv > NV_TARGET:
        pen = min(8, round((nv - NV_TARGET) / 0.5 * 3))
        if pen:
            score -= pen
            penalties.append((f"номинальность (сущ./глаг.={nv}, цель ≤{NV_TARGET})", -pen))

    # 7. Document-level: ровные по длине абзацы (burstiness абзацев). Срабатывает
    #    только на достаточно многоабзацном тексте, иначе инертно (короткая проза).
    st = report.structure
    if st.paragraphs >= PARA_MIN_COUNT and st.para_cv < PARA_CV_AI:
        pen = min(10, round((PARA_CV_AI - st.para_cv) / PARA_CV_AI * 20))
        if pen:
            score -= pen
            penalties.append((f"ровные абзацы (CV={st.para_cv}, цель ≥{PARA_CV_AI})", -pen))

    # 8. Document-level: listicle-сигнатура (засилье однотипных пунктов). Инертно
    #    на прозе без списков, бьёт по шаблонным гайдам/постам.
    if st.list_items >= LISTICLE_MIN_ITEMS and st.listicle_share > LISTICLE_SHARE_AI:
        pen = min(12, round((st.listicle_share - LISTICLE_SHARE_AI) * 30))
        if pen:
            score -= pen
            penalties.append((f"листикл ({st.list_items} пунктов, {int(st.listicle_share*100)}% строк)", -pen))

    # Заметка о стерильности. Не штраф: цель показать, что ноль это не середина
    # человеческого распределения, а его редкий край.
    #
    # Условие ровно то, что измерялось: ноль банов и ноль маркеров. Ритм,
    # номинальность и структура сюда не входят, иначе текст с минусом за ровный
    # ритм терял бы заметку, хотя по лексике он как раз стерилен.
    if not (hard_phrase or copy_paste or soft) and words >= STERILE_MIN_WORDS:
        share = next((s for limit, s in HUMAN_ZERO_SHARE if words < limit),
                     HUMAN_ZERO_SHARE[-1][1])
        notes.append(
            f"стерильно: ни одного маркера. Так пишет {share:.0f}% людей на тексте "
            f"в {words} слов, остальные {100 - share:.0f}% что-нибудь да используют. "
            "Цель не ноль, а типичная для жанра частота: вычищать дальше незачем")

    final = max(0, min(100, round(score)))
    return ScoreResult(score=final, band=_band(final), penalties=penalties, notes=notes)
