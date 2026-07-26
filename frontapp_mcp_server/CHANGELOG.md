# Changelog

## [0.2.0](https://github.com/dougborg/frontapp-openapi-client/compare/mcp-v0.1.0...mcp-v0.2.0) (2026-07-26)


### Features

* **client,mcp:** analytics polling vertical ([#6](https://github.com/dougborg/frontapp-openapi-client/issues/6)) ([#79](https://github.com/dougborg/frontapp-openapi-client/issues/79)) ([7200b79](https://github.com/dougborg/frontapp-openapi-client/commit/7200b79b475fbf2b33993dfff16ee51f37e25638))
* **client,mcp:** attachment upload + download support ([#12](https://github.com/dougborg/frontapp-openapi-client/issues/12)) ([#65](https://github.com/dougborg/frontapp-openapi-client/issues/65)) ([1e5d4db](https://github.com/dougborg/frontapp-openapi-client/commit/1e5d4db139186c290a7a034f2a1f5cfe75d79b23))
* **client,mcp:** close out small workspace-admin Tier 2/3 issues ([#84](https://github.com/dougborg/frontapp-openapi-client/issues/84), [#86](https://github.com/dougborg/frontapp-openapi-client/issues/86), [#93](https://github.com/dougborg/frontapp-openapi-client/issues/93)) ([#97](https://github.com/dougborg/frontapp-openapi-client/issues/97)) ([c077a22](https://github.com/dougborg/frontapp-openapi-client/commit/c077a22fd5565dab93906ebdb6b95708de3a7a4c))
* **client,mcp:** contact_lists + contact_groups verticals ([#47](https://github.com/dougborg/frontapp-openapi-client/issues/47), [#48](https://github.com/dougborg/frontapp-openapi-client/issues/48)) ([#70](https://github.com/dougborg/frontapp-openapi-client/issues/70)) ([e7cedf9](https://github.com/dougborg/frontapp-openapi-client/commit/e7cedf939409d95a10c1ed173704838b8ad179f1))
* **client,mcp:** contacts vertical — list/get/create/update + handle lookups ([#46](https://github.com/dougborg/frontapp-openapi-client/issues/46)) ([528dc72](https://github.com/dougborg/frontapp-openapi-client/commit/528dc72b6faf6d4a5f4847b70849b9b5edc2f353))
* **client,mcp:** drafts vertical — drafts-first outbound ([#45](https://github.com/dougborg/frontapp-openapi-client/issues/45)) ([f5909c2](https://github.com/dougborg/frontapp-openapi-client/commit/f5909c27791b3f1f484bf88389d4453ada52affb))
* **client,mcp:** knowledge_bases read + contribute vertical ([#83](https://github.com/dougborg/frontapp-openapi-client/issues/83)) ([#96](https://github.com/dougborg/frontapp-openapi-client/issues/96)) ([8e18ee7](https://github.com/dougborg/frontapp-openapi-client/commit/8e18ee7ab4925b52c84bb38b0ef0e2595840f930))
* **client,mcp:** messages vertical — get / seen status / mark seen ([#4](https://github.com/dougborg/frontapp-openapi-client/issues/4)) ([#53](https://github.com/dougborg/frontapp-openapi-client/issues/53)) ([8666688](https://github.com/dougborg/frontapp-openapi-client/commit/8666688fd4d7a067db0916c41c75491c178c6817))
* **client,mcp:** tags & inboxes management vertical ([#5](https://github.com/dougborg/frontapp-openapi-client/issues/5)) ([#54](https://github.com/dougborg/frontapp-openapi-client/issues/54)) ([6b3c5b0](https://github.com/dougborg/frontapp-openapi-client/commit/6b3c5b01dfd043559398c72d2dcf6665be464942))
* **client,mcp:** teammates vertical (follow-up D) ([#61](https://github.com/dougborg/frontapp-openapi-client/issues/61)) ([f6c31ae](https://github.com/dougborg/frontapp-openapi-client/commit/f6c31ae8baddcf210bf21ea02029a550a7ad3370))
* **mcp:** mark mutation tools with destructiveHint annotation ([#117](https://github.com/dougborg/frontapp-openapi-client/issues/117)) ([c8a056a](https://github.com/dougborg/frontapp-openapi-client/commit/c8a056ae562bb0259af0f914d63f7de1d1247441)), closes [#114](https://github.com/dougborg/frontapp-openapi-client/issues/114)
* **mcp:** reference resources — frontapp://tags, inboxes, teammates, conversations/recent ([#20](https://github.com/dougborg/frontapp-openapi-client/issues/20)) ([927e098](https://github.com/dougborg/frontapp-openapi-client/commit/927e098d3c0713ffc282096a052651215ceae6ed))
* **mcp:** workspace admin Tier 1 reference resources ([#80](https://github.com/dougborg/frontapp-openapi-client/issues/80), [#81](https://github.com/dougborg/frontapp-openapi-client/issues/81), [#82](https://github.com/dougborg/frontapp-openapi-client/issues/82)) ([#94](https://github.com/dougborg/frontapp-openapi-client/issues/94)) ([7c8c4d1](https://github.com/dougborg/frontapp-openapi-client/commit/7c8c4d1c2a7cb86c12fddbb7176a16204c7dabac))
* **release:** migrate to release-please manifest-mode release automation ([#168](https://github.com/dougborg/frontapp-openapi-client/issues/168)) ([fcdaaf4](https://github.com/dougborg/frontapp-openapi-client/commit/fcdaaf44eeb5a92fb6e00f12fcb05f62939e70c9))


### Bug Fixes

* **mcp:** drop ctx.elicit() from confirm_or_preview gate ([#115](https://github.com/dougborg/frontapp-openapi-client/issues/115)) ([df3b033](https://github.com/dougborg/frontapp-openapi-client/commit/df3b03309cc84bb9b069f7e82a61239b0e9ce0f9)), closes [#104](https://github.com/dougborg/frontapp-openapi-client/issues/104)
* **tests:** set MCP package asyncio_mode to auto ([#167](https://github.com/dougborg/frontapp-openapi-client/issues/167)) ([9a57510](https://github.com/dougborg/frontapp-openapi-client/commit/9a575106798713456077d25ab4c3e3ce42dff3d5)), closes [#166](https://github.com/dougborg/frontapp-openapi-client/issues/166)

## CHANGELOG

All notable changes to the Frontapp MCP Server will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
