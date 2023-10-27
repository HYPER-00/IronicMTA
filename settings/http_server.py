from typing import TypedDict


class HttpServerSettings(TypedDict):
    http_port: int
    debug_http_port: int
    max_http_connections: int
