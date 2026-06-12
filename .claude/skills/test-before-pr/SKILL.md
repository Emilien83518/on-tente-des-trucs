---
name: test-before-pr
description: Test code on the current branch before creating a pull request. Use this skill whenever the user is about to open a PR, says "create a PR", "open a pull request", "push this for review", or any variation — always run tests first before creating the PR. Also trigger when the user says "test my code", "check for bugs", or "verify before merging". This skill catches bugs early by writing and running tests automatically, then filing a GitHub issue for each bug found.
---

# Test Before PR

Before creating any pull request, run this skill to verify the code works correctly.
The goal is to catch bugs early so they don't land in `main`.

## Step 1 — Find what changed

Run this to see which files were modified on this branch compared to `main`:

```bash
git diff main --name-only
```

Focus your testing on those files. Also check if any test files already exist:

```bash
# Look for existing test files
find . -name "test_*.py" -o -name "*_test.py" 2>/dev/null
```

## Step 2 — Run existing tests (if any)

If test files exist, run them:

```bash
python -m pytest -v
# or if pytest is not installed:
python -m unittest discover -v
```

Note which tests pass and which fail. If all tests pass, jump to Step 4.

## Step 3 — Write and run a temporary test script (if no tests exist)

If no test files exist, write a temporary script called `_temp_test.py` in the project root.

The test script should:
- Import the changed files/classes
- Create instances of the objects
- Call the main methods with realistic inputs
- Use `assert` statements to verify the output is what you expect
- Print a clear PASS or FAIL message for each test

### Example structure for this chess project:

```python
# _temp_test.py — temporary test script, delete after running
import sys

passed = 0
failed = 0

def test(name, condition, detail=""):
    global passed, failed
    if condition:
        print(f"  PASS — {name}")
        passed += 1
    else:
        print(f"  FAIL — {name}" + (f": {detail}" if detail else ""))
        failed += 1

# --- Test each changed piece/class ---
# Import and instantiate, call get_valid_moves with a fake board, check results

print("Running tests...")

# Example: testing a piece
# from pieces.queen import Queen
# board = [[None]*8 for _ in range(8)]
# q = Queen("white", (3, 3))
# moves = q.get_valid_moves(board)
# test("Queen has moves from center", len(moves) > 0)
# test("Queen does not move off board", all(0 <= r <= 7 and 0 <= c <= 7 for r, c in moves))

print(f"\nResults: {passed} passed, {failed} failed")
sys.exit(0 if failed == 0 else 1)
```

Write real tests for the actual changed files — don't just copy the example above.

Run the script:

```bash
python _temp_test.py
```

After running, delete the temp file:

```bash
del _temp_test.py   # Windows
# or: rm _temp_test.py  (Linux/Mac)
```

## Step 4 — For each bug found, create a GitHub issue

If any test fails, that's a bug. For each one:

1. Identify exactly what failed (which file, which method, what the wrong behavior is)
2. Create a GitHub issue:

```bash
gh issue create \
  --title "Bug: <short description>" \
  --label "bug" \
  --body "## Bug description
<what went wrong>

## Location
File: <file path>
Method: <method name>

## Expected behavior
<what it should do>

## Actual behavior
<what it actually does>

## Found by
Automated test before PR on branch \`$(git branch --show-current)\`"
```

3. Fix the bug in the code
4. Re-run the tests to confirm the fix works

## Step 5 — Report and proceed

Once all tests pass:
- Summarize what was tested and what (if anything) was found and fixed
- Then proceed to create the PR with `gh pr create`

If bugs were found and fixed, mention the issue numbers in the PR body so they are linked.

## Important rules

- Never create the PR if tests are still failing — fix first, then open the PR
- Always delete `_temp_test.py` before committing — it should never be committed
- Be thorough: test edge cases like empty squares, pieces at board edges, friendly/enemy blocking
- If a bug is found but cannot be fixed right now, still create the issue, note it in the PR body, and warn the user before proceeding
