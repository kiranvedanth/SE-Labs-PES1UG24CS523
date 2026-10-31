import pytest
from spam_scoring import score_message, classify, filter_inbox, inbox_status


# ---------------------------------------------------------------------------
# Starter tests (from the original test_spam_scoring.py)
# ---------------------------------------------------------------------------
def test_plain_message_scores_zero():
    # No spam words, no shouting, no links, unknown sender -> 0
    assert score_message("hello there", False, 0) == 0


def test_low_score_is_clean():
    # classify: falls through both ifs -> "clean"
    assert classify(1) == "clean"


# ---------------------------------------------------------------------------
# score_message: lines inside the word loop
# ---------------------------------------------------------------------------
def test_spam_word_adds_two_points():
    # Targets: spam-word branch (score += 2). "FREE!" -> lower+strip -> "free"
    assert score_message("FREE!", False, 0) == 2


def test_shouted_word_adds_one_point():
    # Targets: elif branch (uppercase and longer than 3 chars) -> score += 1
    assert score_message("HELLO", False, 0) == 1


# ---------------------------------------------------------------------------
# score_message: link handling
# ---------------------------------------------------------------------------
def test_many_links_add_four_points():
    # Targets: link_count > 3 -> score += 4
    assert score_message("hello", False, 4) == 4


def test_few_links_add_one_point():
    # Targets: elif link_count > 0 -> score += 1
    assert score_message("hello", False, 2) == 1


# ---------------------------------------------------------------------------
# score_message: known sender
# ---------------------------------------------------------------------------
def test_known_sender_score_never_goes_negative():
    # Targets: sender_known, score = 0 - 3 = -3 -> reset to 0
    assert score_message("hello", True, 0) == 0


# ---------------------------------------------------------------------------
# classify
# ---------------------------------------------------------------------------
def test_score_eight_is_spam():
    # Targets: score >= 8 -> "spam"
    assert classify(8) == "spam"


def test_score_five_is_suspicious():
    # Targets: score >= 4 -> "suspicious"
    assert classify(5) == "suspicious"


# ---------------------------------------------------------------------------
# filter_inbox
# ---------------------------------------------------------------------------
def test_filter_inbox_counts_each_label():
    messages = [
        ("free winner prize urgent cash", False, 4),  # 10 + 4 = 14 -> spam
        ("free winner", False, 0),                    # 2 + 2 = 4  -> suspicious
        ("hello", False, 0),                          # 0          -> clean
        ("hello", True, 0),                           # 0 - 3 -> 0 -> clean
    ]
    assert filter_inbox(messages) == {"spam": 1, "suspicious": 1, "clean": 2}


# ---------------------------------------------------------------------------
# inbox_status
# ---------------------------------------------------------------------------
def test_status_empty_inbox():
    # Targets: total == 0 -> "empty"
    assert inbox_status({"spam": 0, "suspicious": 0, "clean": 0}) == "empty"


def test_status_flooded_inbox():
    # Targets: ratio > 0.5 (6/10 = 0.6) -> "flooded"
    assert inbox_status({"spam": 6, "suspicious": 2, "clean": 2}) == "flooded"


def test_status_noisy_inbox():
    # Targets: ratio > 0.2 (3/10 = 0.3) -> "noisy"
    assert inbox_status({"spam": 3, "suspicious": 3, "clean": 4}) == "noisy"


def test_status_healthy_inbox():
    # Targets: fall-through (1/10 = 0.1) -> "healthy"
    assert inbox_status({"spam": 1, "suspicious": 4, "clean": 5}) == "healthy"
