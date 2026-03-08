from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.routes.speech import (
    calculate_reading_similarity,
    compare_word_feedback,
    is_exact_reading_match,
    normalize_text,
)


def statuses(tokens):
    return [token["status"] for token in tokens if token["status"] != "neutral"]


def texts(tokens):
    return [token["text"] for token in tokens if token["status"] != "neutral"]


def test_normalize_text_removes_punctuation_and_lowercases():
    assert normalize_text("Hello,   WORLD!") == "hello world"


def test_compare_word_feedback_marks_wrong_and_missing_words():
    expected_tokens, heard_tokens = compare_word_feedback(
        "The cat sat on the mat.",
        "The dog sat on mat",
    )

    assert texts(expected_tokens) == ["The", "cat", "sat", "on", "the", "mat"]
    assert statuses(expected_tokens) == ["correct", "wrong", "correct", "correct", "missing", "correct"]
    assert texts(heard_tokens) == ["The", "dog", "sat", "on", "mat"]
    assert statuses(heard_tokens) == ["correct", "wrong", "correct", "correct", "correct"]


def test_compare_word_feedback_marks_extra_words():
    expected_tokens, heard_tokens = compare_word_feedback(
        "I can see a cat.",
        "I can really see a cat",
    )

    assert statuses(expected_tokens) == ["correct", "correct", "correct", "correct", "correct"]
    assert statuses(heard_tokens) == ["correct", "correct", "extra", "correct", "correct", "correct"]


def test_exact_reading_match_allows_case_and_punctuation_only_differences():
    assert is_exact_reading_match("The cat sat on the mat.", "the cat sat on the mat") is True


def test_exact_reading_match_rejects_wrong_or_missing_words():
    assert is_exact_reading_match("The cat sat on the mat.", "The dog sat on the mat") is False
    assert is_exact_reading_match("The cat sat on the mat.", "The cat sat on mat") is False


def test_exact_reading_match_rejects_word_order_changes():
    assert is_exact_reading_match("I can see a cat.", "I can a see cat") is False


def test_similarity_is_only_100_for_exact_matches():
    assert calculate_reading_similarity("I can see a cat.", "I can see a cat") == 100.0
    assert calculate_reading_similarity("I can see a cat.", "I can see the cat") < 100.0
