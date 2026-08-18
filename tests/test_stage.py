import pytest

from src.stage import Stage

def test_invalid_probability():
    with pytest.raises(ValueError):
        Stage("stage_1", 1.5)