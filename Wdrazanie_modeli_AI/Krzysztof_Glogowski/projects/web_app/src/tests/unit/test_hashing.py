from web_app.utils.hash import calculate_hash


def test_calculate_hash():
    # given
    file_content = b"test content"
    expected_hash = "6ae8a75555209fd6c44157c0aed8016e763ff435a19cf186f76863140143ff72"

    # when
    result = calculate_hash(file_content)
    result_2 = calculate_hash(file_content)

    # then
    assert result == expected_hash
    assert result == result_2
