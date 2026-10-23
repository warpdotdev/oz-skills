"""Лексическое разнообразие: MATTR по словоформам на начале текста.

Свежие модели пишут лексически чище людей: слов из словаря сканера у них нет,
зато слова почти не повторяются. Человек в посте возвращается к «я», «он»,
«это», «было», к одному и тому же существительному, модель подбирает синоним.
Замер на LLMTrace и Пикабу (eval/MODERN-SLOP.md, раздел про разнообразие):
MATTR у людей 0.900 ± 0.042, у GPT-5.6 на 0.7 σ выше, у o3 и GigaChat-Max
больше чем на 1 σ.

Почему словоформы, а не леммы. По леммам сигнал чуть сильнее, но в браузере
морфологии нет, а сайт и расширение обязаны считать то же число, что scan.py.
Поэтому токенизация здесь нарочно примитивная и повторена в docs/scan.js байт
в байт: нижний регистр, ё → е, слово это кириллица с внутренними дефисами
(«кто-то», «северо-запад»). Латиница и цифры не считаются: в русском тексте
это имена, бренды и числа, их разнообразие о стиле не говорит.

Почему только начало и почему не на коротком. MATTR почти не зависит от
длины, но длинный текст модель разбавляет повторами заголовков и списков:
первые LEX_MAX_TOKENS слов сравнивают тексты разной длины честно и одинаково
дёшево в браузере. На коротком тексте окон мало и число шумит: у людей на
60-80 словах разброс 0.058 против 0.037 на 150+, и ниже LEX_MIN_TOKENS больше
половины срабатываний на людях приходилось именно на такие тексты. Поэтому
короче LEX_MIN_TOKENS словоформ признак не считается вовсе.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Окно скользящего TTR, число первых слов, на которых он считается, и
# минимальная длина, с которой признак вообще считается. Подобраны на половине
# корпуса (eval/MODERN-SLOP.md): окно 40 и 200 слов разделяют людей и машины
# лучше, чем 150 (AUC для GPT-5.6 0.78 против 0.75), 300 почти не добавляет.
LEX_WINDOW = 40
LEX_MAX_TOKENS = 200
LEX_MIN_TOKENS = 100

_TOKEN_RE = re.compile(r"[а-яё]+(?:-[а-яё]+)*")


@dataclass
class LexicalStats:
    tokens: int      # кириллических словоформ в тексте всего
    mattr: float     # MATTR по первым LEX_MAX_TOKENS словоформам; 0.0, если слов меньше окна.
                     # Не округляется: штраф считается от точного числа, как в браузере

    def as_dict(self) -> dict:
        return self.__dict__.copy()


def lexical_tokens(text: str) -> list[str]:
    """Словоформы для MATTR. Порт в docs/scan.js обязан дать тот же список."""
    return [t.replace("ё", "е") for t in _TOKEN_RE.findall(text.lower())]


def mattr(tokens: list[str], window: int = LEX_WINDOW) -> float:
    """Moving-average type-token ratio (Covington & McFall, 2010).

    Среднее по всем окнам длины window доли разных словоформ. Сумма копится в
    целых числах и делится один раз: так JS и Python получают одно и то же
    число с плавающей точкой, без накопленной разницы округлений.
    """
    n = len(tokens)
    if n < window:
        return 0.0
    counts: dict[str, int] = {}
    for t in tokens[:window]:
        counts[t] = counts.get(t, 0) + 1
    distinct = len(counts)
    total = distinct
    for i in range(window, n):
        new, old = tokens[i], tokens[i - window]
        counts[new] = counts.get(new, 0) + 1
        if counts[new] == 1:
            distinct += 1
        counts[old] -= 1
        if counts[old] == 0:
            distinct -= 1
        total += distinct
    return total / ((n - window + 1) * window)


def lexical_stats(text: str) -> LexicalStats:
    toks = lexical_tokens(text)
    return LexicalStats(tokens=len(toks), mattr=mattr(toks[:LEX_MAX_TOKENS]))
