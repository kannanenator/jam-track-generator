use serde::{Deserialize, Serialize};
use std::fmt;

/// Represents a musical note
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum Note {
    C = 0,
    CSharp = 1,
    D = 2,
    DSharp = 3,
    E = 4,
    F = 5,
    FSharp = 6,
    G = 7,
    GSharp = 8,
    A = 9,
    ASharp = 10,
    B = 11,
}

impl Note {
    /// Parse a note from a string (e.g., "F#", "Gb", "C")
    pub fn from_string(s: &str) -> Option<Self> {
        match s.to_uppercase().as_str() {
            "C" => Some(Note::C),
            "C#" | "DB" => Some(Note::CSharp),
            "D" => Some(Note::D),
            "D#" | "EB" => Some(Note::DSharp),
            "E" | "FB" => Some(Note::E),
            "F" | "E#" => Some(Note::F),
            "F#" | "GB" => Some(Note::FSharp),
            "G" => Some(Note::G),
            "G#" | "AB" => Some(Note::GSharp),
            "A" => Some(Note::A),
            "A#" | "BB" => Some(Note::ASharp),
            "B" | "CB" => Some(Note::B),
            _ => None,
        }
    }

    /// Get the note as a semitone value (0-11)
    pub fn semitone(&self) -> u8 {
        *self as u8
    }

    /// Transpose a note by a number of semitones
    pub fn transpose(&self, semitones: i32) -> Note {
        let new_value = (self.semitone() as i32 + semitones).rem_euclid(12);
        Note::from_semitone(new_value as u8)
    }

    /// Create a note from a semitone value (0-11)
    pub fn from_semitone(semitone: u8) -> Note {
        match semitone % 12 {
            0 => Note::C,
            1 => Note::CSharp,
            2 => Note::D,
            3 => Note::DSharp,
            4 => Note::E,
            5 => Note::F,
            6 => Note::FSharp,
            7 => Note::G,
            8 => Note::GSharp,
            9 => Note::A,
            10 => Note::ASharp,
            11 => Note::B,
            _ => unreachable!(),
        }
    }

    /// Get frequency for a note at a given octave (A4 = 440Hz)
    pub fn frequency(&self, octave: u8) -> f64 {
        let a4 = 440.0;
        let semitones_from_a4 = (octave as i32 - 4) * 12 + (self.semitone() as i32 - 9);
        a4 * 2_f64.powf(semitones_from_a4 as f64 / 12.0)
    }
}

impl fmt::Display for Note {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let name = match self {
            Note::C => "C",
            Note::CSharp => "C#",
            Note::D => "D",
            Note::DSharp => "D#",
            Note::E => "E",
            Note::F => "F",
            Note::FSharp => "F#",
            Note::G => "G",
            Note::GSharp => "G#",
            Note::A => "A",
            Note::ASharp => "A#",
            Note::B => "B",
        };
        write!(f, "{}", name)
    }
}

/// Musical modes with their interval patterns
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum Mode {
    Ionian,      // Major scale: W-W-H-W-W-W-H
    Dorian,      // W-H-W-W-W-H-W
    Phrygian,    // H-W-W-W-H-W-W
    Lydian,      // W-W-W-H-W-W-H
    Mixolydian,  // W-W-H-W-W-H-W
    Aeolian,     // Natural minor: W-H-W-W-H-W-W
    Locrian,     // H-W-W-H-W-W-W
}

impl Mode {
    /// Get the interval pattern for the mode (in semitones from root)
    pub fn intervals(&self) -> Vec<u8> {
        match self {
            Mode::Ionian => vec![0, 2, 4, 5, 7, 9, 11],
            Mode::Dorian => vec![0, 2, 3, 5, 7, 9, 10],
            Mode::Phrygian => vec![0, 1, 3, 5, 7, 8, 10],
            Mode::Lydian => vec![0, 2, 4, 6, 7, 9, 11],
            Mode::Mixolydian => vec![0, 2, 4, 5, 7, 9, 10],
            Mode::Aeolian => vec![0, 2, 3, 5, 7, 8, 10],
            Mode::Locrian => vec![0, 1, 3, 5, 6, 8, 10],
        }
    }

    /// Parse mode from string
    pub fn from_string(s: &str) -> Option<Self> {
        match s.to_lowercase().as_str() {
            "ionian" | "major" => Some(Mode::Ionian),
            "dorian" => Some(Mode::Dorian),
            "phrygian" => Some(Mode::Phrygian),
            "lydian" => Some(Mode::Lydian),
            "mixolydian" => Some(Mode::Mixolydian),
            "aeolian" | "minor" => Some(Mode::Aeolian),
            "locrian" => Some(Mode::Locrian),
            _ => None,
        }
    }

    /// Get the scale notes for this mode starting from a root note
    pub fn scale(&self, root: Note) -> Vec<Note> {
        self.intervals()
            .iter()
            .map(|&interval| root.transpose(interval as i32))
            .collect()
    }
}

impl fmt::Display for Mode {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let name = match self {
            Mode::Ionian => "Ionian",
            Mode::Dorian => "Dorian",
            Mode::Phrygian => "Phrygian",
            Mode::Lydian => "Lydian",
            Mode::Mixolydian => "Mixolydian",
            Mode::Aeolian => "Aeolian",
            Mode::Locrian => "Locrian",
        };
        write!(f, "{}", name)
    }
}

