# Canvas Autograder

Automatically grades Canvas LMS assignments based on a minimum word count. Fetches all submissions for a given assignment, counts words in each submission body, and posts a grade for any submission that meets the threshold.

## Setup

1. **Install dependencies:**

   ```
   pip install requests python-dotenv
   ```

2. **Configure your Canvas API token:**

   Create a `.env` file in the project root (already gitignored):

   ```
   CANVAS_TOKEN=your_canvas_api_token_here
   ```

   The script loads this automatically on startup — no shell setup needed.

3. **Edit `autograder.py`** to set your course and assignment:

   ```python
   COURSE_ID = 831226
   ASSIGNMENT_ID = 9754940
   WORD_COUNT_MIN = 100
   SCORE_TO_GIVE = 1
   ```

## Usage

**Dry run** (prints what would happen, posts no grades):

Set `DRY_RUN = True` in `autograder.py`, then:

```
python autograder.py
```

**Live run** (actually posts grades to Canvas):

Set `DRY_RUN = False`, then run the same command. Already-graded submissions are automatically skipped, so the script is safe to re-run.

## Word Counting

A submission earns a grade if it contains at least `WORD_COUNT_MIN` words. The word counter:

- Strips HTML tags (Canvas submissions are HTML)
- Decodes HTML entities (`&amp;`, `&nbsp;`, etc.)
- Removes URLs so they don't inflate the count
- Counts only tokens containing at least one alphanumeric character (filters out stray punctuation)
- Treats hyphenated words (e.g. "well-known") as a single word

## Tests

```
pip install pytest
python -m pytest test_autograder.py -v
```

Tests cover edge cases including empty input, HTML stripping, URL removal, punctuation filtering, whitespace handling, and non-English characters.
