def assert_positive_response(response, expected_prediction, from_cache: bool = False):
    assert response.status_code == 200
    assert response.headers.get("content-type") == "application/json"
    assert response.headers.get("X-Readed-From-Cache") == str(from_cache).lower()
    response_json = response.json()
    assert "prediction" in response_json
    assert response_json["prediction"] is not None
    assert response_json["prediction"] == expected_prediction
