import os
import pretty_midi
import numpy as np

RAW_DIR = '../data/raw/'
OUT_DIR = '../data/parsed/'
os.makedirs(OUT_DIR, exist_ok=True)

# Drum note mapping — grouping hats together!
DRUM_CLASSES = {
    'kick': [35, 36],
    'snare': [38, 40],
    'closed_hat': [42, 44, 46], 
    'crash': [49, 57],
    'low_tom': [45, 41, 43]
}

def extract_drum_pattern(mid_file):
    midi = pretty_midi.PrettyMIDI(mid_file)
    pattern = []

    for instrument in midi.instruments:
        if not instrument.is_drum:
            continue

        frame = {}
        for note in instrument.notes:
            start_step = int(note.start / 0.5)  # fixed grid
            while len(pattern) <= start_step:
                pattern.append({k: 0 for k in DRUM_CLASSES.keys()})

            for drum_name, note_list in DRUM_CLASSES.items():
                if note.pitch in note_list:
                    pattern[start_step][drum_name] = 1

    return np.array([[beat.get(k, 0) for k in DRUM_CLASSES.keys()] for beat in pattern])

for genre in os.listdir(RAW_DIR):
    genre_path = os.path.join(RAW_DIR, genre)
    if not os.path.isdir(genre_path):
        continue

    for midi_file in os.listdir(genre_path):
        if not midi_file.endswith('.mid'):
            continue
        path = os.path.join(genre_path, midi_file)
        try:
            matrix = extract_drum_pattern(path)
            name = f"{genre}_{os.path.splitext(midi_file)[0]}.npy"
            np.save(os.path.join(OUT_DIR, name), matrix)
            print(f"✅ Saved {name} | Steps: {matrix.shape[0]}")
        except Exception as e:
            print(f"⚠️ Failed on {midi_file}: {e}")
