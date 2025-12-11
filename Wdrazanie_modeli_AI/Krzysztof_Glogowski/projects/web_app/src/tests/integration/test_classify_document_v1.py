import pytest

from tests.fixture import (
    fake_antivirus_socket_for_non_malformed_files,
    fake_valkey,
    one_page_document_content,
    fake_script_model,
    model_prediction_v1,
    request_body,
    invalid_request_body,
    request_headers,
    model_in_in_memory_filesystem,
)
from tests.integration.fixture import (
    document_hash_v1,
    initialized_app,
    request_endpoint_v1,
    in_memory_model_path,
)
from tests.utils_test import assert_positive_response
from web_app.antivirus.clamav.scanner import AntivirusScanner
from web_app.database.valkey.client import ValkeyClient
from web_app.model.document_classifier import DocumentClassifier
from web_app.service.validator.upload_file_validator import UploadFileValidator
from web_app.utils.error import APIError

# to prevent IDE from removing unused imports START
one_page_document_content
fake_valkey
fake_antivirus_socket_for_non_malformed_files
fake_script_model
model_in_in_memory_filesystem
in_memory_model_path
model_prediction_v1
# to prevent IDE from removing unused imports END


def test_document_classified_correctly(
    initialized_app,
    request_body,
    request_headers,
    request_endpoint_v1,
    document_hash_v1,
    model_prediction_v1,
    mocker,
):
    redis_read_spy = mocker.spy(ValkeyClient, "read")
    redis_write_spy = mocker.spy(ValkeyClient, "write")
    validator_spy = mocker.spy(UploadFileValidator, "validate")
    antivirus_spy = mocker.spy(AntivirusScanner, "scan")
    predict_spy = mocker.spy(DocumentClassifier, "classify")

    # first request
    first_response = initialized_app.post(
        url=request_endpoint_v1, headers=request_headers, files=request_body
    )
    assert_positive_response(first_response, model_prediction_v1)

    assert redis_read_spy.called is True
    assert redis_read_spy.call_count == 1
    assert redis_read_spy.call_args.args[1] == document_hash_v1
    assert redis_read_spy.spy_return is None

    assert redis_write_spy.called is True
    assert redis_write_spy.call_count == 1
    assert redis_write_spy.call_args.args[1] == document_hash_v1
    assert redis_write_spy.call_args.args[2] == model_prediction_v1

    assert validator_spy.called is True
    assert validator_spy.call_count == 1

    assert antivirus_spy.called is True
    assert antivirus_spy.call_count == 1

    assert predict_spy.called is True
    assert predict_spy.call_count == 1

    # second request - predictions read from cache
    second_response = initialized_app.post(
        url=request_endpoint_v1, headers=request_headers, files=request_body
    )
    assert_positive_response(second_response, model_prediction_v1, from_cache=True)

    assert predict_spy.call_count == 1
    assert redis_write_spy.call_count == 1
    assert redis_read_spy.call_count == 2
    assert validator_spy.call_count == 2
    assert antivirus_spy.call_count == 2


@pytest.mark.parametrize("error", [Exception, APIError])
def test_receive_500_when_error_raised_in_api(
    initialized_app, request_body, request_headers, request_endpoint_v1, error, mocker
):
    # given
    mocker.patch.object(DocumentClassifier, "classify", side_effect=error)

    # when
    response = initialized_app.post(
        url=request_endpoint_v1, headers=request_headers, files=request_body
    )

    # then
    assert response.status_code == 500
    assert response.headers.get("content-type") == "application/json"
    response_json = response.json()
    assert "message" in response_json
    assert response_json["message"] is not None
    assert isinstance(response_json["message"], str)
    assert response_json["message"] == "Internal server error"


def test_received_422_when_at_least_one_body_param_is_invalid(
    initialized_app,
    invalid_request_body,
    request_headers,
    request_endpoint_v1,
):
    # when
    response = initialized_app.post(
        url=request_endpoint_v1, headers=request_headers, files=invalid_request_body
    )

    # then
    assert response.status_code == 422
    assert response.headers.get("content-type") == "application/json"
