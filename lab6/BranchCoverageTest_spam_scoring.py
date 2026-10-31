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
# score_message: word loop
# ---------------------------------------------------------------------------
def test_empty_text_does_not_enter_word_loop():
    # Targets: `for word in text.split()` with no iterations
    assert score_message("", False, 0) == 0


def test_spam_word_adds_two_points():
    # Targets: spam-word branch True (score += 2). "FREE!" -> "free"
    assert score_message("FREE!", False, 0) == 2


@pytest.mark.parametrize(
    "text",
    ["FREE!", "Prize.", "cash,", "Winner", "URGENT", "urgent!!"],
)
def test_spam_words_ignore_case_and_punctuation(text):
    # Targets: lower() and strip("!.,") before the SPAM_WORDS lookup
    assert score_message(text, False, 0) == 2


def test_multiple_spam_words_accumulate():
    # Targets: loop repeating the spam-word branch: 5 words x 2 = 10
    assert score_message("free winner prize urgent cash", False, 0) == 10


def test_non_spam_word_is_not_scored():
    # Targets: spam-word condition False and word not uppercase (elif False)
    assert score_message("hello", False, 0) == 0


def test_shouted_word_adds_one_point():
    # Targets: elif branch True (isupper and len > 3) -> "HELLO" = 5 chars
    assert score_message("HELLO", False, 0) == 1


@pytest.mark.parametrize(
    "text, expected",
    [
        ("USA", 0),    # uppercase but exactly 3 chars -> len > 3 False
        ("ABCD", 1),   # uppercase and exactly 4 chars -> len > 3 True
        ("hello", 0),  # not uppercase -> isupper() False
        ("Hello", 0),  # mixed case -> isupper() False
    ],
)
def test_shouting_boundary(text, expected):
    # Targets: both operands of `word.isupper() and len(word) > 3`
    assert score_message(text, False, 0) == expected


def test_shouted_spam_word_scored_once_as_spam():
    # Targets: first condition wins; "FREE!" counts 2, not 2 + 1
    assert score_message("FREE! HELLO", False, 0) == 3


# ---------------------------------------------------------------------------
# score_message: link handling
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "links, expected",
    [
        (0, 0),   # link_count > 3 False and link_count > 0 False
        (1, 1),   # elif True, lower bound
        (3, 1),   # elif True, upper boundary (3 is not > 3)
        (4, 4),   # if True, boundary (4 > 3)
        (10, 4),  # if True, well above boundary
    ],
)
def test_link_scoring_boundaries(links, expected):
    # Targets: `if link_count > 3` / `elif link_count > 0` True and False
    assert score_message("hello", False, links) == expected


# ---------------------------------------------------------------------------
# score_message: known sender
# ---------------------------------------------------------------------------
def test_known_sender_score_never_goes_negative():
    # Targets: sender_known True, score 0 - 3 = -3 -> `score < 0` True -> 0
    assert score_message("hello", True, 0) == 0


def test_known_sender_with_high_score_is_reduced_by_three():
    # Targets: sender_known True, `score < 0` False: 10 - 3 = 7
    assert score_message("free winner prize urgent cash", True, 0) == 7


def test_known_sender_score_exactly_zero_is_kept():
    # Targets: `score < 0` False at boundary: "free"(2) + 1 link(1) = 3; 3 - 3 = 0
    assert score_message("free", True, 1) == 0


def test_unknown_sender_gets_no_discount():
    # Targets: `if sender_known` False: same message as above, no -3
    assert score_message("free winner prize urgent cash", False, 0) == 10


def test_combined_words_links_and_sender():
    # "FREE!"(2) + "HELLO"(1) + "now"(0) + 2 links(1) = 4; unknown sender
    assert score_message("FREE! HELLO now", False, 2) == 4


# ---------------------------------------------------------------------------
# classify
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "score, expected",
    [
        (0, "clean"),
        (3, "clean"),         # just below suspicious boundary
        (4, "suspicious"),    # suspicious boundary (>= 4)
        (7, "suspicious"),    # just below spam boundary
        (8, "spam"),          # spam boundary (>= 8)
        (100, "spam"),
    ],
)
def test_classify_boundaries(score, expected):
    # Targets: `score >= 8` and `score >= 4` True and False
    assert classify(score) == expected


# ---------------------------------------------------------------------------
# filter_inbox
# ---------------------------------------------------------------------------
def test_filter_inbox_empty_list_returns_zero_counts():
    # Targets: `for ... in messages` with no iterations
    assert filter_inbox([]) == {"spam": 0, "suspicious": 0, "clean": 0}


def test_filter_inbox_counts_each_label():
    # Targets: loop body for spam, suspicious and clean labels
    messages = [
        ("free winner prize urgent cash", False, 4),  # 10 + 4 = 14 -> spam
        ("free winner", False, 0),                    # 2 + 2 = 4  -> suspicious
        ("hello", False, 0),                          # 0          -> clean
        ("hello", True, 0),                           # 0 - 3 -> 0 -> clean
    ]
    assert filter_inbox(messages) == {"spam": 1, "suspicious": 1, "clean": 2}


def test_filter_inbox_known_sender_lowers_label():
    # 4 links (4) + "free winner" (4) = 8 -> spam if unknown, 5 -> suspicious if known
    assert filter_inbox([("free winner", False, 4)]) == {
        "spam": 1, "suspicious": 0, "clean": 0
    }
    assert filter_inbox([("free winner", True, 4)]) == {
        "spam": 0, "suspicious": 1, "clean": 0
    }


# ---------------------------------------------------------------------------
# inbox_status
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "counts, expected",
    [
        ({"spam": 0, "suspicious": 0, "clean": 0}, "empty"),      # total == 0
        ({"spam": 6, "suspicious": 2, "clean": 2}, "flooded"),    # 0.6 > 0.5
        ({"spam": 5, "suspicious": 3, "clean": 2}, "noisy"),      # exactly 0.5: not > 0.5
        ({"spam": 3, "suspicious": 3, "clean": 4}, "noisy"),      # 0.3 > 0.2
        ({"spam": 2, "suspicious": 4, "clean": 4}, "healthy"),    # exactly 0.2: not > 0.2
        ({"spam": 1, "suspicious": 4, "clean": 5}, "healthy"),    # 0.1
        ({"spam": 0, "suspicious": 2, "clean": 3}, "healthy"),    # 0.0
        ({"spam": 3, "suspicious": 0, "clean": 0}, "flooded"),    # 1.0
    ],
)
def test_inbox_status_boundaries(counts, expected):
    # Targets: total == 0, ratio > 0.5, ratio > 0.2 True/False and boundaries
    assert inbox_status(counts) == expected
