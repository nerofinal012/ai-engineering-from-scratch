#!/usr/bin/env python3
"""CLI quiz runner for AI Engineering from Scratch lessons."""

import argparse
import glob
import json
import random
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
PHASES_DIR = REPO_ROOT / "phases"

USE_COLOR = sys.stdout.isatty()
GREEN = "\033[32m" if USE_COLOR else ""
RED = "\033[31m" if USE_COLOR else ""
DIM = "\033[2m" if USE_COLOR else ""
BOLD = "\033[1m" if USE_COLOR else ""
RESET = "\033[0m" if USE_COLOR else ""


def resolve_lesson(code: str) -> Path:
    """Resolve 'NN/MM' to a lesson directory containing quiz.json."""
    parts = code.replace("\\", "/").split("/")
    if len(parts) != 2 or not all(p.isdigit() for p in parts):
        raise ValueError(f"Expected format NN/MM (e.g. 04/14), got: {code!r}")
    phase_num, lesson_num = parts
    matches = sorted(glob.glob(str(PHASES_DIR / f"{phase_num}-*" / f"{lesson_num}-*" / "quiz.json")))
    if not matches:
        raise FileNotFoundError(f"No quiz found for {phase_num}/{lesson_num}")
    if len(matches) > 1:
        raise RuntimeError(f"Ambiguous match for {phase_num}/{lesson_num}: {matches}")
    return Path(matches[0])


def list_phases() -> list[Path]:
    return sorted(p for p in PHASES_DIR.iterdir() if p.is_dir() and p.name[:2].isdigit())


def list_lessons(phase_dir: Path) -> list[Path]:
    return sorted(
        d for d in phase_dir.iterdir()
        if d.is_dir() and (d / "quiz.json").exists() and d.name[:2].isdigit()
    )


def prompt_choice(prompt: str, n: int) -> int:
    """Prompt for a 1..n choice, re-prompting on invalid input."""
    while True:
        try:
            raw = input(prompt).strip()
        except EOFError:
            print()
            sys.exit(130)
        if not raw.isdigit():
            print(f"  {DIM}enter a number 1-{n}{RESET}")
            continue
        choice = int(raw)
        if 1 <= choice <= n:
            return choice
        print(f"  {DIM}must be 1-{n}{RESET}")


def pick_interactive() -> Path:
    phases = list_phases()
    print(f"\n{BOLD}Select phase:{RESET}")
    for i, p in enumerate(phases, 1):
        print(f"  {i:2d}) {p.name}")
    pi = prompt_choice("> ", len(phases))
    phase = phases[pi - 1]

    lessons = list_lessons(phase)
    print(f"\n{BOLD}Select lesson in {phase.name}:{RESET}")
    for i, l in enumerate(lessons, 1):
        print(f"  {i:2d}) {l.name}")
    li = prompt_choice("> ", len(lessons))
    return lessons[li - 1] / "quiz.json"


def run_quiz(quiz_path: Path, stage_filter: str | None, shuffle: bool) -> int:
    data = json.loads(quiz_path.read_text(encoding="utf-8"))
    questions = data["questions"]
    if stage_filter:
        questions = [q for q in questions if q.get("stage") == stage_filter]
    if not questions:
        print(f"No questions matching stage={stage_filter!r}")
        return 0
    if shuffle:
        questions = list(questions)
        random.shuffle(questions)

    rel = quiz_path.relative_to(REPO_ROOT)
    print(f"\n{BOLD}{rel}{RESET}  ({len(questions)} questions)")

    correct_count = 0
    wrong = []  # list of (display_index, question_text)

    for i, q in enumerate(questions, 1):
        print(f"\n{BOLD}Q{i}/{len(questions)}{RESET} [{q['stage']}] {q['question']}")
        for j, opt in enumerate(q["options"], 1):
            print(f"  {j}) {opt}")
        choice = prompt_choice("answer: ", len(q["options"]))
        chosen_idx = choice - 1
        correct_idx = q["correct"]
        correct_display = correct_idx + 1  # 1-based for user display

        if chosen_idx == correct_idx:
            print(f"  {GREEN}✓ correct{RESET}")
            correct_count += 1
        else:
            print(f"  {RED}✗ incorrect{RESET} — correct answer was {correct_display}) {q['options'][correct_idx]}")
            wrong.append((i, q["question"]))
        print(f"  {DIM}{q['explanation']}{RESET}")

    total = len(questions)
    print(f"\n{BOLD}Score: {correct_count}/{total}{RESET}")
    if wrong:
        print(f"\n{RED}Missed:{RESET}")
        for idx, text in wrong:
            print(f"  Q{idx}: {text}")
    return 0 if correct_count == total else 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="CLI quiz runner for AI Engineering from Scratch.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="examples:\n"
               "  quiz.py 04/14            run all questions for phase 04, lesson 14\n"
               "  quiz.py 04 14            same, space-separated\n"
               "  quiz.py 00/01 --pre      only pre-lesson questions\n"
               "  quiz.py                  interactive picker",
    )
    parser.add_argument("code", nargs="*", help="lesson code as NN/MM or 'NN MM'")
    stage = parser.add_mutually_exclusive_group()
    stage.add_argument("--pre", action="store_const", const="pre", dest="stage")
    stage.add_argument("--post", action="store_const", const="post", dest="stage")
    parser.add_argument("--shuffle", action="store_true", help="shuffle question order (opt-in for replay)")
    args = parser.parse_args()

    try:
        if not args.code:
            quiz_path = pick_interactive()
        elif len(args.code) == 1:
            quiz_path = resolve_lesson(args.code[0])
        elif len(args.code) == 2:
            quiz_path = resolve_lesson("/".join(args.code))
        else:
            parser.error("expected 0, 1, or 2 positional args")
    except (ValueError, FileNotFoundError, RuntimeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print()
        return 130

    try:
        return run_quiz(quiz_path, args.stage, args.shuffle)
    except KeyboardInterrupt:
        print("\ninterrupted")
        return 130


if __name__ == "__main__":
    sys.exit(main())
