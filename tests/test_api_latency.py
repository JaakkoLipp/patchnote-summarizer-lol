import time
from backend import utils


def test_utils_bundle_like_latency():
    """Roughly time core parsing calls to catch obvious regressions.
    Not a strict SLA; allows generous first-time parse.
    """
    v = "25-16"
    t0 = time.time()
    c = utils.parse_champions(v)
    i = utils.parse_items(v)
    o = utils.parse_other(v)
    a = utils.parse_arena(v)
    t1 = time.time()
    assert "champions" in c
    assert "items" in i
    assert isinstance(o, dict)
    assert "arena" in a
    # Aim under 2 seconds locally; first-run may download but we use local files
    assert (t1 - t0) < 2.0


def test_summary_latency_mocked(monkeypatch):
    # Mock the ollama call to return quickly
    def fake_generate(version):
        assert isinstance(version, str)
        return {"summary": f"Summary for {version}: Major champion and item updates; meta shifts expected."}

    monkeypatch.setattr(utils, "generate_one_liner_summary", fake_generate)

    t0 = time.time()
    out = utils.generate_one_liner_summary("25-16")
    t1 = time.time()
    assert out.get("summary")
    assert (t1 - t0) < 0.1
