from unittest import mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.engine import engine
from app.database.session import get_db_session


def test_engine_initialization():
    assert engine.url.drivername == "postgresql+asyncpg"
    # Verify pool size configuration
    assert engine.pool.size() == 10


@pytest.mark.asyncio
async def test_get_db_session_success():
    # Setup mock session and session maker context manager
    mock_session = mock.AsyncMock(spec=AsyncSession)
    mock_session_maker = mock.MagicMock()
    mock_session_maker.return_value.__aenter__ = mock.AsyncMock(
        return_value=mock_session
    )
    mock_session_maker.return_value.__aexit__ = mock.AsyncMock(return_value=None)

    with mock.patch("app.database.session.async_session_maker", mock_session_maker):
        session_gen = get_db_session()
        # Retrieve the session from the generator
        retrieved_session = await anext(session_gen)

        assert retrieved_session == mock_session

        # Simulate generator exiting successfully
        try:
            await anext(session_gen)
        except StopAsyncIteration:
            pass

        # Verify commit and close were called on the mock session
        mock_session.commit.assert_awaited_once()
        mock_session.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_db_session_exception():
    mock_session = mock.AsyncMock(spec=AsyncSession)
    mock_session_maker = mock.MagicMock()
    mock_session_maker.return_value.__aenter__ = mock.AsyncMock(
        return_value=mock_session
    )
    mock_session_maker.return_value.__aexit__ = mock.AsyncMock(return_value=None)

    with mock.patch("app.database.session.async_session_maker", mock_session_maker):
        session_gen = get_db_session()
        retrieved_session = await anext(session_gen)
        assert retrieved_session == mock_session

        # Simulate an exception at the yield point using athrow
        with pytest.raises(ValueError, match="Database error"):
            await session_gen.athrow(ValueError("Database error"))

        # Verify rollback and close were called
        mock_session.rollback.assert_awaited_once()
        mock_session.close.assert_awaited_once()
