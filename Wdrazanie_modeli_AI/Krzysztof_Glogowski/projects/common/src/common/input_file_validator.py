from io import BufferedIOBase

from magic import Magic


class InputFileValidator:
    def __init__(self):
        self.supported_content_types = [
            "application/pdf",
        ]
        self.max_file_size = 2 * 1024 * 1024  # 2 MB

    def validate(self, file_obj: BufferedIOBase) -> list[str]:
        errors: list[str] = []
        self._validate_content_type(file_obj, errors)
        self._validate_size(file_obj, errors)
        return errors

    def _validate_content_type(self, file_obj: BufferedIOBase, error_collector: list[str]) -> None:
        sample = file_obj.read(2048)
        file_obj.seek(0)
        mime = Magic(mime=True)
        content_type = mime.from_buffer(sample)
        if content_type not in self.supported_content_types:
            error_collector.append(f"Unsupported content type: {content_type}")

    def _validate_size(self, file_obj, error_collector: list[str]):
        file_obj.seek(0, 2)
        size = file_obj.tell()
        file_obj.seek(0)
        if size <= 0:
            error_collector.append("File size must be greater than 0")
        elif size > self.max_file_size:
            error_collector.append(
                f"File size exceeds the maximum limit of {self.max_file_size} bytes"
            )
