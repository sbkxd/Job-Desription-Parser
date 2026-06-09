from unittest import mock

import pytest
from fastapi import Request

from app.logging.logger import get_logger
from app.logging.middleware import LoggingMiddleware


def test_get_logger():
    logger = get_logger("test_logger")
    assert hasattr(logger, "info")
    assert hasattr(logger, "error")


@pytest.mark.asyncio
async def test_logging_middleware_success():
    # Setup mock request and response
    mock_request = mock.Mock(spec=Request)
    mock_request.method = "GET"
    mock_request.url = mock.Mock()
    mock_request.url.path = "/test-path"
    mock_request.query_params = {}
    mock_request.headers = {}

    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.headers = {}

    async def mock_call_next(req):
        return mock_response

    middleware = LoggingMiddleware(app=None)

    with mock.patch("app.logging.middleware.logger") as mock_logger:
        res = await middleware.dispatch(mock_request, mock_call_next)

        # Verify status code and header
        assert res.status_code == 200
        assert "X-Request-ID" in res.headers

        # Verify log statements were called
        assert mock_logger.info.call_count >= 2


@pytest.mark.asyncio
async def test_logging_middleware_failure():
    mock_request = mock.Mock(spec=Request)
    mock_request.method = "POST"
    mock_request.url = mock.Mock()
    mock_request.url.path = "/fail-path"
    mock_request.query_params = {}
    mock_request.headers = {"X-Request-ID": "custom-id-123"}

    async def mock_call_next(req):
        raise ValueError("Something went wrong")

    middleware = LoggingMiddleware(app=None)

    with mock.patch("app.logging.middleware.logger") as mock_logger:
        with pytest.raises(ValueError, match="Something went wrong"):
            await middleware.dispatch(mock_request, mock_call_next)

        assert mock_logger.error.called
        # Verify it logged with exc_info=True
        args, kwargs = mock_logger.error.call_args
        assert kwargs.get("exc_info") is True
