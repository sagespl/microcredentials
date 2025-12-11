import logging
from io import BufferedIOBase

from fastapi.exceptions import RequestValidationError

from common.input_file_validator import InputFileValidator


class UploadFileValidator:
    def __init__(self):
        self.validator = InputFileValidator()

    def validate(self, upload_file: BufferedIOBase) -> None:
        errors = self.validator.validate(upload_file)
        if len(errors) > 0:
            raise RequestValidationError(errors)
        logging.info("Upload file validation completed successfully.")
