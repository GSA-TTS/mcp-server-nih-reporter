# Python MCP Server Implementation Guide

## Overview

This document provides Python-specific best practices and examples for implementing MCP servers using the MCP Python SDK. It covers server setup, tool registration patterns, input validation with Pydantic, error handling, and complete working examples.

---

## Quick Reference

### Key Imports
```python
from fastmcp import FastMCP
from pydantic import Field
from typing import Annotated, Optional, List, Dict, Any
from enum import Enum
import httpx
```

### Server Initialization
```python
mcp = FastMCP("service_mcp", instructions="...")
```

### Tool Registration Pattern
```python
@mcp.tool(name="tool_name", annotations={...})
async def tool_function(
    param1: Annotated[str, Field(description="...", min_length=1)],
    param2: Annotated[int, Field(description="...", ge=0)] = 0,
) -> str:
    # Implementation
    pass
```

> **FastMCP 3.x**: Use flat `Annotated[type, Field(...)]` parameters directly in the function
> signature — **not** a single `params: SomeModel` argument. FastMCP 3.x treats a Pydantic
> model parameter literally (requiring callers to pass `{"params": {...}}`), which breaks
> LLM tool use. Inline `Annotated` fields produce the flat JSON schema LLMs expect.

---

## MCP Python SDK and FastMCP

The official MCP Python SDK provides FastMCP, a high-level framework for building MCP servers. It provides:
- Automatic description and inputSchema generation from function signatures and docstrings
- Pydantic model integration for input validation
- Decorator-based tool registration with `@mcp.tool`

**For complete SDK documentation, use WebFetch to load:**
`https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md`

## Server Naming Convention

Python MCP servers must follow this naming pattern:
- **Format**: `{service}_mcp` (lowercase with underscores)
- **Examples**: `github_mcp`, `jira_mcp`, `stripe_mcp`

The name should be:
- General (not tied to specific features)
- Descriptive of the service/API being integrated
- Easy to infer from the task description
- Without version numbers or dates

## app.py Structure

`app.py` is the single file that owns server initialization and transport. Keep it thin — no
tool logic lives here.

```python
import os

from dotenv import load_dotenv
from fastmcp import FastMCP

from <servername>.tools import register_tools

load_dotenv()  # loads .env before any code reads API keys

mcp = FastMCP(
    "<service>_mcp",
    instructions=(
        "One paragraph: what this server is for and what API it wraps.\n\n"
        "TOOL SELECTION GUIDE:\n"
        "- Natural-language use case → tool_name\n"
        "- Another use case → other_tool_name\n\n"
        "Any important conventions (date formats, ID formats, pagination, rate limits).\n\n"
        "AUTHENTICATION: Requires SERVICE_API_KEY environment variable."
    ),
)

register_tools(mcp)

if __name__ == "__main__":
    # Dual-transport: HTTP when a platform port env var is set (Databricks Apps, Cloud Run,
    # etc.), stdio otherwise (Claude Desktop, Claude Code, local MCP clients).
    port_env = os.getenv("DATABRICKS_APP_PORT") or os.getenv("PORT")
    if port_env:
        mcp.run(transport="http", host="0.0.0.0", port=int(port_env))
    else:
        mcp.run(transport="stdio")
```

**`instructions` guidelines:**
- Lead with one sentence on what the server wraps and why an LLM would use it
- Include a `TOOL SELECTION GUIDE` mapping natural-language tasks to tool names — this is the
  highest-value content since it steers the LLM to the right tool without trial and error
- Document any domain conventions the LLM needs to call tools correctly (fiscal year
  definitions, ID formats, pagination defaults, casing rules)
- End with the env var name required for authentication

**`python-dotenv`:** Add `python-dotenv` to your dependencies and call `load_dotenv()` at the
top of `app.py`. This lets developers drop a `.env` file in the project root for local
development without setting system env vars, while deployed environments supply vars directly.

## Tool Implementation

### Tool Naming

Use snake_case for tool names (e.g., "search_users", "create_project", "get_channel_info") with clear, action-oriented names.

**Avoid Naming Conflicts**: Include the service context to prevent overlaps:
- Use "slack_send_message" instead of just "send_message"
- Use "github_create_issue" instead of just "create_issue"
- Use "asana_list_tasks" instead of just "list_tasks"

