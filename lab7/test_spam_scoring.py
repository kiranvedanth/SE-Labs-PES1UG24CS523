import re

from hypothesis import given, example, strategies as st

from spam_scoring import sender_domain, first_link, shout_ratio


# ---------- sender_domain ----------

@given(st.text() | st.none())
def test_sender_domain_no_crash(s):
    sender_domain(s)


@given(st.text() | st.none())
def test_sender_domain_result_is_clean(s):
    result = sender_domain(s)
    if result is not None:
        assert result != ""
        assert "@" not in result
        assert result == result.strip()


@given(st.text(min_size=1, alphabet=st.characters(blacklist_characters="@"))
       .filter(lambda d: d.strip() != ""))
def test_sender_domain_extracts_domain(d):
    assert sender_domain("user@" + d) == d.strip().lower()


@example("offers@Deals.com")
@example("a@b@c.com")
@example("no-at-sign")
@example("trailing@")
@example("")
@given(st.text())
def test_sender_domain_examples(s):
    sender_domain(s)


def test_sender_domain_known_values():
    assert sender_domain("offers@Deals.com") == "deals.com"
    assert sender_domain("a@b@c.com") == "c.com"
    assert sender_domain("no-at-sign") is None
    assert sender_domain("trailing@") is None
    assert sender_domain(None) is None


# ---------- first_link ----------

@given(st.text() | st.none())
def test_first_link_no_crash(s):
    first_link(s)


@given(st.text() | st.none())
def test_first_link_result_is_link(s):
    result = first_link(s)
    if result is not None:
        assert re.fullmatch(r'https?://\S+', result, re.IGNORECASE)


@given(st.text().filter(lambda t: "http" not in t.lower()))
def test_first_link_none_without_http(t):
    assert first_link(t) is None


def test_first_link_known_values():
    assert first_link("visit https://example.com now") == "https://example.com"
    assert first_link("see http://a.com and https://b.com") == "http://a.com"
    assert first_link("line one\nhttps://x.org\nline three") == "https://x.org"
    assert first_link("no links here") is None
    assert first_link("") is None
    assert first_link(None) is None


# ---------- shout_ratio ----------

@given(st.text() | st.none())
def test_shout_ratio_no_crash(s):
    shout_ratio(s)


@given(st.text() | st.none())
def test_shout_ratio_in_range(s):
    result = shout_ratio(s)
    if result is not None:
        assert 0.0 <= result <= 1.0


@given(st.text(min_size=1, alphabet=st.characters(whitelist_categories=("Lu",))))
def test_shout_ratio_all_uppercase_is_one(s):
    assert shout_ratio(s) == 1.0


def test_shout_ratio_known_values():
    assert shout_ratio("FREE PRIZE NOW") == 1.0
    assert shout_ratio("free prize now") == 0.0
    assert shout_ratio("Hello") == 0.2
    assert shout_ratio("") is None
    assert shout_ratio("12345 !!!") is None
    assert shout_ratio(None) is None
