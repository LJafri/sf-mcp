#!/bin/bash
# Setup script for Salesforce MCP Python server

set -e

echo "🚀 Setting up Salesforce MCP Python server..."
echo ""

# Check Python version
echo "✓ Checking Python version..."
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "✓ Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "✓ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "✓ Upgrading pip..."
pip install --upgrade pip

# Install package
echo "✓ Installing salesforce-mcp package..."
pip install -e .

# Install development dependencies (optional)
if [ "$1" == "--dev" ]; then
    echo "✓ Installing development dependencies..."
    pip install -r requirements-dev.txt
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To start the server, run:"
echo "  sf-mcp-server --orgs DEFAULT_TARGET_ORG --toolsets all"
echo ""
echo "For more information, see README.md"