### Tool Structure with FastMCP 3.x

Tools are defined using the `@mcp.tool` decorator with flat `Annotated` parameters for input
validation. **Do not** use a single `params: SomeModel` argument — FastMCP 3.x exposes it as
a nested object in the JSON schema, which breaks LLM tool use.

```python
from fastmcp import FastMCP
from pydantic import Field
from typing import Annotated, Optional, List

# Initialize the MCP server
mcp = FastMCP("example_mcp")

@mcp.tool(
    name="service_tool_name",
    annotations={
        "title": "Human-Readable Tool Title",
        "readOnlyHint": True,      # Tool does not modify environment
        "destructiveHint": False,   # Tool does not perform destructive operations
        "idempotentHint": True,     # Repeated calls have no additional effect
        "openWorldHint": False      # Tool does not interact with external entities
    }
)
async def service_tool_name(
    param1: Annotated[str, Field(description="First parameter (e.g., 'user123')", min_length=1, max_length=100)],
    param2: Annotated[Optional[int], Field(description="Optional integer, 0–1000", ge=0, le=1000)] = None,
    tags: Annotated[Optional[List[str]], Field(description="List of tags to apply")] = None,
) -> str:
    '''Tool description automatically becomes the 'description' field.

    This tool performs a specific operation on the service. Pydantic validates all
    inputs via the Annotated Field constraints before the function body runs.

    Args:
        param1 (str): First parameter description
        param2 (Optional[int]): Optional parameter with default
        tags (Optional[List[str]]): List of tags

    Returns:
        str: JSON-formatted response containing operation results
    '''
    # Implementation here
    pass
```

**Why `Annotated[type, Field(...)]` instead of a Pydantic model?**

FastMCP 3.x maps each function parameter directly to a top-level JSON schema property. When
you pass a Pydantic model as a single argument (e.g., `params: MyModel`), the schema wraps
everything under a `params` key, forcing the LLM to call the tool like
`{"params": {"param1": "...", "param2": 42}}`. With inline `Annotated` fields the schema is
flat (`{"param1": "...", "param2": 42}`), which is what LLMs expect.

You still get all Pydantic validation: `ge`, `le`, `min_length`, `max_length`, `pattern`,
enum types, and custom validators — just expressed inline rather than in a model class.

Pydantic `BaseModel` classes remain useful as **response types** or for internal data
structures, just not as tool input parameters.

## Pydantic v2 Key Features

Pydantic `BaseModel` classes are used for **response types, internal data structures, and
shared type definitions** — not as tool input parameters (see tool structure section above).

- Use `model_config` instead of nested `Config` class
- Use `field_validator` instead of deprecated `validator`
- Use `model_dump()` instead of deprecated `dict()`
- Validators require `@classmethod` decorator
- Type hints are required for validator methods

```python
from pydantic import BaseModel, Field, field_validator, ConfigDict

# Good use: response shape or internal data model
class UserRecord(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    name: str = Field(..., description="User's full name", min_length=1, max_length=100)
    email: str = Field(..., description="User's email address", pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    age: int = Field(..., description="User's age", ge=0, le=150)

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Email cannot be empty")
        return v.lower()

# Bad use: passing this as a tool parameter wraps it under a "params" key in the schema
# @mcp.tool(...)
# async def my_tool(params: UserRecord) -> str:   # DON'T do this
#     ...
```

For enum types used as tool parameters, use `str` enums with `Annotated`:

```python
from enum import Enum
from typing import Annotated
from pydantic import Field

class ResponseFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"

# Use directly as an Annotated parameter default:
async def my_tool(
    response_format: Annotated[ResponseFormat, Field(description="Output format")] = ResponseFormat.MARKDOWN,
) -> str:
    ...
```

## Response Format Options

Support multiple output formats for flexibility:

```python
from enum import Enum
from typing import Annotated
from pydantic import Field

class ResponseFormat(str, Enum):
    '''Output format for tool responses.'''
    MARKDOWN = "markdown"
    JSON = "json"

# Use as an Annotated parameter with a default:
async def my_tool(
    query: Annotated[str, Field(description="Search query")],
    response_format: Annotated[ResponseFormat, Field(
        description="Output format: 'markdown' for human-readable or 'json' for machine-readable"
    )] = ResponseFormat.MARKDOWN,
) -> str:
    ...
```

