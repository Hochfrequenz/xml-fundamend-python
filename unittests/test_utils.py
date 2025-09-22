import pytest

from fundamend.utils import remove_linebreaks_and_hyphens


@pytest.mark.parametrize(
    "original, expected",
    [
        pytest.param("foo", "foo", id="no change"),
        pytest.param("foo ", "foo", id="trailing whitespace"),
        pytest.param(" foo", "foo", id="leading whitespace"),
        pytest.param(" foo ", "foo", id="trailing and leading whitespaces"),
        pytest.param(" foo\r\n ", "foo", id="trailing and leading whitespaces and line break"),
        # hyphen requirements discussed here:
        # https://github.com/Hochfrequenz/xml-fundamend-python/issues/172#issue-3427724092
        pytest.param(" Foo-\r\nbar ", "Foobar", id="hyphen with line break"),
        pytest.param(" Foo\r\n and bar ", "Foo and bar", id="line break w/o hyphen"),
    ],
)
def test_anwendungsfall_beschreibung_normalization(original: str, expected: str) -> None:
    actual = remove_linebreaks_and_hyphens(original)
    assert actual == expected
