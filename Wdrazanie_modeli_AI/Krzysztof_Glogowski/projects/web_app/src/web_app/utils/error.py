from abc import ABC


class APIError(Exception, ABC):
    pass


class PretrainedEncoderNotFoundError(APIError):
    def __init__(self, encoder_name: str):
        self._msg = f"Unable to find pretrained encoder {encoder_name=} unavailable."
        super().__init__(self._msg)


class DocumentClusteringModelNotFoundError(APIError):
    def __init__(self, path: str):
        self._msg = f"Unable to find Document Clustering model in {path=} location."
        super().__init__(self._msg)


class ValkeyConnectionError(APIError):
    def __init__(self, host: str, port: int):
        self._msg = f"Unable to connect to Valkey database on {host=}, {port=}."
        super().__init__(self._msg)


class ValkeyConnectionNotAliveError(APIError):
    def __init__(self, host: str, port: int):
        self._msg = f"Connection to Valkey is not alive on {host=}, {port=}."
        super().__init__(self._msg)


class ClamavConnectionError(APIError):
    def __init__(self, socket_host: str, socket_port: int):
        self._msg = f"Unable to connect to ClamAV {socket_host=}, {socket_port=}."
        super().__init__(self._msg)


class ClamavConnectionNotAliveError(APIError):
    def __init__(self, socket_host: str, socket_port: int):
        self._msg = f"Connection to ClamAV is not alive on {socket_host=}, {socket_port=}."
        super().__init__(self._msg)
