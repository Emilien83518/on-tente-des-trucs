---
name: comment-everything
description: Add a clear comment to every function and every class written in this project. Always trigger this skill whenever writing any new code — functions, classes, or methods — especially in Python. This skill exists because the user is a beginner and needs every piece of code explained in plain language so they can learn as the project grows. Never write a function or class without a comment above it.
---

# Comment Everything

The user is learning to code. Every function and every class must have a comment that explains what it does in plain, simple language — no jargon, no assumptions.

## Rules

- **Every class** gets a comment above it explaining what it represents and its role in the project
- **Every method/function** gets a comment explaining:
  - What it does (one sentence, plain English)
  - What the inputs are (parameters) and what they mean
  - What it gives back (return value), if anything
- Write comments **above** the function or **on the line right after** `def` / `class` — be consistent
- Keep comments **short and honest** — one or two lines max
- Use **simple words** — imagine explaining to someone who has never coded before
- Do not use technical words like "instantiate", "iterate", "invoke" without explaining them

## Format to follow

### For a class:
```python
# Represents a [thing] in the game — [one sentence on its role]
class MyClass:
```

### For a function/method:
```python
def my_function(param1, param2):
    # [What this function does in one plain sentence]
    # param1: [what it is]
    # param2: [what it is]
    # Returns: [what comes out, or nothing if it returns None]
```

## Example — good comment:
```python
def get_valid_moves(self, board):
    # Returns a list of all squares this piece is allowed to move to
    # board: the 8x8 grid representing the current state of the game
    # Returns: a list of (row, col) positions the piece can legally reach
```

## Example — bad comment (too vague or technical):
```python
def get_valid_moves(self, board):
    # Computes valid move set via directional iteration
```

## When reviewing existing code

If asked to review or modify existing code that is missing comments, add the missing comments before doing anything else.
