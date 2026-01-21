# icon-gen-ai – Changelog

## 0.4.7

### Fixed
- **CLI: Improved `providers` command messaging** - Now provides clear, actionable guidance when AI features are not installed or configured:
  - When AI extras are not installed: Shows explicit instructions to run `pip install icon-gen-ai[ai]`
  - When no API key is configured: Lists all supported API keys (ANTHROPIC_API_KEY, HF_TOKEN, OPENAI_API_KEY) with instructions on how to set them
  - When provider is active: Shows the active provider name and model
- **CLI: Updated `search` command error messages** - More descriptive errors that mention all three supported providers
- **Documentation: Added API key configuration guide** - README now includes instructions on how to configure API keys after installing AI extras

### Changed
- API keys are now listed alphabetically in all CLI messages (ANTHROPIC_API_KEY, HF_TOKEN, OPENAI_API_KEY)

