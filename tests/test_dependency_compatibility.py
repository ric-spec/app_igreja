from pathlib import Path


def test_requirements_pin_starlette_compatibility():
    requirements = Path("requirements.txt").read_text(encoding="utf-8")
    assert "starlette<0.47" in requirements