**Markdown format**:
- Use headers, lists, and formatting for clarity
- Convert timestamps to human-readable format (e.g., "2024-01-15 10:30:00 UTC" instead of epoch)
- Show display names with IDs in parentheses (e.g., "@john.doe (U123456)")
- Omit verbose metadata (e.g., show only one profile image URL, not all sizes)
- Group related information logically

**JSON format**:
- Return complete, structured data suitable for programmatic processing
- Include all available fields and metadata
- Use consistent field names and types

## Pagination Implementation

For tools that list resources:

```python
from typing import Annotated, Optional
from pydantic import Field

@mcp.tool(name="example_list_items")
async def example_list_items(
    limit: Annotated[Optional[int], Field(description="Maximum results to return", ge=1, le=100)] = 20,
    offset: Annotated[Optional[int], Field(description="Number of results to skip for pagination", ge=0)] = 0,
) -> str:
    data = await api_request(limit=limit, offset=offset)

    response = {
        "total": data["total"],
        "count": len(data["items"]),
        "offset": offset,
        "items": data["items"],
        "has_more": data["total"] > offset + len(data["items"]),
        "next_offset": offset + len(data["items"]) if data["total"] > offset + len(data["items"]) else None
    }
    return json.dumps(response, indent=2)
```

## Error Handling

Provide clear, actionable error messages:

```python
def _handle_api_error(e: Exception) -> str:
    '''Consistent error formatting across all tools.'''
    if isinstance(e, httpx.HTTPStatusError):
        if e.response.status_code == 404:
            return "Error: Resource not found. Please check the ID is correct."
        elif e.response.status_code == 403:
            return "Error: Permission denied. You don't have access to this resource."
        elif e.response.status_code == 429:
            return "Error: Rate limit exceeded. Please wait before making more requests."
        return f"Error: API request failed with status {e.response.status_code}"
    elif isinstance(e, httpx.TimeoutException):
        return "Error: Request timed out. Please try again."
    return f"Error: Unexpected error occurred: {type(e).__name__}"
```

## Shared Utilities

Extract common functionality into reusable functions:

```python
# Shared API request function
async def _make_api_request(endpoint: str, method: str = "GET", **kwargs) -> dict:
    '''Reusable function for all API calls.'''
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method,
            f"{API_BASE_URL}/{endpoint}",
            timeout=30.0,
            **kwargs
        )
        response.raise_for_status()
        return response.json()
```

## Async/Await Best Practices

Always use async/await for network requests and I/O operations:

```python
# Good: Async network request
async def fetch_data(resource_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}/resource/{resource_id}")
        response.raise_for_status()
        return response.json()

# Bad: Synchronous request
def fetch_data(resource_id: str) -> dict:
    response = requests.get(f"{API_URL}/resource/{resource_id}")  # Blocks
    return response.json()
```

## Type Hints

Use type hints throughout:

```python
from typing import Optional, List, Dict, Any

async def get_user(user_id: str) -> Dict[str, Any]:
    data = await fetch_user(user_id)
    return {"id": data["id"], "name": data["name"]}
```

## Tool Docstrings

Every tool must have a concise docstring covering purpose, usage guidance, and error behaviour.
Parameter types and constraints are already expressed in the `Annotated[type, Field(...)]`
signatures — don't duplicate them in the docstring.

```python
async def example_search_users(
    query: Annotated[str, Field(description="Search string", min_length=2, max_length=200)],
    limit: Annotated[Optional[int], Field(description="Max results", ge=1, le=100)] = 20,
    offset: Annotated[Optional[int], Field(description="Pagination offset", ge=0)] = 0,
    response_format: Annotated[ResponseFormat, Field(description="Output format")] = ResponseFormat.MARKDOWN,
) -> str:
    '''Search for users in the Example system by name, email, or team.

    Does NOT create or modify users — only searches existing ones.

    Use when: "Find all marketing team members" -> query="team:marketing"
    Use when: "Search for John's account" -> query="john"
    Don't use when: You need to create a user (use example_create_user instead).
    Don't use when: You have a user ID (use example_get_user instead — faster).

    Returns JSON schema on success:
    {
        "total": int, "count": int, "offset": int,
        "users": [{"id": str, "name": str, "email": str, "team": str}],
        "has_more": bool, "next_offset": int
    }

    Error responses:
    - "Error: Rate limit exceeded" — 429 from API
    - "Error: Invalid API key" — 403 from API
    - "No users found matching '<query>'" — empty result set
    '''
```

