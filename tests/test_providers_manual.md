# Manual Testing Guide for `icon-gen-ai providers` Command

This guide helps you manually test the different states of the `providers` command.

## Test Scenario 1: No AI Features Installed

**Setup:**
```bash
# Uninstall the package completely
pip uninstall icon-gen-ai -y

# Install without AI extras
pip install icon-gen-ai
```

**Test:**
```bash
icon-gen-ai providers
```

**Expected Output:**
```
❌ AI features not installed

To enable AI-powered icon search, install the AI extras:
  pip install icon-gen-ai[ai]

Then configure at least one API key:
  • OPENAI_API_KEY (OpenAI)
  • ANTHROPIC_API_KEY (Anthropic)
  • HF_TOKEN (Hugging Face)
```

---

## Test Scenario 2: AI Features Installed, No API Key Configured

**Setup:**
```bash
# Install with AI extras
pip install icon-gen-ai[ai]

# Make sure no API keys are set
unset OPENAI_API_KEY
unset ANTHROPIC_API_KEY
unset HF_TOKEN
```

**Test:**
```bash
icon-gen-ai providers
```

**Expected Output:**
```
✓ Available providers: anthropic, huggingface, openai

⚠ No API key configured

Configure at least one API key to use AI features:
  • OPENAI_API_KEY (OpenAI)
  • ANTHROPIC_API_KEY (Anthropic)
  • HF_TOKEN (Hugging Face)

Set via environment variable or .env file
```

---

## Test Scenario 3: AI Features Installed with Active Provider

**Setup:**
```bash
# Install with AI extras (if not already)
pip install icon-gen-ai[ai]

# Set an API key
export OPENAI_API_KEY="your-key-here"
# OR
export ANTHROPIC_API_KEY="your-key-here"
# OR
export HF_TOKEN="your-key-here"
```

**Test:**
```bash
icon-gen-ai providers
```

**Expected Output:**
```
✓ Available providers: anthropic, huggingface, openai
✓ Active provider: OpenAI (gpt-4o)
```
(The provider name and model will vary based on which key you set)

---

## Quick Test Script

Save this as `test_providers.sh`:

```bash
#!/bin/bash

echo "=== Test 1: With API Key ==="
icon-gen-ai providers
echo ""

echo "=== Test 2: Without API Keys ==="
(unset OPENAI_API_KEY ANTHROPIC_API_KEY HF_TOKEN; icon-gen-ai providers)
echo ""

echo "Done!"
```

Make it executable:
```bash
chmod +x test_providers.sh
./test_providers.sh
```
