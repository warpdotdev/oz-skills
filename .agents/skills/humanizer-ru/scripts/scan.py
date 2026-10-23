#!/usr/bin/env python3
"""CLI-сканер: прогоняет текст через детерминированные метрики humanizer-ru.

Использование (из корня репо; у установленного скилла путь: <папка скилла>/scripts/scan.py):
    python skills/humanizer-ru/scripts/scan.py path/to/text.txt
    python skills/humanizer-ru/scripts/scan.py - <<'EOF'   (текст на stdin)
    python skills/humanizer-ru/scripts/scan.py text.txt --json

Это машинная половина режима «Аудит». Для полного очеловечивания (семантика,
голос, рерайт) нужен сам скилл — этот сканер только подсвечивает грепабельные
маркеры и считает метрики, которые LLM не умеет измерять на глаз.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from humanizer_metrics import diff_facts, facts_verdict, scan_report
    from humanizer_metrics.burstiness import rhythm_verdict
    from humanizer_metrics.lexical import LEX_MIN_TOKENS
    from humanizer_metrics.score import LEX_MUTED_GENRES, LEX_THRESHOLD
    from humanizer_metrics.markers import GENRE_MUTED_BANS, GENRES, marker_verdict
    from humanizer_metrics.morphology import morph_verdict
    from humanizer_metrics.repeats import REPEAT_MAX_TOKENS, REPEAT_N
    from humanizer_metrics.structure import structure_verdict
except ImportError as exc:
    print(f"[ошибка] не хватает зависимостей сканера ({exc.name}); балла не будет.\n"
          "Поставьте один раз любым способом:\n"
          "  uvx ru-humanizer файл.txt        (без установки, нужен uv)\n"
          "  pipx install ru-humanizer        (даёт команду ru-humanizer)\n"
          "  отдельный venv с razdel и pymorphy3 (команды в README, раздел про зависимости)\n"
          "Системный pip на macOS с Homebrew и на Debian/Ubuntu падает с\n"
          "externally-managed-environment (PEP 668): системный Python закрыт для pip.",
          file=sys.stderr)
    raise SystemExit(2)


def _read(src: str) -> str:
    """Текст из файла или stdin. BOM в начале снимается: иначе U+FEFF
    считается невидимым символом и роняет балл чистого текста."""
    if src == "-":
        try:
            return sys.stdin.read().lstrip("\ufeff")
        except UnicodeDecodeError:
            print("[ошибка] stdin не в кодировке UTF-8, передайте текст в UTF-8", file=sys.stderr)
            raise SystemExit(2)
    try:
        return Path(src).read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        print(f"[ошибка] файл не найден: {src}", file=sys.stderr)
        raise SystemExit(2)
    except UnicodeDecodeError:
        print(f"[ошибка] {src} не в кодировке UTF-8, сохраните файл в UTF-8", file=sys.stderr)
        raise SystemExit(2)
    except OSError as exc:
        print(f"[ошибка] не могу прочитать {src}: {exc.strerror or exc}", file=sys.stderr)
        raise SystemExit(2)


def utf8_console() -> None:
    """Отчёт с ≥, ⛔ и ✓ в консоли Windows (cp1251, cp866) падал с
    UnicodeEncodeError при выводе в файл. Пишем UTF-8, непредставимое заменяем.
    Stdin читаем как UTF-8 строго: иначе на Windows текст из трубы декодируется
    кодировкой локали, а с заменой ошибок кириллица молча стала бы «�»."""
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8", errors="strict")
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def _line_numbers(text: str, positions: list[int], limit: int = 3) -> str:
    """Номера строк первых вхождений: «стр. 3, 7» — чтобы находку можно
    было найти в тексте глазами."""
    lines = sorted({text.count("\n", 0, p) + 1 for p in positions})
    shown = ", ".join(str(n) for n in lines[:limit])
    more = f", +{len(lines) - limit}" if len(lines) > limit else ""
    return f"стр. {shown}{more}"


def main() -> int:
    utf8_console()
    # `ru-humanizer mcp` поднимает MCP-сервер той же командой, что и сканер:
    # так карточка в реестре MCP запускает пакет как `uvx ru-humanizer mcp`.
    if sys.argv[1:2] == ["mcp"]:
        from humanizer_metrics.mcp_server import main as mcp_main
        return mcp_main()
    ap = argparse.ArgumentParser(description="Детерминированный сканер AI-маркеров (humanizer-ru)")
    ap.add_argument("source", help="файл с текстом или '-' для stdin")
    ap.add_argument("--json", action="store_true", help="вывод в JSON")
    ap.add_argument("--before", metavar="ФАЙЛ",
                    help="исходник до правки: сканер добавит «было/стало» по чистоте и "
                         "проверит факт-замок (числа, даты, имена, ссылки, код). "
                         "Новый факт, которого не было в исходнике, даёт exit 2")
    ap.add_argument("--genre", choices=GENRES, default="marketing",
                    help="жанр текста: снимает маркеры, законные для регистра "
                         "(academic, legal, fiction, news). По умолчанию marketing: "
                         "строгий режим, под него откалиброваны пороги")
    args = ap.parse_args()

    text = _read(args.source)

    if not text.strip():
        if args.json:
            print(json.dumps({"empty": True}, ensure_ascii=False))
        else:
            print("Текст пуст, сканировать нечего.")
        return 0

    genre = args.genre
    sr = scan_report(text, genre)
    rep, sc, bans, soft = sr.report, sr.score, sr.hard_bans, sr.markers
    before_text = _read(args.before) if args.before else None
    before_sc = scan_report(before_text, genre).score if before_text is not None else None
    fdiff = diff_facts(before_text, text) if before_text is not None else None
    EM_DASH_MUTED = "Длинное тире" in GENRE_MUTED_BANS.get(genre, set())

    if args.json:
        out = sr.as_dict()
        if fdiff is not None:
            out["before"] = {"source": args.before, "score": before_sc.score, "band": before_sc.band}
            out["facts"] = fdiff.as_dict()
        print(json.dumps(out, ensure_ascii=False, indent=2))
        if fdiff is not None and not fdiff.ok:
            return 2
        return 1 if bans else 0

    print(f"=== humanizer-ru scan: {args.source} ===")
    if genre != "marketing":
        print(f"жанр: {genre} (снято маркеров по жанру: "
              f"{sr.muted_bans} банов, {sr.muted_markers} мягких)")
    print()

    if sr.non_russian:
        print("⚠ Текст не похож на русский: скилл и метрики рассчитаны на русский "
              "язык, отчёт ниже не показателен.\n")

    if before_sc is not None:
        print(f"ЧИСТОТА: было {before_sc.score}, стало {sc.score}/100  [{sc.band}]")
    else:
        print(f"ЧИСТОТА: {sc.score}/100  [{sc.band}]")
    print("  (≥85 чисто · 60-84 точечная правка · <60 рерайт)")
    if sc.penalties:
        for reason, pts in sc.penalties:
            print(f"  {pts:+d}  {reason}")
    else:
        print("  без штрафов")
    for note in sc.notes:
        print(f"  ℹ  {note}")
    print()

    print("HARD BANS:")
    if bans:
        for h in bans:
            note = " (штраф по плотности, допуск ~2/100 слов)" if h.marker == "Длинное тире" else ""
            print(f"  ⛔ {h.marker} ×{h.count} ({_line_numbers(text, h.positions)}){note}")
    else:
        print("  ✓ чисто")
    print()

    print(f"Маркеры (быстрый сканер): {marker_verdict(soft)}")
    top = sorted(soft, key=lambda x: -x.count)
    for h in top[:12]:
        print(f"  • [{h.category}] «{h.marker}» ×{h.count} ({_line_numbers(text, h.positions)})")
    if len(top) > 12:
        print(f"  … и ещё {len(top) - 12}")
    print()

    print("Ритм / типографика:")
    print(f"  {rhythm_verdict(rep.rhythm, dash_ok=EM_DASH_MUTED)}")
    print(f"  предложений: {rep.rhythm.sentences}, средняя длина: {rep.rhythm.mean_len:.1f} "
          f"(min {rep.rhythm.min_len} / max {rep.rhythm.max_len}), CV: {rep.rhythm.cv_len}")
    print(f"  многоточий: {rep.rhythm.ellipsis}, скобок: {rep.rhythm.parentheses}, "
          f"вопросов: {rep.rhythm.questions}")
    if rep.lexical.tokens >= LEX_MIN_TOKENS:
        rule = (f"в жанре {genre} не штрафуется" if genre in LEX_MUTED_GENRES
                else f"штраф выше {LEX_THRESHOLD}")
        print(f"  лексическое разнообразие: MATTR {rep.lexical.mattr:.3f} "
              f"(у людей обычно 0.90 ± 0.04, {rule})")
    else:
        print(f"  лексическое разнообразие: не считается, словоформ {rep.lexical.tokens} "
              f"(нужно от {LEX_MIN_TOKENS})")
    print()

    print("Морфология:")
    print(f"  {morph_verdict(rep.morph)}")
    print(f"  сущ.: {rep.morph.nouns}, глаг.форм: {rep.morph.verbs}, "
          f"номинализаций: {rep.morph.nominalizations}")
    print()

    print("Структура (уровень документа):")
    print(f"  {structure_verdict(rep.structure)}")
    phrases = rep.repeats.phrases
    if phrases:
        print(f"  повтор фраз между абзацами: {len(phrases)} (цепочки от {REPEAT_N} слов в первых "
              f"{REPEAT_MAX_TOKENS} словоформах, в счёт не входит)")
        for ph in phrases[:5]:
            print(f"    «{ph}»")
        if len(phrases) > 5:
            print(f"    … и ещё {len(phrases) - 5}")
    else:
        print(f"  повторов фраз между абзацами нет (цепочки от {REPEAT_N} слов)")

    if fdiff is not None:
        print()
        print(f"Факт-замок (против {args.before}):")
        print(f"  {facts_verdict(fdiff)}")
        for x in fdiff.added:
            print(f"  ✗ новое: {x}")
        for x in fdiff.lost:
            print(f"  ⚠ потеряно: {x}")
        for x in fdiff.claims_added:
            print(f"  ⚠ утверждение появилось: {x}")
        for x in fdiff.emphasis_lost:
            print(f"  ℹ снято {x} (шаблонный жирный снимают нарочно, смысловой проверьте)")
        if fdiff.soft_added:
            print(f"  ℹ мелкие количества появились: {', '.join(fdiff.soft_added)} "
                  "(идиомы и пересказ чисел не считаются, проверьте глазами)")
        if not fdiff.ok:
            return 2

    # Exit code: ненулевой, если есть HARD BANS — удобно для CI/pre-commit.
    return 1 if bans else 0


if __name__ == "__main__":
    raise SystemExit(main())
