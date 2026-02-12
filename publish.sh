#!/bin/bash
# Manual PyPI publish script with venv

set -e

echo "Creating virtual environment..."
python3 -m venv publish_venv
source publish_venv/bin/activate

echo "Installing build dependencies..."
pip3 install --upgrade pip build twine

echo "Cleaning old builds..."
rm -rf dist/ build/ *.egg-info

echo "Building package..."
python3 -m build

echo ""
echo "Checking package..."
twine check dist/*

echo ""
echo "✓ Build complete! Files in dist/:"
ls -lh dist/

echo ""
echo "To upload to PyPI, run:"
echo ""
echo "  source publish_venv/bin/activate && twine upload dist/* --username __token__ --password pypi-YOUR_TOKEN_HERE"
echo ""
echo "Or provide your token as an argument:"
echo "  ./publish.sh pypi-YOUR_TOKEN_HERE"
echo ""

# If token provided as argument, upload automatically
if [ -n "$1" ]; then
    echo "Uploading with provided token..."
    twine upload dist/* --username __token__ --password "$1"
    echo "✓ Upload complete!"
fi

echo ""
echo "After publishing, clean up with: rm -rf publish_venv dist build *.egg-info"