## Complete Example

See below for a complete Python MCP server example using the FastMCP 3.x pattern:

```python
#!/usr/bin/env python3
'''MCP Server for Example Service.'''

import json
import os
from typing import Annotated, Optional
from enum import Enum
import httpx
from dotenv import load_dotenv
from pydantic import Field
from fastmcp import FastMCP

load_dotenv()  # loads .env into os.environ before anything reads API keys

mcp = FastMCP(
    "example_mcp",
    instructions=(
        "This server provides access to the Example API. "
        "TOOL SELECTION GUIDE:\n"
        "- Search for a user by name or email → example_search_users\n"
        "- Get full details for a known user ID → example_get_user\n"
        "AUTHENTICATION: Requires EXAMPLE_API_KEY environment variable."
    ),
)

API_BASE_URL = "https://api.example.com/v1"


class ResponseFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"


async def _make_api_request(endpoint: str, method: str = "GET", **kwargs) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method,
            f"{API_BASE_URL}/{endpoint}",
            timeout=30.0,
            **kwargs
        )
        response.raise_for_status()
        return response.json()


def _handle_api_error(e: Exception) -> str:
    if isinstance(e, httpx.HTTPStatusError):
        if e.response.status_code == 404:
            return "Error: Resource not found. Please check the ID is correct."
        elif e.response.status_code == 403:
            return "Error: Permission denied. You don't have access to this resource."
        elif e.response.status_code == 429:
            return "Error: Rate limit exceeded. Please wait before making more requests."
        return f"Error: API request failed with status {e.response.status_code}"
    elif isinstance(e, httpx.TimeoutException):
        return "Error: Request timed out. Please try again."
    return f"Error: Unexpected error occurred: {type(e).__name__}"


@mcp.tool(
    name="example_search_users",
    annotations={
        "title": "Search Example Users",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def example_search_users(
    query: Annotated[str, Field(description="Search string to match against names/emails", min_length=2, max_length=200)],
    limit: Annotated[Optional[int], Field(description="Maximum results to return", ge=1, le=100)] = 20,
    offset: Annotated[Optional[int], Field(description="Number of results to skip for pagination", ge=0)] = 0,
    response_format: Annotated[ResponseFormat, Field(description="Output format: 'markdown' or 'json'")] = ResponseFormat.MARKDOWN,
) -> str:
    '''Search for users in the Example system by name, email, or team.

    Use when: "Find all marketing team members", "Search for John's account".
    Don't use when: You need to create a user (use example_create_user instead).
    '''
    try:
        data = await _make_api_request(
            "users/search",
            params={"q": query, "limit": limit, "offset": offset}
        )

        users = data.get("users", [])
        total = data.get("total", 0)

        if not users:
            return f"No users found matching '{query}'"

        if response_format == ResponseFormat.MARKDOWN:
            lines = [f"# User Search Results: '{query}'", "",
                     f"Found {total} users (showing {len(users)})", ""]
            for user in users:
                lines.append(f"## {user['name']} ({user['id']})")
                lines.append(f"- **Email**: {user['email']}")
                if user.get('team'):
                    lines.append(f"- **Team**: {user['team']}")
                lines.append("")
            return "\n".join(lines)

        return json.dumps({
            "total": total,
            "count": len(users),
            "offset": offset,
            "users": users,
        }, indent=2)

    except Exception as e:
        return _handle_api_error(e)


if __name__ == "__main__":
    port_env = os.getenv("DATABRICKS_APP_PORT") or os.getenv("PORT")
    if port_env:
        mcp.run(transport="http", host="0.0.0.0", port=int(port_env))
    else:
        mcp.run(transport="stdio")
```

---

## Advanced FastMCP Features

### Context Parameter Injection

FastMCP can automatically inject a `Context` parameter into tools for advanced capabilities like logging, progress reporting, resource reading, and user interaction:

