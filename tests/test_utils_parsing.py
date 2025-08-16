from backend import utils


def test_parse_items_has_data_for_known_patch():
    # Use an existing local HTML file
    version = "25-16"
    data = utils.parse_items(version)
    assert isinstance(data, dict)
    assert "items" in data
    # can't guarantee exact content, but should be a dict
    assert isinstance(data["items"], dict)


def test_parse_champions_returns_dict():
    version = "25-16"
    data = utils.parse_champions(version)
    assert isinstance(data, dict)
    assert "champions" in data


def test_parse_other_is_stable():
    version = "25-16"
    data = utils.parse_other(version)
    assert isinstance(data, dict)


def test_tagline_parsed_or_fallback():
    version = "25-16"
    tag = utils.parse_tagline(version)
    assert "tagline" in tag
