#!/bin/bash
# Script to test the providers command with and without API keys

echo "========================================="
echo "Testing icon-gen-ai providers command"
echo "========================================="
echo ""

echo "🔧 Using LOCAL development version (uv run)"
echo ""

echo "1️⃣  Test WITH configured API key(s):"
echo "----------------------------------------"
uv run icon-gen-ai providers
echo ""

echo "2️⃣  Test WITHOUT API keys (temporarily unsetting):"
echo "----------------------------------------"
env -u OPENAI_API_KEY -u ANTHROPIC_API_KEY -u HF_TOKEN uv run icon-gen-ai providers
echo ""

echo "========================================="
echo "Testing complete!"
echo "========================================="