```python
from fastmcp import FastMCP, Context

mcp = FastMCP("example_mcp")

@mcp.tool()
async def advanced_search(query: str, ctx: Context) -> str:
    '''Advanced tool with context access for logging and progress.'''

    # Report progress for long operations
    await ctx.report_progress(0.25, "Starting search...")

    # Log information for debugging
    await ctx.log_info("Processing query", {"query": query, "timestamp": datetime.now()})

    # Perform search
    results = await search_api(query)
    await ctx.report_progress(0.75, "Formatting results...")

    # Access server configuration
    server_name = ctx.fastmcp.name

    return format_results(results)

@mcp.tool()
async def interactive_tool(resource_id: str, ctx: Context) -> str:
    '''Tool that can request additional input from users.'''

    # Request sensitive information when needed
    api_key = await ctx.elicit(
        prompt="Please provide your API key:",
        input_type="password"
    )

    # Use the provided key
    return await api_call(resource_id, api_key)
```

**Context capabilities:**
- `ctx.report_progress(progress, message)` - Report progress for long operations
- `ctx.log_info(message, data)` / `ctx.log_error()` / `ctx.log_debug()` - Logging
- `ctx.elicit(prompt, input_type)` - Request input from users
- `ctx.fastmcp.name` - Access server configuration
- `ctx.read_resource(uri)` - Read MCP resources

### Resource Registration

Expose data as resources for efficient, template-based access:

```python
@mcp.resource("file://documents/{name}")
async def get_document(name: str) -> str:
    '''Expose documents as MCP resources.

    Resources are useful for static or semi-static data that doesn't
    require complex parameters. They use URI templates for flexible access.
    '''
    document_path = f"./docs/{name}"
    with open(document_path, "r") as f:
        return f.read()

@mcp.resource("config://settings/{key}")
async def get_setting(key: str, ctx: Context) -> str:
    '''Expose configuration as resources with context.'''
    settings = await load_settings()
    return json.dumps(settings.get(key, {}))
```

**When to use Resources vs Tools:**
- **Resources**: For data access with simple parameters (URI templates)
- **Tools**: For complex operations with validation and business logic

### Structured Output Types

FastMCP supports multiple return types beyond strings:

```python
from typing import TypedDict
from dataclasses import dataclass
from pydantic import BaseModel

# TypedDict for structured returns
class UserData(TypedDict):
    id: str
    name: str
    email: str

@mcp.tool()
async def get_user_typed(user_id: str) -> UserData:
    '''Returns structured data - FastMCP handles serialization.'''
    return {"id": user_id, "name": "John Doe", "email": "john@example.com"}

# Pydantic models for complex validation
class DetailedUser(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime
    metadata: Dict[str, Any]

@mcp.tool()
async def get_user_detailed(user_id: str) -> DetailedUser:
    '''Returns Pydantic model - automatically generates schema.'''
    user = await fetch_user(user_id)
    return DetailedUser(**user)
```

### Lifespan Management

Initialize resources that persist across requests:

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def app_lifespan():
    '''Manage resources that live for the server's lifetime.'''
    # Initialize connections, load config, etc.
    db = await connect_to_database()
    config = load_configuration()

    # Make available to all tools
    yield {"db": db, "config": config}

    # Cleanup on shutdown
    await db.close()

mcp = FastMCP("example_mcp", lifespan=app_lifespan)

@mcp.tool()
async def query_data(query: str, ctx: Context) -> str:
    '''Access lifespan resources through context.'''
    db = ctx.request_context.lifespan_state["db"]
    results = await db.query(query)
    return format_results(results)
```

### Transport Options

FastMCP supports two main transport mechanisms. Use a dual-transport `__main__` block so the
same `app.py` works both as a local stdio server and as a deployed HTTP service without any
code changes:

```python
import os

if __name__ == "__main__":
    # Check for a platform port env var (set by Databricks Apps, Cloud Run, etc.).
    # If present, run as an HTTP server. Otherwise fall back to stdio for local
    # MCP clients (Claude Desktop, Claude Code, etc.).
    port_env = os.getenv("DATABRICKS_APP_PORT") or os.getenv("PORT")
    if port_env:
        mcp.run(transport="http", host="0.0.0.0", port=int(port_env))
    else:
        mcp.run(transport="stdio")
