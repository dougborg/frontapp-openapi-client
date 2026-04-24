# ADR-006: Use Utility Functions for Response Unwrapping

## Status

Accepted

Date: 2026-04-24

## Context

The generated API returns `Response[T]` objects with the structure:

```python
response = Response(
    status_code=200,
    content=b"...",
    headers={...},
    parsed=ConversationResponse(...)  # or a per-endpoint error shape
)
```

Users need to:

1. Check if the response was successful
2. Extract the parsed data
3. Handle different response types (success vs. error)
4. Deal with Front's paginated list shape (`_results` becomes `field_results` after
   openapi-python-client name-mangling)
5. Get proper type hints throughout

Common user code without helpers is verbose:

```python
response = await list_conversations.asyncio_detailed(client=client)
if response.status_code == 200:
    parsed = response.parsed
    results = getattr(parsed, "field_results", None) or []
    for conv in results:
        ...
```

This creates boilerplate, and the `field_results` gotcha in particular is easy to miss —
the generated name depends on the upstream `_results` key, which is non-obvious.

## Decision

Provide **utility functions** in `frontapp_public_api_client.utils` that encapsulate the
common response operations:

### Core utilities

```python
# Extract parsed data with automatic typed-error raising
def unwrap(response: Response[T], *, raise_on_error: bool = True) -> T: ...

# Single-object with type assertion
def unwrap_as(
    response: Response[T], expected_type: type[ExpectedT], *, raise_on_error: bool = True
) -> ExpectedT: ...

# Wrapped list responses (grabs `.data` from legacy APIs that use it)
def unwrap_data(
    response: Response[T], *, raise_on_error: bool = True, default: list | None = None
) -> list[Any] | None: ...

# Status checks
def is_success(response: Response[Any]) -> bool: ...
def is_error(response: Response[Any]) -> bool: ...

# Error-message extraction
def get_error_message(response: Response[Any]) -> str | None: ...

# Callback-based handler
def handle_response(
    response: Response[T],
    *,
    on_success: Callable[[T], Any] | None = None,
    on_error: Callable[[APIError], Any] | None = None,
    raise_on_error: bool = False,
) -> Any: ...
```

### Typed exceptions

```python
class APIError(Exception):
    """Base for all Front API errors. Carries status_code + raw body."""

class AuthenticationError(APIError): ...    # 401
class ValidationError(APIError): ...        # 422
class RateLimitError(APIError): ...         # 429
class ServerError(APIError): ...            # 5xx
```

### Front-specific behavior: status-based error dispatch

Unlike some APIs, Front does **not** ship a single canonical `ErrorResponse` schema.
Error bodies vary per endpoint. `unwrap()` therefore dispatches on HTTP status rather
than on parsed type, and stores the attrs/dict payload on `error.error_response` as
`Any` for inspection:

```python
# Inside utils.unwrap()
if not (200 <= response.status_code < 300):
    if status == HTTPStatus.UNAUTHORIZED:
        raise AuthenticationError(message, status, parsed)
    if status == HTTPStatus.UNPROCESSABLE_ENTITY:
        raise ValidationError(message, status, parsed)
    if status == HTTPStatus.TOO_MANY_REQUESTS:
        raise RateLimitError(message, status, parsed)
    if 500 <= status < 600:
        raise ServerError(message, status, parsed)
    raise APIError(message, status, parsed)
```

### Usage

**Single-object response**:

```python
from frontapp_public_api_client.utils import unwrap_as
from frontapp_public_api_client.models.conversation_response import ConversationResponse

response = await get_conversation_by_id.asyncio_detailed(
    client=client, conversation_id="cnv_abc"
)
conv = unwrap_as(response, ConversationResponse)  # raises AuthenticationError / etc. on failure
```

**Paginated list response**:

```python
from frontapp_public_api_client.utils import unwrap

response = await list_conversations.asyncio_detailed(client=client, limit=50)
parsed = unwrap(response)
results = getattr(parsed, "field_results", None) or []
```

**Typed error handling**:

```python
from frontapp_public_api_client.utils import ValidationError

try:
    conv = unwrap_as(response, ConversationResponse)
except ValidationError as e:
    # e.error_response carries whatever Front returned
    print(f"Validation failed: {e}")
    print(f"Raw: {e.error_response}")
```

## Consequences

### Positive

1. **Reduced boilerplate**: 5+ lines → 1 line for the common case
2. **Type safety**: `@overload` decorators for proper type narrowing
3. **Better errors**: typed exceptions with status + raw body attached
4. **IDE support**: full autocomplete and type hints
5. **Opt-in**: users can still use `Response` directly for low-level needs
6. **Front-appropriate**: status-based dispatch accommodates Front's per-endpoint error
   shapes without forcing a schema we don't have
7. **Composable**: combine utilities for complex scenarios

### Negative

1. **Additional API to learn**: users need to know the helpers exist and when to reach
   for each
2. **Implicit raise**: `unwrap()` throws by default, which is generally desired but
   occasionally surprising
3. **Abstraction**: hides some raw response details that low-level debugging might want
   (workaround: `raise_on_error=False` returns `None` for the common case and leaves the
   caller to inspect `response` directly)

### Neutral

1. **Exported at the package top level**:
   `from frontapp_public_api_client import unwrap, unwrap_as, is_success, APIError`
2. **`field_results` gotcha documented in CLAUDE.md** — new contributors should read the
   Known Pitfalls section before writing list-handling code

## Type system design

`@overload` decorators make the type checker understand behavior:

```python
@overload
def unwrap[T](response: Response[T], *, raise_on_error: bool = True) -> T: ...

@overload
def unwrap[T](response: Response[T], *, raise_on_error: bool = False) -> T | None: ...
```

This means no assertions are needed in user code — the type checker knows that
`unwrap(response)` returns `T` (never `None`) when `raise_on_error=True` (the default):

```python
conv = unwrap_as(response, ConversationResponse)
print(conv.subject)   # no type error, conv is definitely ConversationResponse
```

## Alternatives considered

### Monadic Result type

```python
result = await list_conversations.asyncio_detailed(client=client)
results = (
    result.map(lambda r: r.field_results)
    .unwrap_or([])
)
```

**Rejected**: not Pythonic, steep learning curve, overkill for simple cases.

### Methods on the Response class

Extend `Response` with utility methods: `response.unwrap_data()`.

**Rejected**: `Response` is generated by openapi-python-client and gets overwritten on
regeneration. Monkey-patching is fragile.

### Context manager

```python
with handle_response() as handler:
    response = await list_conversations.asyncio_detailed(client=client)
    results = handler.get_results(response)
```

**Rejected**: verbose, extra indentation, no clear benefit over try/except.

### Defer to status_code checks at call sites

Don't provide helpers — ask callers to do the `if 200 <= status_code < 300` dance
themselves.

**Rejected**: this is the boilerplate the ADR exists to eliminate. Every caller would
reimplement the same check, `field_results` unwrapping, and typed-exception dispatch.
Bugs would proliferate.

## Implementation notes

### UNSET handling

Handles Front's `UNSET` fields gracefully via `unwrap_unset` in the domain layer (see
[ADR-0011: Pydantic Domain Models](0011-pydantic-domain-models.md)):

```python
# If a field is UNSET, returns default rather than raising
tags = unwrap_unset(conv.tags, [])
```

### Error-response inspection

Because Front's error bodies vary per endpoint, `error.error_response` is typed as
`Any`. Callers who want structured error handling should inspect the specific endpoint's
response shape (e.g. 422s on POSTs typically include a `message` string and sometimes
per-field details; 429 carries `Retry-After` in headers rather than the body).

## References

- [`utils.py`](../../utils.py) — implementation
- [ADR-001: Transport-Layer Resilience](0001-transport-layer-resilience.md) — retries
  layer underneath
- [ADR-0011: Pydantic Domain Models](0011-pydantic-domain-models.md) — domain layer on
  top
- [CLAUDE.md](../../../CLAUDE.md) — Known Pitfalls including `field_results` gotcha
