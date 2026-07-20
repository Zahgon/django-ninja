
from typing import Any, Dict

import django
from django.http import HttpResponse, StreamingHttpResponse

ASYNC_STREAMING = django.VERSION >= (4, 2)


def _copy_temporal_headers(
    temporal_response: HttpResponse, response: StreamingHttpResponse
) -> None:
    """Copy headers and cookies from temporal response, skipping Content-Type."""
    for key, value in temporal_response.items():
        if key.lower() != "content-type":
            response[key] = value
    for cookie_name, cookie in temporal_response.cookies.items():
        response.cookies[cookie_name] = cookie


if ASYNC_STREAMING:

    async def create_streaming_response(
        content_gen: Any,
        *,
        content_type: str,
        status: int,
        temporal_response: HttpResponse,
        extra_headers: Dict[str, str],
    ) -> StreamingHttpResponse:
        """Create a StreamingHttpResponse from an async content generator.

        Django 4.2+: passes the async generator directly and copies
        temporal response headers/cookies lazily after the generator is exhausted.
        """

        async def with_lazy_headers() -> Any:
            async for chunk in content_gen:
                yield chunk
            _copy_temporal_headers(temporal_response, response)

        response = StreamingHttpResponse(
            with_lazy_headers(),
            content_type=content_type,
            status=status,
        )
        for key, value in extra_headers.items():
            response[key] = value
        return response

else:

    async def create_streaming_response(
        content_gen: Any,
        *,
        content_type: str,
        status: int,
        temporal_response: HttpResponse,
        extra_headers: Dict[str, str],
    ) -> StreamingHttpResponse:
        """Create a StreamingHttpResponse from an async content generator.

        Django < 4.2: eagerly consumes the async generator into a list
        since StreamingHttpResponse does not support async iterators.
        """
        chunks = []
        async for chunk in content_gen:
            chunks.append(chunk)
        response = StreamingHttpResponse(
            iter(chunks),
            content_type=content_type,
            status=status,
        )
        _copy_temporal_headers(temporal_response, response)
        for key, value in extra_headers.items():
            response[key] = value
        return response
