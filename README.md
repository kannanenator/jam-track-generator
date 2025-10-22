# 🎸 Modal Vamp Jam Track Generator

A WebAssembly-powered modal jam track generator written in Rust. Create looping chord progressions in any key and mode for jamming and practice.

## Features

- 🎵 **12 Keys**: All chromatic keys (C, C#, D, D#, E, F, F#, G, G#, A, A#, B)
- 🎼 **7 Modes**: Ionian, Dorian, Phrygian, Lydian, Mixolydian, Aeolian, Locrian
- ⏱️ **Adjustable Tempo**: 60-200 BPM
- 🔁 **Seamless Looping**: Generated tracks loop perfectly for jamming
- 🎹 **Modal Progressions**: Chord progressions that emphasize the character of each mode
- 🌐 **Web-based**: Runs entirely in the browser via WebAssembly

## Quick Start

### Prerequisites

- [Rust](https://www.rust-lang.org/tools/install) (1.70 or later)
- [wasm-pack](https://rustwasm.github.io/wasm-pack/installer/)

### Building

```bash
# Clone the repository
git clone <your-repo-url>
cd jam-track-generator

# Build the WASM module
./build.sh

# Or manually:
wasm-pack build --target web --out-dir example/pkg
```

### Running the Example

```bash
cd example
python3 -m http.server 8080
# Open http://localhost:8080 in your browser
```

## Usage

### Web Integration

```javascript
import init, { JamTrackConfig, JamTrackGenerator } from './pkg/jam_track_generator.js';

// Initialize the WASM module
await init();

// Create a configuration
const config = new JamTrackConfig("F#", "Phrygian", 150);

// Create the generator
const generator = new JamTrackGenerator(config);

// Generate audio samples
const samples = generator.generate_samples();
const sampleRate = generator.sample_rate();

// Get chord progression info
const progressionJson = generator.get_progression_info();
const chords = JSON.parse(progressionJson);
console.log("Chords:", chords); // e.g., ["F#m", "G", "F#m", "E"]

// Create an audio buffer and play it
const audioContext = new AudioContext();
const audioBuffer = audioContext.createBuffer(1, samples.length, sampleRate);
const channelData = audioBuffer.getChannelData(0);

for (let i = 0; i < samples.length; i++) {
    channelData[i] = samples[i];
}

const sourceNode = audioContext.createBufferSource();
sourceNode.buffer = audioBuffer;
sourceNode.loop = true; // Enable looping
sourceNode.connect(audioContext.destination);
sourceNode.start(0);
```

## Musical Theory

### Modes

Each mode has a unique character created by its interval pattern:

- **Ionian (Major)**: Bright and happy (W-W-H-W-W-W-H)
- **Dorian**: Minor with a raised 6th, jazzy feel (W-H-W-W-W-H-W)
- **Phrygian**: Dark and exotic with a flat 2nd (H-W-W-W-H-W-W)
- **Lydian**: Dreamy with a raised 4th (W-W-W-H-W-W-H)
- **Mixolydian**: Major with a flat 7th, bluesy (W-W-H-W-W-H-W)
- **Aeolian (Natural Minor)**: Sad and introspective (W-H-W-W-H-W-W)
- **Locrian**: Unstable with diminished quality (H-W-W-H-W-W-W)

### Chord Progressions

The generator creates 4-chord vamps that emphasize each mode's characteristic sound:

- **Phrygian**: i - bII - i - bVII (emphasizes the flat 2nd)
- **Dorian**: i - IV - i - IV (emphasizes the major IV)
- **Lydian**: I - II - I - II (emphasizes the major II)
- **Mixolydian**: I - bVII - I - bVII (emphasizes the flat 7th)
- **Aeolian**: i - iv - i - v (classic minor progression)
- **Ionian**: I - IV - I - V (classic major progression)
- **Locrian**: i° - bII - i° - bV (emphasizes diminished quality)

## Architecture

### Project Structure

```
jam-track-generator/
├── src/
│   ├── lib.rs           # WASM bindings and public API
│   ├── music_theory.rs  # Notes, scales, modes, chords
│   └── audio.rs         # Audio synthesis
├── example/
│   ├── index.html       # Demo web interface
│   └── pkg/            # Built WASM module (generated)
├── Cargo.toml          # Rust dependencies
├── build.sh            # Build script
└── README.md           # This file
```

### Audio Synthesis

The audio engine generates waveforms using:
- Multiple harmonics for a warmer, more musical sound
- ADSR envelope (Attack, Decay, Sustain, Release) for natural-sounding notes
- 44.1kHz sample rate (CD quality)
- Proper mixing to prevent clipping

### API Reference

#### `JamTrackConfig`

Configuration for the jam track generator.

```rust
JamTrackConfig::new(key: String, mode: String, tempo: f64) -> JamTrackConfig
```

Properties:
- `key`: Musical key (e.g., "F#", "C", "Bb")
- `mode`: Modal scale (e.g., "Phrygian", "Dorian")
- `tempo`: Beats per minute (60-200)
- `octave`: Octave for chord voicing (default: 3)
- `beats_per_chord`: Duration of each chord (default: 4.0)

#### `JamTrackGenerator`

Main generator class.

Methods:
- `new(config: JamTrackConfig)`: Create a new generator
- `generate_samples()`: Generate audio samples as Float32Array
- `sample_rate()`: Get the sample rate (44100)
- `duration()`: Get the duration in seconds
- `get_progression_info()`: Get chord names as JSON string

#### Utility Functions

- `get_available_keys()`: Returns array of all available keys
- `get_available_modes()`: Returns array of all available modes

## Development

### Running Tests

```bash
cargo test
```

### Building for Production

```bash
wasm-pack build --target web --release
```

### Code Quality

```bash
# Format code
cargo fmt

# Lint
cargo clippy
```

## Examples

### Example 1: F# Phrygian at 150 BPM

```javascript
const config = new JamTrackConfig("F#", "Phrygian", 150);
const generator = new JamTrackGenerator(config);
```

Generates: F#m - G - F#m - E

### Example 2: C Dorian at 120 BPM

```javascript
const config = new JamTrackConfig("C", "Dorian", 120);
const generator = new JamTrackGenerator(config);
```

Generates: Cm - F - Cm - F

### Example 3: A Aeolian at 90 BPM

```javascript
const config = new JamTrackConfig("A", "Aeolian", 90);
const generator = new JamTrackGenerator(config);
```

Generates: Am - Dm - Am - Em

## Browser Compatibility

- Chrome 57+
- Firefox 52+
- Safari 11+
- Edge 16+

Requires WebAssembly and Web Audio API support.

## Performance

- **Build time**: ~5-10 seconds
- **WASM size**: ~50KB (optimized)
- **Generation time**: <100ms for a 4-chord progression
- **Memory usage**: Minimal (~1-2MB)

## Contributing

Contributions welcome! Please feel free to submit pull requests or open issues.

## License

See LICENSE file for details.

## Acknowledgments

- Built with [Rust](https://www.rust-lang.org/) and [wasm-pack](https://rustwasm.github.io/wasm-pack/)
- Web Audio API for browser audio playback
- Modal theory inspired by jazz and classical music traditions
