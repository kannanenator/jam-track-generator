# Installation Guide

## Prerequisites Installation

### 1. Install Rust (via rustup)

#### Linux / macOS / WSL
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

When prompted, choose the default installation (option 1).

After installation, reload your shell environment:
```bash
source "$HOME/.cargo/env"
```

Verify installation:
```bash
rustc --version
cargo --version
```

#### Windows
Download and run the installer from: https://rustup.rs/

Or use winget:
```powershell
winget install Rustlang.Rustup
```

### 2. Install wasm-pack

#### Linux / macOS / WSL
```bash
curl https://rustwasm.github.io/wasm-pack/installer/init.sh -sSf | sh
```

#### Windows
Download from: https://rustwasm.github.io/wasm-pack/installer/

Or use cargo:
```bash
cargo install wasm-pack
```

Verify installation:
```bash
wasm-pack --version
```

### 3. Add WASM target (if needed)
```bash
rustup target add wasm32-unknown-unknown
```

## Building the Project

Once prerequisites are installed:

```bash
# Option 1: Use the build script
./build.sh

# Option 2: Build manually
wasm-pack build --target web --out-dir example/pkg

# Option 3: Build with optimizations (smaller file size)
wasm-pack build --target web --release --out-dir example/pkg
```

## Running the Example

```bash
cd example

# Python 3
python3 -m http.server 8080

# Python 2
python -m SimpleHTTPServer 8080

# Node.js (if you have it)
npx http-server -p 8080

# PHP (if you have it)
php -S localhost:8080
```

Then open http://localhost:8080 in your browser.

## Troubleshooting

### "rustup: command not found"
Make sure to reload your shell after installation:
```bash
source "$HOME/.cargo/env"
```

Or restart your terminal.

### "wasm-pack: command not found"
Add cargo bin to your PATH:
```bash
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Build errors
Make sure you have the WASM target installed:
```bash
rustup target add wasm32-unknown-unknown
```

### Network issues during build
If you're behind a proxy or have network restrictions, you may need to:
```bash
# Set proxy (if needed)
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
```

## Quick Start (Copy-Paste)

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"

# Install wasm-pack
curl https://rustwasm.github.io/wasm-pack/installer/init.sh -sSf | sh

# Add WASM target
rustup target add wasm32-unknown-unknown

# Build the project
./build.sh

# Run the example
cd example
python3 -m http.server 8080
```

Then open http://localhost:8080 in your browser!
