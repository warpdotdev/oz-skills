"""Повтор фразы между абзацами: модель пересказывает сама себя.

Признак: одна и та же цепочка из REPEAT_N словоформ дословно стоит в двух
разных абзацах. Так пишут Llama-3.3 и YandexGPT: вывод повторяет вступление,
пункт повторяет подводку. У людей тоже бывает, прежде всего в новостях (лид
пересказан в теле заметки), в справках с длинными официальными названиями и в
лонгридах.

Почему это заметка, а не штраф. Подбор на LLMTrace, Пикабу и длинных
человеческих текстах (eval/MODERN-SLOP.md, раздел про повтор фраз) показал
потолок пользы: даже бесконечный штраф вывел бы из полосы «чисто» 2,8% текстов
Llama-3.3 и меньше процента у остальных моделей, потому что текст с такими
повторами почти всегда уже задет другими признаками (медиана счёта у Llama с
повтором 58, без повтора 80). Людей при этом задело бы столько же или больше. Поэтому в счёт повтор не входит, сканер
только показывает сами фразы: это готовая подсказка для правки.

Токенизация своя и повторена в docs/scan.js байт в байт, как у MATTR:
- абзац это непустая строка (у Пикабу и в чатах абзацы идут через один
  перевод строки, пустая строка тут не обязательна);
- строки-заголовки Markdown («## ...») не считаются;
- цитаты в «ёлочках», „лапках“ и "прямых" кавычках вырезаются: чужие слова
  автор повторяет законно;
- слово это кириллица с внутренними дефисами после нижнего регистра и ё → е;
- латиница, цифры, скобки, кавычки и знаки конца предложения рвут цепочку:
  n-грамма не перескакивает через «2020» и через точку;
- n-грамма, где меньше REPEAT_MIN_CONTENT полнозначных слов («и в то же
  время, как и»), не считается: это грамматика, а не фраза;
- считаются только первые REPEAT_MAX_TOKENS словоформ: длинный текст копит
  повторы просто длиной, и без окна признак на лонгридах людей шумит.

Перекрывающиеся n-граммы одного повтора склеиваются: «мы живём в мире, где
всё меняется» это одна фраза, а не две шестёрки.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

REPEAT_N = 6
REPEAT_MAX_TOKENS = 600
REPEAT_MIN_CONTENT = 2
# Сколько разных фраз нужно для заметки. Одна повторённая фраза в первых 600
# словах у людей встречается в 1-3% коротких текстов и в 4-16% длинных, две в
# 0,2-0,7% коротких и 1-5% длинных.
REPEAT_MIN_PHRASES = 2

# Служебные слова: предлоги, союзы, частицы, местоимения, связка. N-грамма из
# одних таких слов («что это может быть так») фразой не считается.
FUNCTION_WORDS = frozenset("""
а б бы в во вот да для до же за и из или им их к ко как ли либо между на над не ни но о об обо
от ото по под при про с со так там то тоже только у уже чем что чтобы это этот эта эти этого этой
этом этим тот та те того той том тем тех я ты он она оно мы вы они его ее их ему ей нам вам
меня тебя нас вас мне тебе себя себе свой своя свое свои своего своей своих своим который которая
которое которые которого которой которых котором которым был была было были быть есть будет будут
бывает если когда где куда чтоб все весь вся всего всех всем также еще уж даже лишь нет
очень более менее можно нужно надо может могут мой моя мое мои наш наша наше наши ваш ваша ваше
ваши кто чего чему ним ней них него нее нему
""".split())

_TOKEN_RE = re.compile(r"[а-яё]+(?:-[а-яё]+)*|[a-z0-9]+|[.!?…;:()\[\]\"«»“”„]")
_QUOTE_RE = re.compile(r"«[^«»\n]*»|„[^„“\n]*“|\"[^\"\n]*\"")
# Пробелы явные, не \s: у Python и JS классы \s расходятся на редких символах.
_HEADING_RE = re.compile(r"^[ \t]*#{1,6}[ \t]")


@dataclass
class RepeatStats:
    tokens: int                     # словоформ просмотрено (не больше REPEAT_MAX_TOKENS)
    phrases: list[str] = field(default_factory=list)  # разные повторённые фразы, в порядке текста

    def as_dict(self) -> dict:
        return {"tokens": self.tokens, "phrases": list(self.phrases)}


def _runs(line: str) -> list[list[str]]:
    """Цепочки подряд идущих кириллических словоформ строки."""
    runs: list[list[str]] = []
    cur: list[str] = []
    for tok in _TOKEN_RE.findall(line.lower()):
        if "а" <= tok[0] <= "я" or tok[0] == "ё":
            cur.append(tok.replace("ё", "е"))
        else:
            if cur:
                runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    return runs


def repeat_stats(text: str) -> RepeatStats:
    """Повторённые между абзацами фразы. Порт в docs/scan.js обязан дать тот же список."""
    text = _QUOTE_RE.sub(" . ", text)
    budget = REPEAT_MAX_TOKENS
    where: dict[str, set[int]] = {}          # n-грамма -> номера строк
    order: list[tuple[int, int, list[str]]] = []  # (строка, сквозная позиция, цепочка)
    pos = 0
    for li, line in enumerate(text.split("\n")):
        if budget <= 0:
            break
        if _HEADING_RE.match(line):
            continue
        for run in _runs(line):
            run = run[:budget]
            budget -= len(run)
            for i in range(len(run) - REPEAT_N + 1):
                key = " ".join(run[i:i + REPEAT_N])
                where.setdefault(key, set()).add(li)
                order.append((li, pos + i, run[i:i + REPEAT_N]))
            pos += len(run) + 1  # разрыв: следующая цепочка не продолжает эту
            if budget <= 0:
                break
    seen = REPEAT_MAX_TOKENS - max(budget, 0)

    def repeated(words: list[str]) -> bool:
        key = " ".join(words)
        return (len(where[key]) >= 2
                and sum(1 for w in words if w not in FUNCTION_WORDS) >= REPEAT_MIN_CONTENT)

    phrases: list[str] = []
    keys: set[str] = set()
    cur: list[str] = []
    cur_key = ""
    prev = (-1, -2)
    for li, p, words in order:
        if not repeated(words):
            continue
        if prev[0] == li and prev[1] == p - 1 and cur:
            cur.append(words[-1])            # та же фраза тянется дальше
        else:
            if cur and cur_key not in keys:
                keys.add(cur_key)
                phrases.append(" ".join(cur))
            cur, cur_key = list(words), " ".join(words)
        prev = (li, p)
    if cur and cur_key not in keys:
        phrases.append(" ".join(cur))
    return RepeatStats(tokens=seen, phrases=phrases)
