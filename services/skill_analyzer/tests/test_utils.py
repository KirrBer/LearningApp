import io
import pickle
import pytest

from skill_analyzer.model_manager import model_manager
from skill_analyzer import utils

# dummy classes for mocking
class DummyEntity:
    def __init__(self, text):
        self.text = text

class DummyDoc:
    def __init__(self, ents):
        self.ents = ents

class DummyExtractorModel:
    def __call__(self, text):
        # return a document with two entities, one containing a newline
        return DummyDoc([DummyEntity("first"), DummyEntity("second\nskill")])

class DummyModel:
    def __init__(self):
        self.device = "cpu"

    def eval(self):
        pass

    def generate(self, **kwargs):
        # always return an object with sequences and scores attributes
        return DummyAnswer()
    
    def compute_transition_scores(self, sequences, scores, normalize_logits=True):
        # return a tensor of log-probabilities for each token in each sequence
        from torch import tensor
        # Return a 2D tensor with shape (batch_size, seq_len)
        # Each sequence should have log-probs for each token
        return tensor([[-0.1, -0.2, -0.3], [-0.15, -0.25, -0.35]])  # batch of 2 sequences

class DummyAnswer:
    def __init__(self):
        # sequences should be a list of token id lists (or similar)
        self.sequences = [[0, 1, 2], [0, 1, 2]]  # Two sequences with 3 tokens each
        self.scores = [[1.0, 1.0], [1.0, 1.0]]  # Scores for each output token

class DummyTokenizer:
    def __call__(self, x, return_tensors=None, padding=None, truncation=None, **kwargs):
        class TensorDict(dict):
            def to(self, device):
                return self

        # return a mapping-like object similar to real tokenizer output
        # Support batch processing
        if isinstance(x, list):
            return TensorDict({"input_ids": [[0, 1, 2] for _ in x]})
        else:
            return TensorDict({"input_ids": [0, 1, 2]})

    def decode(self, x, skip_special_tokens=True):
        # simply return a fixed string so that the normalization step is predictable
        return "normalized"





def test_extract_skills_from_text(monkeypatch):
    # avoid loading real models during the test
    monkeypatch.setattr(model_manager, "load_models", lambda: None)
    monkeypatch.setattr(model_manager, "get_extractor_model", lambda: DummyExtractorModel())
    monkeypatch.setattr(model_manager, "get_normalize_model", lambda: DummyModel())
    monkeypatch.setattr(model_manager, "get_tokenizer", lambda: DummyTokenizer())

    skills = utils.extract_skills_from_text("some resume text")
    assert skills == ["normalized"]


def test_load_models_auto_called(monkeypatch):
    called = False
    def fake_load():
        nonlocal called
        called = True
    monkeypatch.setattr(model_manager, "load_models", fake_load)
    monkeypatch.setattr(model_manager, "get_extractor_model", lambda: DummyExtractorModel())
    monkeypatch.setattr(model_manager, "get_normalize_model", lambda: DummyModel())
    monkeypatch.setattr(model_manager, "get_tokenizer", lambda: DummyTokenizer())

    # call the function; load_models should be invoked internally
    utils.extract_skills_from_text("anything")
    assert called, "load_models was not called automatically"


@pytest.mark.asyncio
async def test_extract_text_from_pdf(monkeypatch):
    # stub the text extractor and pdf converter
    monkeypatch.setattr(utils, "plain_text_output", lambda buf, sort, hyphens: "some text")

    class FakeFile:
        async def read(self):
            return b"fake pdf bytes"

    result = await utils.extract_text_from_pdf(FakeFile())
    assert result == "some text"



@pytest.mark.asyncio
async def test_find_courses(monkeypatch):
    class Skill:
        def __init__(self, name, course):
            self.name = name
            self.course = course

    async def fake_find(skills):
        return [Skill("foo", "bar")]

    monkeypatch.setattr(utils, "find_skills_in_db", fake_find)

    output = await utils.find_courses(["foo", "baz"])
    assert output == [
        {"name": "foo", "course": "bar"},
        {"name": "baz", "course": None},
    ]