/// Represents a chord
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Chord {
    pub root: Note,
    pub intervals: Vec<u8>,
    pub name: String,
}

impl Chord {
    /// Create a new chord
    pub fn new(root: Note, intervals: Vec<u8>, name: String) -> Self {
        Chord {
            root,
            intervals,
            name,
        }
    }

    /// Get all notes in the chord
    pub fn notes(&self) -> Vec<Note> {
        self.intervals
            .iter()
            .map(|&interval| self.root.transpose(interval as i32))
            .collect()
    }

    /// Get frequencies for all notes in the chord at a given octave
    pub fn frequencies(&self, octave: u8) -> Vec<f64> {
        self.notes()
            .iter()
            .map(|note| note.frequency(octave))
            .collect()
    }

    /// Create a major chord
    pub fn major(root: Note) -> Self {
        Chord::new(root, vec![0, 4, 7], format!("{}", root))
    }

    /// Create a minor chord
    pub fn minor(root: Note) -> Self {
        Chord::new(root, vec![0, 3, 7], format!("{}m", root))
    }

    /// Create a diminished chord
    pub fn diminished(root: Note) -> Self {
        Chord::new(root, vec![0, 3, 6], format!("{}dim", root))
    }

    /// Create a suspended 2 chord
    pub fn sus2(root: Note) -> Self {
        Chord::new(root, vec![0, 2, 7], format!("{}sus2", root))
    }

    /// Create a suspended 4 chord
    pub fn sus4(root: Note) -> Self {
        Chord::new(root, vec![0, 5, 7], format!("{}sus4", root))
    }

    /// Create a power chord (root and fifth)
    pub fn power(root: Note) -> Self {
        Chord::new(root, vec![0, 7], format!("{}5", root))
    }
}

/// Generate a chord progression for a given mode
pub fn generate_modal_progression(root: Note, mode: Mode) -> Vec<Chord> {
    let scale = mode.scale(root);

    // Generate triads based on the mode's characteristic intervals
    match mode {
        Mode::Phrygian => {
            // Phrygian: emphasize the b2 and minor quality
            // Common progression: i - bII - i - bVII
            vec![
                Chord::minor(scale[0]),  // i
                Chord::major(scale[1]),  // bII
                Chord::minor(scale[0]),  // i
                Chord::major(scale[6]),  // bVII
            ]
        }
        Mode::Dorian => {
            // Dorian: emphasize the major VI
            // Common progression: i - IV - i - IV
            vec![
                Chord::minor(scale[0]),  // i
                Chord::major(scale[3]),  // IV
                Chord::minor(scale[0]),  // i
                Chord::major(scale[3]),  // IV
            ]
        }
        Mode::Lydian => {
            // Lydian: emphasize the #4
            // Common progression: I - II - I - II
            vec![
                Chord::major(scale[0]),  // I
                Chord::major(scale[1]),  // II
                Chord::major(scale[0]),  // I
                Chord::major(scale[1]),  // II
            ]
        }
        Mode::Mixolydian => {
            // Mixolydian: emphasize the b7
            // Common progression: I - bVII - I - bVII
            vec![
                Chord::major(scale[0]),  // I
                Chord::major(scale[6]),  // bVII
                Chord::major(scale[0]),  // I
                Chord::major(scale[6]),  // bVII
            ]
        }
        Mode::Aeolian => {
            // Aeolian (natural minor): classic minor progression
            // Common progression: i - iv - i - v
            vec![
                Chord::minor(scale[0]),  // i
                Chord::minor(scale[3]),  // iv
                Chord::minor(scale[0]),  // i
                Chord::minor(scale[4]),  // v
            ]
        }
        Mode::Ionian => {
            // Ionian (major): classic major progression
            // Common progression: I - IV - I - V
            vec![
                Chord::major(scale[0]),  // I
                Chord::major(scale[3]),  // IV
                Chord::major(scale[0]),  // I
                Chord::major(scale[4]),  // V
            ]
        }
        Mode::Locrian => {
            // Locrian: emphasize the diminished quality
            // Common progression: i° - bII - i° - bV
            vec![
                Chord::diminished(scale[0]),  // i°
                Chord::major(scale[1]),       // bII
                Chord::diminished(scale[0]),  // i°
                Chord::major(scale[4]),       // bV
            ]
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_note_parsing() {
        assert_eq!(Note::from_string("F#"), Some(Note::FSharp));
        assert_eq!(Note::from_string("Gb"), Some(Note::FSharp));
        assert_eq!(Note::from_string("C"), Some(Note::C));
    }

    #[test]
    fn test_transpose() {
        assert_eq!(Note::C.transpose(2), Note::D);
        assert_eq!(Note::B.transpose(1), Note::C);
        assert_eq!(Note::C.transpose(-2), Note::ASharp);
    }

    #[test]
    fn test_mode_scale() {
        let scale = Mode::Phrygian.scale(Note::E);
        let expected = vec![
            Note::E,
            Note::F,
            Note::G,
            Note::A,
            Note::B,
            Note::C,
            Note::D,
        ];
        assert_eq!(scale, expected);
    }

    #[test]
    fn test_chord_notes() {
        let chord = Chord::minor(Note::A);
        let notes = chord.notes();
        assert_eq!(notes, vec![Note::A, Note::C, Note::E]);
    }
}
