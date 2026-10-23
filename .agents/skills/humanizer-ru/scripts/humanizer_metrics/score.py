"""Score чистоты: сворачивает детерминированные сигналы в одно число 0-100.

Выше = текст читается живее/человечнее. Это НЕ детектор и НЕ вероятность ИИ:
просто агрегат уже считаемых метрик (хард-баны, маркеры, ритм, морфология),
поданный как обратная связь «было/стало». Опирается на пороги, которые уже
откалиброваны в burstiness/morphology и задокументированы в eval/RESULTS.md.

Пороги штрафов подобраны на eval/corpus (human → высокий score, raw-AI →
низкий, humanized → между). Калибровочный прогон: см. eval/run_eval.py.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .burstiness import CV_HUMAN_TARGET, STACCATO_MIN_RUN
from .lexical import LEX_MIN_TOKENS
from .markers import (GENRE_MUTED_BANS, GENRE_MUTED_CATEGORIES,
                      effective_hard_bans, mute_by_genre)
from .morphology import NV_TARGET
from .repeats import REPEAT_MIN_PHRASES
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

# Почерк свежих моделей и обвязка чата (markers.py, eval/MODERN-SLOP.md).
# Считаются числом РАЗНЫХ оборотов, а не плотностью: плотность размывается на
# длинном тексте, а у современной модели два-три таких оборота на пост. Один
# оборот бывает и у человека (до 3%), поэтому первый стоит 3 балла, каждый
# следующий 10. Веса подобраны на половине корпуса и проверены на второй:
# пойманного слопа 53% → 67%, ложных тревог на людях +1 п.п.
SIGNATURE_CATEGORY = "Почерк модели"
SIGNATURE_FIRST = 3
SIGNATURE_NEXT = 10
SIGNATURE_MAX = 24
CHAT_WRAP_CATEGORY = "Обвязка чата"
CHAT_WRAP_EACH = 10
CHAT_WRAP_MAX = 20
DISTINCT_CATEGORIES = (SIGNATURE_CATEGORY, CHAT_WRAP_CATEGORY)

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

# Рваная медитативность (каталог #49): цепочка обрывков «Короткие. Точные.
# Отдельные.» это почерк хуманайзера, который вывернул ровный ритм наизнанку:
# обратная сторона штрафа за ровный ритм. Штраф мягкий, как
# у номинальности: на 400 постах Пикабу правило срабатывает на 4, и половина из
# них настоящие авторские обрывки.
STACCATO_PENALTY = 8
STACCATO_PENALTY_MAX = 14
# Лексическое разнообразие (lexical.py): слова почти не повторяются, модель
# подбирает синоним там, где человек сказал бы то же слово или «он». MATTR у
# людей 0.902 ± 0.037, порог 0.955 это +1.4 σ. Балл за каждую тысячную выше
# порога, потолок 15: ниже, чем у почерка модели, потому что признак
# статистический и на одном тексте шумит. Подобрано на половине корпуса и
# проверено на второй (eval/MODERN-SLOP.md): ловит GigaChat-Max и o3, а GPT-5.6
# не сдвигает, его тексты лежат внутри человеческого разброса.
#
# В новостях, научном и юридическом регистре штраф снят: плотный фактический
# текст разнообразен законно. На людях LLMTrace он срабатывал чаще всего на
# новостях (2,8% текстов против 0,6-0,9% у статей и отзывов), а на справочных
# текстах задевал людей почти так же часто, как машины, и ни одну машину не
# перевёл из «чисто». В художественном жанре оставлен: на рассказах LLMTrace
# машины срабатывают впятеро чаще людей.
LEX_THRESHOLD = 0.955
LEX_SLOPE = 1000
LEX_PENALTY_MAX = 15
LEX_MUTED_GENRES = frozenset({"news", "academic", "legal"})
# Повтор фразы между абзацами (repeats.py): заметка без штрафа. Даже бесконечный
# штраф вывел бы из «чисто» 0,8-2,8% текстов одной Llama-3.3, у людей потери
# того же порядка (eval/MODERN-SLOP.md). Показываем не больше REPEAT_SHOW фраз.
REPEAT_SHOW = 3
# Плотность мягких маркеров на коротком тексте считается так, будто слов не
# меньше DENSITY_MIN_WORDS: один оборот в реплике из семи слов это не 14 на
# сотню, а повод посмотреть. Иначе бытовое сообщение уходило в «правку».
DENSITY_MIN_WORDS = 50
# Потолок штрафа за номинальность. Именованный, потому что браузерный сканер
# морфологии не имеет и объявляет ровно эту величину как неизмеренную.
NV_PENALTY_MAX = 8


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


def _plural(n: int, one: str, few: str, many: str) -> str:
    if n % 10 == 1 and n % 100 != 11:
        return one
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return few
    return many


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
    soft = sum(h.count for h in markers
               if h.category != COPY_PASTE_CATEGORY and h.category not in DISTINCT_CATEGORIES)
    if soft:
        pen = min(30, round(2 * _per100(soft, max(words, DENSITY_MIN_WORDS))))
        if pen:
            score -= pen
            penalties.append((f"маркеры: {soft} ({_per100(soft, words):.1f}/100 слов)", -pen))

    # 3б. Почерк модели и обвязка чата: по числу разных оборотов (см. константы).
    sig = len({h.marker for h in markers if h.category == SIGNATURE_CATEGORY})
    if sig:
        pen = min(SIGNATURE_MAX, SIGNATURE_FIRST + SIGNATURE_NEXT * (sig - 1))
        score -= pen
        penalties.append((f"почерк модели: {sig} {_plural(sig, 'оборот', 'оборота', 'оборотов')}", -pen))
    wrap = len({h.marker for h in markers if h.category == CHAT_WRAP_CATEGORY})
    if wrap:
        pen = min(CHAT_WRAP_MAX, CHAT_WRAP_EACH * wrap)
        score -= pen
        penalties.append((f"обвязка чата: {wrap} {_plural(wrap, 'след', 'следа', 'следов')}", -pen))

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

    # 5. Ровный ритм: чем ниже CV относительно порога 0.35, тем больше штраф.
    #    Порог тот же, что у вердикта rhythm_verdict: ⚠ и штраф всегда вместе.
    cv = report.rhythm.cv_len
    if report.rhythm.sentences >= 4 and cv < CV_HUMAN_TARGET:
        pen = min(20, round((CV_HUMAN_TARGET - cv) / CV_HUMAN_TARGET * 30))
        if pen:
            score -= pen
            penalties.append((f"ровный ритм (CV={cv}, цель ≥{CV_HUMAN_TARGET})", -pen))

    # 5б. Рваная медитативность: цепочки обрывков подряд. Обратная сторона
    #     ровного ритма, поэтому стоит рядом с ним.
    runs = report.rhythm.staccato_runs
    if runs:
        pen = min(STACCATO_PENALTY_MAX, STACCATO_PENALTY * runs)
        score -= pen
        penalties.append((
            f"рваная медитативность: {runs} {_plural(runs, 'цепочка', 'цепочки', 'цепочек')} "
            f"обрывков по {STACCATO_MIN_RUN}+ подряд (самая длинная {report.rhythm.staccato_max})", -pen))

    # 5в. Лексическое разнообразие: считается только на тексте от LEX_MIN_TOKENS
    #     словоформ, на коротком MATTR шумит. floor, а не round: браузер обязан
    #     получить то же целое, а округление половин в JS и Python разное.
    lex = report.lexical
    if (genre not in LEX_MUTED_GENRES and lex.tokens >= LEX_MIN_TOKENS
            and lex.mattr > LEX_THRESHOLD):
        pen = min(LEX_PENALTY_MAX, math.floor((lex.mattr - LEX_THRESHOLD) * LEX_SLOPE))
        if pen:
            score -= pen
            penalties.append((f"лексическое разнообразие (MATTR={lex.mattr:.3f}, "
                              f"порог {LEX_THRESHOLD})", -pen))

    # 6. Номинальность: сущ./глаг. выше цели 2.5 = канцелярит. Слабый сигнал и
    #    главный источник ложных срабатываний (энциклопедический/юр. регистр
    #    легитимно номинален), поэтому штраф мягкий и низко ограничен.
    nv = report.morph.noun_verb_ratio
    if nv > NV_TARGET:
        pen = min(NV_PENALTY_MAX, round((nv - NV_TARGET) / 0.5 * 3))
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
    if not (hard_phrase or copy_paste or soft or sig or wrap) and words >= STERILE_MIN_WORDS:
        share = next((s for limit, s in HUMAN_ZERO_SHARE if words < limit),
                     HUMAN_ZERO_SHARE[-1][1])
        notes.append(
            f"стерильно: ни одного маркера. Так пишет {share:.0f}% людей на тексте "
            f"в {words} слов, остальные {100 - share:.0f}% что-нибудь да используют. "
            "Цель не ноль, а типичная для жанра частота: вычищать дальше незачем")

    # Заметка о повторе фраз между абзацами. Почему не штраф: комментарий у REPEAT_SHOW.
    phrases = report.repeats.phrases
    if len(phrases) >= REPEAT_MIN_PHRASES:
        shown = ", ".join(f"«{p}»" for p in phrases[:REPEAT_SHOW])
        more = f" и ещё {len(phrases) - REPEAT_SHOW}" if len(phrases) > REPEAT_SHOW else ""
        notes.append(
            f"повтор фраз между абзацами: {shown}{more}. В счёт не входит: у людей так "
            "бывает в новостях и справках. Если повтор не нарочный, оставьте фразу в одном месте")

    final = max(0, min(100, round(score)))
    return ScoreResult(score=final, band=_band(final), penalties=penalties, notes=notes)
