"""Tests for MCP tool annotations.

Every mutation tool (one that takes a ``confirm:`` parameter) must carry
the ``destructiveHint`` annotation so spec-compliant clients prompt the
user before invoking. Read-only tools must not carry that hint.

This is the contract documented in ADR-0016 (post-elicit) and the
``DESTRUCTIVE`` constant in ``frontapp_mcp.tools.schemas``.
"""

from __future__ import annotations

import inspect

import pytest
from fastmcp import FastMCP
from frontapp_mcp.tools import register_all_tools


@pytest.fixture
def registered_tools():
    """Return the live tool registry after ``register_all_tools`` has run."""
    mcp = FastMCP("annotation-test")
    register_all_tools(mcp)
    return mcp


def _is_mutation(fn) -> bool:
    """A tool is a mutation iff its callable takes a ``confirm`` parameter."""
    return "confirm" in inspect.signature(fn).parameters


async def test_every_mutation_tool_carries_destructive_hint(registered_tools):
    tools = await registered_tools.list_tools()
    mutations: list[str] = []
    missing: list[str] = []
    for tool in tools:
        if not _is_mutation(tool.fn):
            continue
        mutations.append(tool.name)
        ann = tool.annotations
        if ann is None or ann.destructiveHint is not True:
            missing.append(tool.name)
    assert mutations, "Expected at least one mutation tool to be discovered"
    assert not missing, (
        f"{len(missing)} mutation tool(s) missing destructiveHint=True: {missing}"
    )


async def test_read_tools_do_not_set_destructive_hint(registered_tools):
    tools = await registered_tools.list_tools()
    reads: list[str] = []
    misannotated: list[str] = []
    for tool in tools:
        if _is_mutation(tool.fn):
            continue
        reads.append(tool.name)
        ann = tool.annotations
        if ann is not None and ann.destructiveHint is True:
            misannotated.append(tool.name)
    assert reads, "Expected at least one read tool to be discovered"
    assert not misannotated, (
        f"Read tool(s) incorrectly annotated as destructive: {misannotated}"
    )
