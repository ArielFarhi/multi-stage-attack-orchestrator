import pytest

from src.stage import Stage

def test_invalid_probability():
    with pytest.raises(ValueError):
        Stage("stage_1", 1.5)


def test_empty_name_is_invalid():
    with pytest.raises(ValueError):
        Stage("", 0.5)


def test_stage_with_probability_one_always_succeeds():
    assert Stage("stage", 1.0).run() is True


def test_stage_with_probability_zero_always_fails():
    assert Stage("stage", 0.0).run() is False
