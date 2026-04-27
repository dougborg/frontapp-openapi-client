"""Shared pytest fixtures for MCP server tests."""

import os
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def frontapp_context():
    """Context fixture backed by a real FrontappClient for integration tests.

    Skipped when FRONTAPP_API_KEY is not set.
    """
    api_key = os.getenv("FRONTAPP_API_KEY")
    if not api_key:
        pytest.skip("FRONTAPP_API_KEY not set - skipping integration test")

    try:
        from frontapp_public_api_client import FrontappClient
    except ImportError:
        pytest.skip("frontapp_public_api_client not installed")

    context = MagicMock()
    mock_request_context = MagicMock()
    mock_lifespan_context = MagicMock()

    base_url = os.getenv("FRONTAPP_BASE_URL", "https://api2.frontapp.com")
    client = FrontappClient(
        api_key=api_key,
        base_url=base_url,
        timeout=30.0,
        max_retries=3,
        max_pages=10,
    )

    mock_lifespan_context.client = client
    mock_request_context.lifespan_context = mock_lifespan_context
    context.request_context = mock_request_context

    yield context


def create_mock_context(
    elicit_confirm: bool = True, *, elicit_action: str | None = None
):
    """Build a mock FastMCP context for unit tests.

    The three values of ``ConfirmationResult`` map to elicit-result shape:

    - CONFIRMED: ``action='accept'`` + ``data.confirm=True``
    - DECLINED:  ``action='accept'`` + ``data.confirm=False``
    - CANCELLED: ``action != 'accept'`` (typically ``'decline'``)

    Args:
        elicit_confirm: If True, the elicitation models user-confirmation
            (CONFIRMED). If False, by default the elicitation is cancelled
            (action='decline' → CANCELLED) — that's the historical
            behavior.
        elicit_action: Override the ``action`` field explicitly. Pass
            ``'accept'`` together with ``elicit_confirm=False`` to
            exercise the DECLINED branch (where the elicitation succeeds
            but the user un-checks the confirm flag).

    Returns:
        Tuple of (context, lifespan_context).
    """
    if elicit_action is None:
        elicit_action = "accept" if elicit_confirm else "decline"

    context = MagicMock()
    mock_request_context = MagicMock()
    mock_lifespan_context = MagicMock()
    context.request_context = mock_request_context
    mock_request_context.lifespan_context = mock_lifespan_context

    mock_elicit_result = MagicMock()
    mock_elicit_result.action = elicit_action
    if elicit_action == "accept":
        mock_elicit_result.data = MagicMock()
        mock_elicit_result.data.confirm = elicit_confirm
    else:
        mock_elicit_result.data = None

    context.elicit = AsyncMock(return_value=mock_elicit_result)

    return context, mock_lifespan_context


@pytest.fixture
def mock_context():
    """Mock FastMCP context fixture."""
    return create_mock_context()


@pytest.fixture
def mcp_tool_capture():
    """Factory: register a tools module against a fake FastMCP and return
    the captured ``{name: callable}`` dict.

    New tool test files should use this fixture. Existing per-vertical
    test files (test_contacts_tools, test_drafts_tools, test_messages_tools,
    test_tags_tools, test_inboxes_tools) still define their own copy of
    the same pattern — migration is tracked as follow-up cleanup so this
    PR doesn't churn 5 working test files.
    """

    def factory(register_tools_fn) -> dict[str, object]:
        captured: dict[str, object] = {}

        class FakeMCP:
            def tool(self, **kwargs: object):
                name = kwargs["name"]

                def decorator(fn):
                    captured[name] = fn
                    return fn

                return decorator

        register_tools_fn(FakeMCP())
        return captured

    return factory
