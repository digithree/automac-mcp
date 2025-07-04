# MCP OSer - Claude Code Development Guide

## Project Overview

MCP OSer is a Model Context Protocol (MCP) server for macOS UI automation. It provides Claude Code with tools to programmatically control the local macOS UI through input actions and screen comprehension.

## Core Architecture

### Technology Stack
- **Python** with **uv** dependency management
- **FastMCP** framework for MCP server implementation
- **pyautogui** for input control and screenshots
- **pyobjc** for native macOS integration (AppKit, Quartz)
- **osascript** for AppleScript execution
- **easyocr** for optical character recognition

### MCP Server Design
- All functionality exposed as **Tools** (not Resources) since Claude Code automatically invokes tools but not resources
- **Input Control Tools**: `click`, `type_text`, `scroll`, `keyboard_shortcut`
- **UI Comprehension Tools**: `get_screen_layout`, `get_screen_text`, `focus_app`, `get_available_apps`
- Handles JSON-RPC communication and MCP protocol compliance automatically

## Development Best Practices

### Testing Philosophy
- All features must be tested with real macOS UI interactions
- Test each MCP tool individually before integration
- Verify accessibility permissions are properly configured
- Create test scripts that launch actual applications and verify UI changes

### Security & Safety
- Leverage Claude Desktop's command confirmation prompts for safety
- Validate all input parameters to prevent unintended system actions
- Handle accessibility permission errors gracefully with helpful messages
- Never expose or log sensitive information from screen captures

### macOS Integration Guidelines
- **Accessibility Requirements**: Requires both Accessibility and Screen Recording permissions
- **Optimization**: Recommend enabling "Increase contrast" in System Settings for better OCR accuracy
- **Native APIs**: Prefer macOS Accessibility APIs over generic automation tools when possible
- **Error Handling**: Provide clear error messages when permissions are missing

### Code Architecture Principles
- Separate MCP server framework code from UI automation logic
- Modularize input control functions from UI comprehension functions
- Use comprehensive error handling for all system-level operations
- Maintain clean separation between AppleScript, Python automation, and OCR components

## Development Environment Setup

### Dependency Management
- Uses **uv** for fast, reliable dependency management
- Always run `uv sync` before development
- Update `pyproject.toml` when adding dependencies to ensure consistency

### Development Commands
```bash
# Install dependencies
uv sync

# Test server with MCP Inspector (for debugging)
uv run --with fastmcp fastmcp dev mcp_oser.py

# Run server for Claude Desktop integration
uv run python mcp_oser.py
```

### Claude Desktop Configuration
**Recommended Configuration** (most reliable):
```json
{
  "mcpServers": {
    "mcp-oser": {
      "command": "/absolute/path/to/mcp-oser/.venv/bin/python", 
      "args": ["/absolute/path/to/mcp-oser/mcp_oser.py"]
    }
  }
}
```

**Important Configuration Notes**:
- Use absolute paths to avoid path resolution issues
- Direct virtual environment path is more reliable than `uv run`
- Manual configuration preferred over `fastmcp install` due to uv compatibility
- Restart Claude Desktop after configuration changes

## Claude Code Specific Behaviors

### Tool vs Resource Design Decisions
- **Use Tools Only**: Claude Code automatically invokes tools but ignores resources
- **Avoid Resource Decorators**: Don't use `@mcp.resource()` as Claude Desktop doesn't auto-invoke them
- **Tool Parameter Validation**: All tool parameters should have clear types and descriptions

### Error Handling for Claude Code
- Provide specific, actionable error messages
- Include permission setup instructions in error responses  
- Return structured error information that Claude Code can interpret and act upon
- Handle timeout scenarios gracefully with clear status messages

### Testing Strategy for Claude Code Integration
- Test each tool individually through Claude Desktop
- Verify error messages are helpful and actionable
- Test permission scenarios and error recovery
- Create realistic test scenarios that match typical Claude Code usage patterns