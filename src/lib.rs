mod audio;
mod music_theory;

use audio::{generate_progression_samples, SAMPLE_RATE};
use music_theory::{generate_modal_progression, Mode, Note};
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
extern "C" {
    #[wasm_bindgen(js_namespace = console)]
    fn log(s: &str);
}

macro_rules! console_log {
    ($($t:tt)*) => (log(&format_args!($($t)*).to_string()))
}

/// Configuration for the jam track generator
#[wasm_bindgen]
#[derive(Debug, Clone)]
pub struct JamTrackConfig {
    key: String,
    mode: String,
    tempo: f64,
    octave: u8,
    beats_per_chord: f64,
}

#[wasm_bindgen]
impl JamTrackConfig {
    #[wasm_bindgen(constructor)]
    pub fn new(key: String, mode: String, tempo: f64) -> Result<JamTrackConfig, JsValue> {
        Ok(JamTrackConfig {
            key,
            mode,
            tempo,
            octave: 3,
            beats_per_chord: 4.0,
        })
    }

    #[wasm_bindgen(getter)]
    pub fn key(&self) -> String {
        self.key.clone()
    }

    #[wasm_bindgen(setter)]
    pub fn set_key(&mut self, key: String) {
        self.key = key;
    }

    #[wasm_bindgen(getter)]
    pub fn mode(&self) -> String {
        self.mode.clone()
    }

    #[wasm_bindgen(setter)]
    pub fn set_mode(&mut self, mode: String) {
        self.mode = mode;
    }

    #[wasm_bindgen(getter)]
    pub fn tempo(&self) -> f64 {
        self.tempo
    }

    #[wasm_bindgen(setter)]
    pub fn set_tempo(&mut self, tempo: f64) {
        self.tempo = tempo;
    }

    #[wasm_bindgen(getter)]
    pub fn octave(&self) -> u8 {
        self.octave
    }

    #[wasm_bindgen(setter)]
    pub fn set_octave(&mut self, octave: u8) {
        self.octave = octave;
    }

    #[wasm_bindgen(getter)]
    pub fn beats_per_chord(&self) -> f64 {
        self.beats_per_chord
    }

    #[wasm_bindgen(setter)]
    pub fn set_beats_per_chord(&mut self, beats: f64) {
        self.beats_per_chord = beats;
    }
}

/// The main jam track generator
#[wasm_bindgen]
pub struct JamTrackGenerator {
    config: JamTrackConfig,
}

#[wasm_bindgen]
impl JamTrackGenerator {
    #[wasm_bindgen(constructor)]
    pub fn new(config: JamTrackConfig) -> Result<JamTrackGenerator, JsValue> {
        console_log!("Creating JamTrackGenerator with key: {}, mode: {}, tempo: {}",
                     config.key, config.mode, config.tempo);
        Ok(JamTrackGenerator { config })
    }

    /// Generate audio samples for the jam track
    #[wasm_bindgen]
    pub fn generate_samples(&self) -> Result<Vec<f32>, JsValue> {
        // Parse the key
        let root = Note::from_string(&self.config.key)
            .ok_or_else(|| JsValue::from_str(&format!("Invalid key: {}", self.config.key)))?;

        // Parse the mode
        let mode = Mode::from_string(&self.config.mode)
            .ok_or_else(|| JsValue::from_str(&format!("Invalid mode: {}", self.config.mode)))?;

        console_log!("Generating progression for {} {}", root, mode);

        // Generate the chord progression
        let progression = generate_modal_progression(root, mode);

        console_log!("Generated {} chords", progression.len());

        // Log the chord progression
        for (i, chord) in progression.iter().enumerate() {
            console_log!("Chord {}: {}", i + 1, chord.name);
        }

        // Generate audio samples
        let samples = generate_progression_samples(
            &progression,
            self.config.octave,
            self.config.tempo,
            self.config.beats_per_chord,
        );

        console_log!("Generated {} samples", samples.len());

        Ok(samples)
    }

