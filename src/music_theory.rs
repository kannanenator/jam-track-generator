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

    /// Get guitar chord tab/fingering for this chord
    pub fn get_guitar_tab(&self) -> Option<ChordTab> {
        get_chord_tab(&self.name)
    }
}

/// Represents a guitar chord fingering
/// Strings are ordered from low E to high E: [E, A, D, G, B, E]
/// -1 means don't play that string (muted)
/// 0 means play open string
/// 1+ means fret number
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChordTab {
    pub name: String,
    pub fingers: Vec<i8>, // Fret positions for each string (low E to high E)
    pub base_fret: u8,    // Starting fret (for barre chords)
}

impl ChordTab {
    pub fn new(name: String, fingers: Vec<i8>, base_fret: u8) -> Self {
        ChordTab {
            name,
            fingers,
            base_fret,
        }
    }
}

/// Get guitar chord tab for a chord name
pub fn get_chord_tab(chord_name: &str) -> Option<ChordTab> {
    // Standard guitar chord fingerings
    // Format: [E, A, D, G, B, E] from low to high
    match chord_name {
        // C chords
        "C" => Some(ChordTab::new("C".to_string(), vec![-1, 3, 2, 0, 1, 0], 0)),
        "Cm" => Some(ChordTab::new("Cm".to_string(), vec![-1, 3, 5, 5, 4, 3], 0)),
        "Cdim" => Some(ChordTab::new("Cdim".to_string(), vec![-1, 3, 4, 5, 4, -1], 0)),

        // C# / Db chords
        "C#" => Some(ChordTab::new("C#".to_string(), vec![-1, 4, 6, 6, 6, 4], 0)),
        "C#m" => Some(ChordTab::new("C#m".to_string(), vec![-1, 4, 6, 6, 5, 4], 0)),
        "C#dim" => Some(ChordTab::new("C#dim".to_string(), vec![-1, 4, 5, 6, 5, -1], 0)),

        // D chords
        "D" => Some(ChordTab::new("D".to_string(), vec![-1, -1, 0, 2, 3, 2], 0)),
        "Dm" => Some(ChordTab::new("Dm".to_string(), vec![-1, -1, 0, 2, 3, 1], 0)),
        "Ddim" => Some(ChordTab::new("Ddim".to_string(), vec![-1, -1, 0, 1, 3, 1], 0)),

        // D# / Eb chords
        "D#" => Some(ChordTab::new("D#".to_string(), vec![-1, -1, 1, 3, 4, 3], 0)),
        "D#m" => Some(ChordTab::new("D#m".to_string(), vec![-1, -1, 1, 3, 4, 2], 0)),
        "D#dim" => Some(ChordTab::new("D#dim".to_string(), vec![-1, -1, 1, 2, 4, 2], 0)),

        // E chords
        "E" => Some(ChordTab::new("E".to_string(), vec![0, 2, 2, 1, 0, 0], 0)),
        "Em" => Some(ChordTab::new("Em".to_string(), vec![0, 2, 2, 0, 0, 0], 0)),
        "Edim" => Some(ChordTab::new("Edim".to_string(), vec![0, 1, 2, 0, 2, 0], 0)),

        // F chords
        "F" => Some(ChordTab::new("F".to_string(), vec![1, 3, 3, 2, 1, 1], 0)),
        "Fm" => Some(ChordTab::new("Fm".to_string(), vec![1, 3, 3, 1, 1, 1], 0)),
        "Fdim" => Some(ChordTab::new("Fdim".to_string(), vec![1, 2, 3, 1, 3, 1], 0)),

        // F# / Gb chords
        "F#" => Some(ChordTab::new("F#".to_string(), vec![2, 4, 4, 3, 2, 2], 0)),
        "F#m" => Some(ChordTab::new("F#m".to_string(), vec![2, 4, 4, 2, 2, 2], 0)),
        "F#dim" => Some(ChordTab::new("F#dim".to_string(), vec![2, 3, 4, 2, 4, 2], 0)),

        // G chords
        "G" => Some(ChordTab::new("G".to_string(), vec![3, 2, 0, 0, 0, 3], 0)),
        "Gm" => Some(ChordTab::new("Gm".to_string(), vec![3, 5, 5, 3, 3, 3], 0)),
        "Gdim" => Some(ChordTab::new("Gdim".to_string(), vec![3, 4, 5, 3, 5, 3], 0)),

        // G# / Ab chords
        "G#" => Some(ChordTab::new("G#".to_string(), vec![4, 6, 6, 5, 4, 4], 0)),
        "G#m" => Some(ChordTab::new("G#m".to_string(), vec![4, 6, 6, 4, 4, 4], 0)),
        "G#dim" => Some(ChordTab::new("G#dim".to_string(), vec![4, 5, 6, 4, 6, 4], 0)),

        // A chords
        "A" => Some(ChordTab::new("A".to_string(), vec![-1, 0, 2, 2, 2, 0], 0)),
        "Am" => Some(ChordTab::new("Am".to_string(), vec![-1, 0, 2, 2, 1, 0], 0)),
        "Adim" => Some(ChordTab::new("Adim".to_string(), vec![-1, 0, 1, 2, 1, -1], 0)),

        // A# / Bb chords
        "A#" => Some(ChordTab::new("A#".to_string(), vec![-1, 1, 3, 3, 3, 1], 0)),
        "A#m" => Some(ChordTab::new("A#m".to_string(), vec![-1, 1, 3, 3, 2, 1], 0)),
        "A#dim" => Some(ChordTab::new("A#dim".to_string(), vec![-1, 1, 2, 3, 2, -1], 0)),

        // B chords
        "B" => Some(ChordTab::new("B".to_string(), vec![-1, 2, 4, 4, 4, 2], 0)),
        "Bm" => Some(ChordTab::new("Bm".to_string(), vec![-1, 2, 4, 4, 3, 2], 0)),
        "Bdim" => Some(ChordTab::new("Bdim".to_string(), vec![-1, 2, 3, 4, 3, -1], 0)),

        _ => None,
    }
}

