import requests

from tests.fixture import (
    model_prediction_v1,
    request_body,
    invalid_request_body,
    one_page_document_content,
)
from tests.system.fixture import docker, request_endpoint_v1
from tests.utils_test import assert_positive_response

# to prevent IDE from removing unused imports START
one_page_document_content
# to prevent IDE from removing unused imports END


def test_classify_v1(docker, request_endpoint_v1, request_body, model_prediction_v1):
    first_response = requests.post(request_endpoint_v1, files=request_body)
    assert_positive_response(first_response, model_prediction_v1)

    second_response = requests.post(request_endpoint_v1, files=request_body)
    assert_positive_response(second_response, model_prediction_v1, from_cache=True)


def test_received_422_when_at_least_one_body_param_is_invalid(
    docker, request_endpoint_v1, invalid_request_body
):
    # when
    response = requests.post(request_endpoint_v1, files=invalid_request_body)

    # then
    assert response.status_code == 422
    assert response.headers.get("content-type") == "application/json"