    /// Get the sample rate
    #[wasm_bindgen]
    pub fn sample_rate(&self) -> f64 {
        SAMPLE_RATE
    }

    /// Get the duration of the generated track in seconds
    #[wasm_bindgen]
    pub fn duration(&self) -> f64 {
        let seconds_per_beat = 60.0 / self.config.tempo;
        let num_chords = 4.0; // We generate 4 chords
        num_chords * self.config.beats_per_chord * seconds_per_beat
    }

    /// Get the chord progression as a JSON string
    #[wasm_bindgen]
    pub fn get_progression_info(&self) -> Result<String, JsValue> {
        let root = Note::from_string(&self.config.key)
            .ok_or_else(|| JsValue::from_str(&format!("Invalid key: {}", self.config.key)))?;

        let mode = Mode::from_string(&self.config.mode)
            .ok_or_else(|| JsValue::from_str(&format!("Invalid mode: {}", self.config.mode)))?;

        let progression = generate_modal_progression(root, mode);

        let chord_names: Vec<String> = progression.iter().map(|c| c.name.clone()).collect();

        serde_json::to_string(&chord_names)
            .map_err(|e| JsValue::from_str(&format!("Serialization error: {}", e)))
    }

    /// Get chord tabs (guitar fingerings) for the progression as JSON
    #[wasm_bindgen]
    pub fn get_chord_tabs(&self) -> Result<String, JsValue> {
        let root = Note::from_string(&self.config.key)
            .ok_or_else(|| JsValue::from_str(&format!("Invalid key: {}", self.config.key)))?;

        let mode = Mode::from_string(&self.config.mode)
            .ok_or_else(|| JsValue::from_str(&format!("Invalid mode: {}", self.config.mode)))?;

        let progression = generate_modal_progression(root, mode);

        let chord_tabs: Vec<_> = progression
            .iter()
            .map(|chord| chord.get_guitar_tab())
            .collect();

        serde_json::to_string(&chord_tabs)
            .map_err(|e| JsValue::from_str(&format!("Serialization error: {}", e)))
    }

    /// Update the configuration
    #[wasm_bindgen]
    pub fn update_config(&mut self, config: JamTrackConfig) {
        self.config = config;
    }
}

/// Get a list of available modes
#[wasm_bindgen]
pub fn get_available_modes() -> Vec<String> {
    vec![
        "Ionian".to_string(),
        "Dorian".to_string(),
        "Phrygian".to_string(),
        "Lydian".to_string(),
        "Mixolydian".to_string(),
        "Aeolian".to_string(),
        "Locrian".to_string(),
    ]
}

/// Get a list of available keys
#[wasm_bindgen]
pub fn get_available_keys() -> Vec<String> {
    vec![
        "C".to_string(),
        "C#".to_string(),
        "D".to_string(),
        "D#".to_string(),
        "E".to_string(),
        "F".to_string(),
        "F#".to_string(),
        "G".to_string(),
        "G#".to_string(),
        "A".to_string(),
        "A#".to_string(),
        "B".to_string(),
    ]
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_jam_track_config() {
        let config = JamTrackConfig::new("F#".to_string(), "Phrygian".to_string(), 150.0).unwrap();
        assert_eq!(config.key(), "F#");
        assert_eq!(config.mode(), "Phrygian");
        assert_eq!(config.tempo(), 150.0);
    }

    #[test]
    fn test_generator_creation() {
        let config = JamTrackConfig::new("C".to_string(), "Dorian".to_string(), 120.0).unwrap();
        let generator = JamTrackGenerator::new(config).unwrap();
        assert_eq!(generator.sample_rate(), SAMPLE_RATE);
    }

    #[test]
    fn test_sample_generation() {
        let config = JamTrackConfig::new("A".to_string(), "Aeolian".to_string(), 100.0).unwrap();
        let generator = JamTrackGenerator::new(config).unwrap();
        let samples = generator.generate_samples().unwrap();
        assert!(!samples.is_empty());
    }
}
