import pytest

from src.stage import Stage

def test_invalid_probability():
    with pytest.raises(ValueError):
        Stage("stage_1", 1.5)


def test_empty_name_is_invalid():
    with pytest.raises(ValueError):
        Stage("", 0.5)
