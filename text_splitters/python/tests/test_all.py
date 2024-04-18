import pytest
import indexify_text_splitters


def test_sum_as_string():
    assert indexify_text_splitters.sum_as_string(1, 1) == "2"