/// Get multiple progression variations for a given mode
fn get_progression_variations(root: Note, mode: Mode) -> Vec<Vec<Chord>> {
    let scale = mode.scale(root);

    match mode {
        Mode::Phrygian => {
            vec![
                // Variation 1: Classic Phrygian vamp
                vec![
                    Chord::minor(scale[0]),  // i
                    Chord::major(scale[1]),  // bII
                    Chord::minor(scale[0]),  // i
                    Chord::major(scale[6]),  // bVII
                ],
                // Variation 2: Extended vamp
                vec![
                    Chord::minor(scale[0]),  // i
                    Chord::major(scale[1]),  // bII
                    Chord::major(scale[6]),  // bVII
                    Chord::major(scale[1]),  // bII
                ],
                // Variation 3: Dark progression
                vec![
                    Chord::minor(scale[0]),  // i
                    Chord::major(scale[6]),  // bVII
                    Chord::major(scale[5]),  // bVI
                    Chord::major(scale[1]),  // bII
                ],
            ]
        }
        Mode::Dorian => {
            vec![
                // Variation 1: Classic Dorian
                vec![
                    Chord::minor(scale[0]),  // i
                    Chord::major(scale[3]),  // IV
                    Chord::minor(scale[0]),  // i
                    Chord::major(scale[3]),  // IV
                ],
                // Variation 2: Full Dorian sound
                vec![
                    Chord::minor(scale[0]),  // i
                    Chord::minor(scale[3]),  // iv
                    Chord::major(scale[4]),  // V
                    Chord::major(scale[3]),  // IV
                ],
                // Variation 3: Modal interchange
                vec![
                    Chord::minor(scale[0]),  // i
                    Chord::major(scale[6]),  // VII
                    Chord::major(scale[3]),  // IV
                    Chord::minor(scale[4]),  // v
                ],
            ]
        }
        Mode::Lydian => {
            vec![
                // Variation 1: Classic Lydian
                vec![
                    Chord::major(scale[0]),  // I
                    Chord::major(scale[1]),  // II
                    Chord::major(scale[0]),  // I
                    Chord::major(scale[1]),  // II
                ],
                // Variation 2: Dreamy progression
                vec![
                    Chord::major(scale[0]),  // I
                    Chord::major(scale[1]),  // II
                    Chord::minor(scale[5]),  // vi
                    Chord::major(scale[1]),  // II
                ],
                // Variation 3: Bright progression
                vec![
                    Chord::major(scale[0]),  // I
                    Chord::major(scale[4]),  // V
                    Chord::major(scale[1]),  // II
                    Chord::major(scale[4]),  // V
                ],
            ]
        }
        Mode::Mixolydian => {
            vec![
                // Variation 1: Classic Mixolydian
                vec![
                    Chord::major(scale[0]),  // I
                    Chord::major(scale[6]),  // bVII
                    Chord::major(scale[0]),  // I
                    Chord::major(scale[6]),  // bVII
                ],
                // Variation 2: Bluesy progression
                vec![
                    Chord::major(scale[0]),  // I
                    Chord::major(scale[6]),  // bVII
                    Chord::major(scale[3]),  // IV
                    Chord::major(scale[6]),  // bVII
                ],
                // Variation 3: Rock progression
                vec![
                    Chord::major(scale[0]),  // I
                    Chord::major(scale[3]),  // IV
                    Chord::major(scale[6]),  // bVII
                    Chord::major(scale[3]),  // IV
                ],
            ]
        }
        Mode::Aeolian => {
            vec![
                // Variation 1: Classic minor
                vec![
                    Chord::minor(scale[0]),  // i
                    Chord::minor(scale[3]),  // iv
                    Chord::minor(scale[0]),  // i
                    Chord::minor(scale[4]),  // v
                ],
                // Variation 2: Descending bass
                vec![
                    Chord::minor(scale[0]),  // i
                    Chord::major(scale[6]),  // VII
                    Chord::major(scale[5]),  // VI
                    Chord::major(scale[4]),  // V
                ],
                // Variation 3: Emotional progression
                vec![
                    Chord::minor(scale[0]),  // i
                    Chord::major(scale[5]),  // VI
                    Chord::major(scale[3]),  // III
                    Chord::major(scale[6]),  // VII
                ],
            ]
        }
        Mode::Ionian => {
            vec![
                // Variation 1: Classic I-IV-I-V
                vec![
                    Chord::major(scale[0]),  // I
                    Chord::major(scale[3]),  // IV
                    Chord::major(scale[0]),  // I
                    Chord::major(scale[4]),  // V
                ],
                // Variation 2: I-V-vi-IV (pop progression)
                vec![
                    Chord::major(scale[0]),  // I
                    Chord::major(scale[4]),  // V
                    Chord::minor(scale[5]),  // vi
                    Chord::major(scale[3]),  // IV
                ],
                // Variation 3: Circle progression
                vec![
                    Chord::major(scale[0]),  // I
                    Chord::minor(scale[5]),  // vi
                    Chord::major(scale[3]),  // IV
                    Chord::major(scale[4]),  // V
                ],
            ]
        }
        Mode::Locrian => {
            vec![
                // Variation 1: Classic Locrian
                vec![
                    Chord::diminished(scale[0]),  // i°
                    Chord::major(scale[1]),       // bII
                    Chord::diminished(scale[0]),  // i°
                    Chord::major(scale[4]),       // bV
                ],
                // Variation 2: Unstable progression
                vec![
                    Chord::diminished(scale[0]),  // i°
                    Chord::major(scale[4]),       // bV
                    Chord::major(scale[1]),       // bII
                    Chord::major(scale[4]),       // bV
                ],
                // Variation 3: Dark progression
                vec![
                    Chord::diminished(scale[0]),  // i°
                    Chord::major(scale[1]),       // bII
                    Chord::minor(scale[2]),       // ii
                    Chord::major(scale[4]),       // bV
                ],
            ]
        }
    }
}

/// Generate a random chord progression for a given mode
/// Uses a pseudo-random selection based on the current timestamp
pub fn generate_modal_progression(root: Note, mode: Mode) -> Vec<Chord> {
    let variations = get_progression_variations(root, mode);

    // Use a simple pseudo-random selection based on time
    // This is deterministic within the same millisecond but varies across calls
    let timestamp = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis();

    let index = (timestamp % variations.len() as u128) as usize;
    variations[index].clone()
}

/// Generate a specific variation of a chord progression (0-based index)
pub fn generate_modal_progression_variation(root: Note, mode: Mode, variation: usize) -> Vec<Chord> {
    let variations = get_progression_variations(root, mode);
    let index = variation % variations.len();
    variations[index].clone()
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
