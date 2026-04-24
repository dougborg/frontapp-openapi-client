---

## description: 'Regenerate the OpenAPI client from the specification'

# Regenerate OpenAPI Client

Regenerate the Python client code from the Frontapp OpenAPI specification.

## Pre-requisites

- OpenAPI spec is valid and up-to-date at `docs/frontapp-openapi.yaml`
- All dependencies installed: `uv sync --all-extras`

## Instructions

1. **Validate the OpenAPI spec**:

   ```bash
   uv run poe validate-openapi
   ```

   - Check for any validation errors
   - Fix spec issues before proceeding

1. **Run regeneration** (~2+ minutes, NEVER CANCEL):

   ```bash
   uv run poe regenerate-client
   ```

   This script automatically:
   - Validates the spec with openapi-spec-validator
   - Validates with Redocly
   - Generates client using openapi-python-client
   - Auto-fixes code quality with ruff
   - Moves generated code to package location

1. **Review changes**:

   ```bash
   git diff frontapp_public_api_client/
   ```

   - Check for unexpected changes
   - Verify new endpoints/models look correct
   - Ensure no manual edits were lost

1. **Run validation**:

   ```bash
   uv run poe check
   ```

   - Verify tests pass
   - Check type hints are valid
   - Ensure formatting is correct

1. **Commit changes**:

   ```bash
   git add frontapp_public_api_client/api/
   git add frontapp_public_api_client/models/
   git add frontapp_public_api_client/client.py
   git add frontapp_public_api_client/client_types.py
   git commit -m "chore(client): regenerate from OpenAPI spec"
   ```

## What Gets Regenerated

### DO NOT EDIT (Generated Files):

- `frontapp_public_api_client/api/**/*.py` - API endpoint methods
- `frontapp_public_api_client/models/**/*.py` - Data models (attrs)
- `frontapp_public_api_client/client.py` - Base client classes
- `frontapp_public_api_client/client_types.py` - Type definitions
- `frontapp_public_api_client/errors.py` - Error classes

### PRESERVED (Not Regenerated):

- `frontapp_public_api_client/frontapp_client.py` - Enhanced client
- `frontapp_public_api_client/domain/**/*.py` - Pydantic domain models
- `frontapp_public_api_client/helpers/**/*.py` - Helper utilities
- `tests/**/*.py` - Test files

## Troubleshooting

**Validation fails**:

- Check `docs/frontapp-openapi.yaml` for syntax errors
- Verify all `$ref` references are valid
- Ensure required fields are present

**Generation fails**:

- Check npx and node are installed
- Verify openapi-python-client is available
- Check error messages for specific issues

**Tests fail after regeneration**:

- API models may have changed
- Update tests to match new schemas
- Check for breaking changes in API

## Success Criteria

- [ ] OpenAPI spec validates successfully
- [ ] Client regeneration completes without errors
- [ ] `uv run poe check` passes
- [ ] Git diff shows expected changes only
- [ ] Tests pass with new generated code
- [ ] Commit created with proper message
