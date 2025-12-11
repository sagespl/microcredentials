from tests.fixture import one_page_document_content, two_pages_document_content
from web_app.service.mapper.document_mapper import to_model_input


def test_to_model_input_for_one_page_document(one_page_document_content):
    # given
    expected_length = 1
    expected_shape = (1, 3, 224, 224)

    # when
    images, length = to_model_input(one_page_document_content)

    # then
    assert length.item() == expected_length
    assert images.shape == expected_shape


def test_to_model_input_for_two_page_document(two_pages_document_content):
    # given
    expected_length = 2
    expected_shape = (2, 3, 224, 224)

    # when
    images, length = to_model_input(two_pages_document_content)

    # then
    assert length.item() == expected_length
    assert images.shape == expected_shape