```

**Transport selection:**
- **stdio**: Local MCP clients (Claude Desktop, Claude Code), single-user subprocess execution
- **http**: Deployed web services, Databricks Apps, Cloud Run, multi-client scenarios

---

## Code Best Practices

### Code Composability and Reusability

Your implementation MUST prioritize composability and code reuse:

1. **Extract Common Functionality**:
   - Create reusable helper functions for operations used across multiple tools
   - Build shared API clients for HTTP requests instead of duplicating code
   - Centralize error handling logic in utility functions
   - Extract business logic into dedicated functions that can be composed
   - Extract shared markdown or JSON field selection & formatting functionality

2. **Avoid Duplication**:
   - NEVER copy-paste similar code between tools
   - If you find yourself writing similar logic twice, extract it into a function
   - Common operations like pagination, filtering, field selection, and formatting should be shared
   - Authentication/authorization logic should be centralized

### Python-Specific Best Practices

1. **Use Type Hints**: Always include type annotations for function parameters and return values
2. **Pydantic Models**: Define clear Pydantic models for all input validation
3. **Avoid Manual Validation**: Let Pydantic handle input validation with constraints
4. **Proper Imports**: Group imports (standard library, third-party, local)
5. **Error Handling**: Use specific exception types (httpx.HTTPStatusError, not generic Exception)
6. **Async Context Managers**: Use `async with` for resources that need cleanup
7. **Constants**: Define module-level constants in UPPER_CASE

## Quality Checklist

Before finalizing your Python MCP server implementation, ensure:

### Strategic Design
- [ ] Tools enable complete workflows, not just API endpoint wrappers
- [ ] Tool names reflect natural task subdivisions
- [ ] Response formats optimize for agent context efficiency
- [ ] Human-readable identifiers used where appropriate
- [ ] Error messages guide agents toward correct usage

### Implementation Quality
- [ ] FOCUSED IMPLEMENTATION: Most important and valuable tools implemented
- [ ] All tools have descriptive names and documentation
- [ ] Return types are consistent across similar operations
- [ ] Error handling is implemented for all external calls
- [ ] Server name follows format: `{service}_mcp`
- [ ] All network operations use async/await
- [ ] Common functionality is extracted into reusable functions
- [ ] Error messages are clear, actionable, and educational
- [ ] Outputs are properly validated and formatted

### app.py
- [ ] `load_dotenv()` called at the top before any code reads env vars
- [ ] `python-dotenv` listed in project dependencies
- [ ] `FastMCP` initialized with a meaningful `instructions` string
- [ ] `instructions` includes a TOOL SELECTION GUIDE mapping tasks to tool names
- [ ] `instructions` documents domain conventions and the required env var name
- [ ] Dual-transport `__main__` block: HTTP when `DATABRICKS_APP_PORT`/`PORT` is set, stdio otherwise
- [ ] No tool logic in `app.py` — only server init and transport configuration

### Tool Configuration
- [ ] All tools implement 'name' and 'annotations' in the decorator
- [ ] Annotations correctly set (readOnlyHint, destructiveHint, idempotentHint, openWorldHint)
- [ ] All tool parameters use `Annotated[type, Field(...)]` — NOT a single `params: Model` argument
- [ ] All `Field()` definitions have explicit descriptions and appropriate constraints (ge, le, min_length, pattern, etc.)
- [ ] All tools have concise docstrings covering purpose, usage examples, return schema, and error responses
- [ ] Pydantic `BaseModel` classes used only for response types or internal data structures, not tool inputs

### Advanced Features (where applicable)
- [ ] Context injection used for logging, progress, or elicitation
- [ ] Resources registered for appropriate data endpoints
- [ ] Lifespan management implemented for persistent connections
- [ ] Structured output types used (TypedDict, Pydantic models)
- [ ] Appropriate transport configured (stdio or streamable HTTP)

### Code Quality
- [ ] File includes proper imports including Pydantic imports
- [ ] Pagination is properly implemented where applicable
- [ ] Filtering options are provided for potentially large result sets
- [ ] All async functions are properly defined with `async def`
- [ ] HTTP client usage follows async patterns with proper context managers
- [ ] Type hints are used throughout the code
- [ ] Constants are defined at module level in UPPER_CASE

### Testing
- [ ] Server runs successfully: `python your_server.py --help`
- [ ] All imports resolve correctly
- [ ] Sample tool calls work as expected
- [ ] Error scenarios handled gracefully
