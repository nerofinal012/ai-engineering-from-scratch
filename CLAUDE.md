# AI Engineering from Scratch

Course curriculum spanning ~20 phases, 260+ lessons. Each lesson is a
self-contained directory with notes, code, and a quiz.

## Layout

```
phases/<NN>-<phase-name>/
  <MM>-<lesson-name>/
    code/         # lesson scripts (e.g. verify.py)
    quiz.json     # 5 questions, mixed pre- and post-lesson
    ...
```

Phase and lesson directories are always prefixed with a unique 2-digit
number — that prefix is the canonical short ID.

## Environment

- WSL Ubuntu 24.04 on Windows 11.
- Python venv at `./.venv` (Python 3.12). Activate with
  `source .venv/bin/activate`.
- Node via fnm; cargo via rustup. Both available in interactive shells.
- Run `python phases/00-setup-and-tooling/01-dev-environment/code/verify.py`
  to confirm all toolchain prerequisites pass (7/7 core).

## Quiz runner

`quiz.py` at the repo root runs any lesson's quiz from the command line.
Pure stdlib, no extra deps.

```
python quiz.py 04/14            # phase 04, lesson 14
python quiz.py 04 14            # space-separated form
python quiz.py 00/01 --pre      # only pre-lesson questions
python quiz.py 00/01 --post     # only post-lesson questions
python quiz.py 00/01 --shuffle  # randomize question order (replay mode)
python quiz.py                  # interactive picker, grouped by phase
```

Behavior:

- Questions are shown in their authored order by default (`--shuffle`
  to opt out); option order within a question is never shuffled.
- Each answer gives immediate ✓/✗ feedback plus the explanation.
- Correct answers are displayed as 1-4 (matching what was shown), not
  the 0-based JSON index.
- Invalid input (non-digit, out of range) re-prompts without crashing.
- End-of-quiz summary shows score `X/Y` and lists missed questions.
- Exit codes: `0` perfect score, `1` any wrong, `2` argument/lookup error.

## Quiz JSON schema

All 120+ `quiz.json` files share one schema (verified consistent across
phases 00, 01, 04, 16):

```json
{
  "questions": [
    {
      "stage": "pre" | "post",
      "question": "...",
      "options": ["...", "...", "...", "..."],
      "correct": 0,
      "explanation": "..."
    }
  ]
}
```

Always 4 options. `correct` is a 0-based index into `options`. Typical
quiz has 5 questions, mixed pre/post.
