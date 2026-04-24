"""Tests for frontapp_mcp package structure and imports."""


def test_package_import():
    """Test that the main package can be imported."""
    import frontapp_mcp

    # Version is dynamically updated by semantic-release, just check format
    assert frontapp_mcp.__version__  # Not empty
    assert "." in frontapp_mcp.__version__  # Has version separators


def test_submodule_imports():
    """Test that submodules can be imported."""
    from frontapp_mcp import prompts, resources, tools

    assert tools is not None
    assert resources is not None
    assert prompts is not None


def test_package_metadata():
    """Test that package metadata is available."""
    import frontapp_mcp

    assert hasattr(frontapp_mcp, "__version__")
    assert isinstance(frontapp_mcp.__version__, str)
    assert len(frontapp_mcp.__version__) > 0


def test_tool_module_imports():
    """Verify all tool modules import without errors."""
    from frontapp_mcp.tools import conversations

    assert conversations is not None


def test_package_docstring():
    """Test that the package has documentation."""
    import frontapp_mcp

    assert frontapp_mcp.__doc__ is not None
    assert "MCP Server" in frontapp_mcp.__doc__ or "MCP server" in frontapp_mcp.__doc__
    assert "Frontapp" in frontapp_mcp.__doc__
