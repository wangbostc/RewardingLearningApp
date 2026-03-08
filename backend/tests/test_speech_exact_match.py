from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.routes.speech import calculate_reading_similarity, is_exact_reading_match


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

