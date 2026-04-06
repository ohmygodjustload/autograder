import pytest
from unittest.mock import patch

with patch.dict("os.environ", {"CANVAS_TOKEN": "fake-token"}):
    from autograder import count_words


class TestCountWordsNullAndEmpty:
    def test_none_input(self):
        assert count_words(None) == 0

    def test_empty_string(self):
        assert count_words("") == 0

    def test_whitespace_only(self):
        assert count_words("   \n\t  ") == 0


class TestCountWordsThreshold:
    def test_exact_100_words(self):
        text = " ".join(["word"] * 100)
        assert count_words(text) == 100

    def test_99_words(self):
        text = " ".join(["word"] * 99)
        assert count_words(text) == 99


class TestCountWordsHTML:
    def test_adjacent_p_tags_not_fused(self):
        assert count_words("<p>Hello</p><p>World</p>") == 2

    def test_nested_tags(self):
        assert count_words("<div><span>one</span> <b>two</b></div>") == 2

    def test_nbsp_entities(self):
        assert count_words("Hello&nbsp;&nbsp;&nbsp;world") == 2

    def test_amp_entity(self):
        # "&" alone is not alphanumeric, so it's filtered out
        assert count_words("bread &amp; butter") == 2


class TestCountWordsURLs:
    def test_url_stripped(self):
        assert count_words("Visit https://example.com/a/b/c for info") == 3

    def test_url_only(self):
        assert count_words("https://example.com/long/path/here") == 0

    def test_http_url(self):
        assert count_words("See http://example.com please") == 2


class TestCountWordsPunctuation:
    def test_punctuation_only_tokens(self):
        assert count_words("... --- *** !!!") == 0

    def test_hyphenated_words(self):
        assert count_words("well-known self-sustaining") == 2

    def test_colon_in_time(self):
        # "10:30" stays as a single token
        assert count_words("Meet at 10:30 today") == 4


class TestCountWordsWhitespace:
    def test_newlines(self):
        assert count_words("Line1\nLine2\n\nLine3") == 3

    def test_tabs(self):
        assert count_words("one\ttwo\t\tthree") == 3

    def test_multiple_spaces(self):
        assert count_words("one   two     three") == 3


class TestCountWordsInternational:
    def test_accented_characters(self):
        assert count_words("café résumé naïve") == 3

    def test_chinese_characters(self):
        # Each character cluster separated by spaces counts as a word
        assert count_words("你好 世界") == 2


class TestCountWordsIntegration:
    def test_mixed_html_urls_punctuation(self):
        text = (
            "<p>This is a <b>test</b> submission.</p>"
            "<p>Visit https://example.com/page for more info!</p>"
            "<p>Some well-known facts: the café was open...</p>"
        )
        # "This is a test submission" = 5
        # "Visit for more info" = 4 (URL stripped)
        # "Some well-known facts the café was open" = 7
        assert count_words(text) == 16

    def test_100_real_words_with_html(self):
        words = " ".join(f"word{i}" for i in range(105))
        text = f"<div><p>{words}</p><p>https://example.com/pad</p><p>--- ... !!!</p></div>"
        assert count_words(text) == 105
