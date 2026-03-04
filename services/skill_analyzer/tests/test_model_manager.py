import pytest

from skill_analyzer import model_manager


def test_singleton():
    a = model_manager.ModelManager()
    b = model_manager.ModelManager()
    assert a is b


def test_unload_models():
    mm = model_manager.ModelManager()
    mm._extractor_model = object()
    mm._normalize_model = object()
    mm._tokenizer = object()
    # call the method under test
    mm.unload_models()

    assert mm._extractor_model is None
    assert mm._normalize_model is None
    assert mm._tokenizer is None
