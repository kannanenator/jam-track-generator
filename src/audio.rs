use crate::music_theory::Chord;
use std::f64::consts::PI;

/// Audio sample rate (44.1kHz is standard)
pub const SAMPLE_RATE: f64 = 44100.0;

/// Generate audio samples for a chord
pub fn generate_chord_samples(
    chord: &Chord,
    octave: u8,
    duration_seconds: f64,
    attack: f64,
    decay: f64,
    sustain: f64,
    release: f64,
) -> Vec<f32> {
    let num_samples = (duration_seconds * SAMPLE_RATE) as usize;
    let mut samples = vec![0.0_f32; num_samples];

    let frequencies = chord.frequencies(octave);

    // Generate samples for each note in the chord
    for &freq in &frequencies {
        let note_samples = generate_tone_with_envelope(
            freq,
            duration_seconds,
            attack,
            decay,
            sustain,
            release,
        );

        // Mix the note into the chord
        for (i, &sample) in note_samples.iter().enumerate() {
            if i < samples.len() {
                samples[i] += sample / frequencies.len() as f32;
            }
        }
    }

    samples
}

/// Generate a tone with ADSR envelope
fn generate_tone_with_envelope(
    frequency: f64,
    duration_seconds: f64,
    attack: f64,
    decay: f64,
    sustain_level: f64,
    release: f64,
) -> Vec<f32> {
    let num_samples = (duration_seconds * SAMPLE_RATE) as usize;
    let mut samples = vec![0.0_f32; num_samples];

    let attack_samples = (attack * SAMPLE_RATE) as usize;
    let decay_samples = (decay * SAMPLE_RATE) as usize;
    let release_samples = (release * SAMPLE_RATE) as usize;
    let sustain_samples = num_samples.saturating_sub(attack_samples + decay_samples + release_samples);

    for i in 0..num_samples {
        let t = i as f64 / SAMPLE_RATE;

        // Generate base waveform (mix of sine waves for a warmer sound)
        let fundamental = (2.0 * PI * frequency * t).sin();
        let harmonic2 = 0.3 * (2.0 * PI * frequency * 2.0 * t).sin();
        let harmonic3 = 0.1 * (2.0 * PI * frequency * 3.0 * t).sin();
        let wave = fundamental + harmonic2 + harmonic3;

        // Apply ADSR envelope
        let envelope = if i < attack_samples {
            // Attack phase
            i as f64 / attack_samples as f64
        } else if i < attack_samples + decay_samples {
            // Decay phase
            let decay_progress = (i - attack_samples) as f64 / decay_samples as f64;
            1.0 - (1.0 - sustain_level) * decay_progress
        } else if i < attack_samples + decay_samples + sustain_samples {
            // Sustain phase
            sustain_level
        } else {
            // Release phase
            let release_progress = (i - attack_samples - decay_samples - sustain_samples) as f64
                / release_samples as f64;
            sustain_level * (1.0 - release_progress)
        };

        samples[i] = (wave * envelope * 0.3) as f32;
    }

    samples
}

/// Generate samples for an entire progression
pub fn generate_progression_samples(
    chords: &[Chord],
    octave: u8,
    tempo: f64,
    beats_per_chord: f64,
) -> Vec<f32> {
    let seconds_per_beat = 60.0 / tempo;
    let chord_duration = seconds_per_beat * beats_per_chord;

    // ADSR envelope parameters (in seconds)
    let attack = 0.01;
    let decay = 0.1;
    let sustain = 0.7;
    let release = chord_duration * 0.3;

    let mut all_samples = Vec::new();

    for chord in chords {
        let chord_samples = generate_chord_samples(
            chord,
            octave,
            chord_duration,
            attack,
            decay,
            sustain,
            release,
        );
        all_samples.extend(chord_samples);
    }

    all_samples
}

/// Mix multiple audio buffers together
pub fn mix_samples(buffers: Vec<Vec<f32>>) -> Vec<f32> {
    if buffers.is_empty() {
        return Vec::new();
    }

    let max_len = buffers.iter().map(|b| b.len()).max().unwrap_or(0);
    let num_buffers = buffers.len() as f32;
    let mut result = vec![0.0; max_len];

    for buffer in buffers {
        for (i, &sample) in buffer.iter().enumerate() {
            result[i] += sample / num_buffers;
        }
    }

    result
}

/// Apply a simple low-pass filter for smoothing
pub fn apply_lowpass_filter(samples: &[f32], cutoff_freq: f64) -> Vec<f32> {
    let rc = 1.0 / (2.0 * PI * cutoff_freq);
    let dt = 1.0 / SAMPLE_RATE;
    let alpha = dt / (rc + dt);

    let mut filtered = vec![0.0; samples.len()];
    filtered[0] = samples[0];

    for i in 1..samples.len() {
        filtered[i] = (filtered[i - 1] as f64 + alpha * (samples[i] as f64 - filtered[i - 1] as f64)) as f32;
    }

    filtered
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::music_theory::{Chord, Note};

    #[test]
    fn test_generate_chord_samples() {
        let chord = Chord::major(Note::C);
        let samples = generate_chord_samples(&chord, 4, 1.0, 0.01, 0.1, 0.7, 0.2);
        assert_eq!(samples.len(), SAMPLE_RATE as usize);
    }

    #[test]
    fn test_generate_progression() {
        let chords = vec![
            Chord::major(Note::C),
            Chord::major(Note::F),
        ];
        let samples = generate_progression_samples(&chords, 4, 120.0, 4.0);
        // Should have samples for 2 chords at 120 BPM, 4 beats each
        // 2 chords * 4 beats * (60/120) seconds/beat * 44100 samples/second
        let expected_len = (2.0 * 4.0 * (60.0 / 120.0) * SAMPLE_RATE) as usize;
        assert_eq!(samples.len(), expected_len);
    }
}
