import os
import tempfile

import torch
from torch.jit import ScriptModule

from tests.fixture import (
    fake_script_model,
    model_prediction_v1,
    model_prediction_v2,
    model_in_in_memory_filesystem,
)
from web_app.model.document_classifier import DocumentClassifier

# to prevent IDE from removing unused imports START
fake_script_model
model_in_in_memory_filesystem
model_prediction_v1
model_prediction_v2
# to prevent IDE from removing unused imports END


def test_from_path():
    # given
    fd, model_path = tempfile.mkstemp(suffix=".pt")
    os.close(fd)

    try:
        scripted_model = torch.jit.script(torch.nn.Linear(2, 2))
        scripted_model.save(model_path)
        classifier = DocumentClassifier.from_path(model_path)

        assert classifier is not None
        assert isinstance(classifier, DocumentClassifier)
        assert classifier.model is not None
        assert isinstance(classifier.model, ScriptModule)

    finally:
        os.remove(model_path)


def test_classify(model_in_in_memory_filesystem, model_prediction_v1, mocker):
    # given
    image = torch.ones((1, 3, 224, 224))
    length = torch.tensor([1])
    expected_prediction = model_prediction_v1

    # when
    classifier = DocumentClassifier.from_path("memory://model.pt")
    predict_spy = mocker.spy(classifier.model, "forward")
    prediction = classifier.classify(image, length)

    # then
    assert prediction is not None
    assert prediction == expected_prediction
    assert predict_spy.call_count == 1
    assert predict_spy.call_args.args[0].equal(image)
    assert predict_spy.call_args.args[1].equal(length)


def test_classify_proba(model_in_in_memory_filesystem, model_prediction_v2, mocker):
    # given
    image = torch.ones((1, 3, 224, 224))
    length = torch.tensor([1])
    expected_prediction = model_prediction_v2

    # when
    classifier = DocumentClassifier.from_path("memory://model.pt")
    predict_proba_spy = mocker.spy(classifier.model, "predict_proba")
    prediction = classifier.classify_proba(image, length)

    # then
    assert prediction is not None
    assert prediction == expected_prediction
    assert predict_proba_spy.call_count == 1
    assert predict_proba_spy.call_args.args[0].equal(image)
    assert predict_proba_spy.call_args.args[1].equal(length)
