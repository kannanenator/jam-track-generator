#!/bin/bash

# Build script for the WASM jam track generator

set -e

echo "Building WASM module..."

# Check if wasm-pack is installed
if ! command -v wasm-pack &> /dev/null; then
    echo "wasm-pack not found. Installing..."
    curl https://rustwasm.github.io/wasm-pack/installer/init.sh -sSf | sh
fi

# Build the WASM module
wasm-pack build --target web --out-dir example/pkg

echo "Build complete! WASM module is in example/pkg/"
echo ""
echo "To test the example:"
echo "  cd example"
echo "  python3 -m http.server 8080"
echo "  # Then open http://localhost:8080 in your browser"
