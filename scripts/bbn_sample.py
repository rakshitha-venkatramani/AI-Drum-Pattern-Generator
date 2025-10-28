import pandas as pd
import os
from pretty_midi import PrettyMIDI, Instrument, Note, note_number_to_drum_name
from pgmpy.models import BayesianNetwork
from pgmpy.estimators import MaximumLikelihoodEstimator
from pgmpy.inference import VariableElimination
from pgmpy.sampling import BayesianModelSampling

# Load dataset
data = pd.read_csv('../data/sample_drum_data.csv')

# Build and train Bayesian Network
model = BayesianNetwork([
    ('style', 'kit'),
    ('bpm', 'kit'),
    ('kit', 'kick'),
    ('kit', 'snare'),
    ('kit', 'hihat'),
    ('kit', 'crash'),
    ('kit', 'tom')
])
model.fit(data, estimator=MaximumLikelihoodEstimator)
inference = VariableElimination(model)
sampler = BayesianModelSampling(model)

# 🎛 User input
style = input("Enter drum style (e.g., rock, jazz): ").strip().lower()
bpm_input = input("Enter tempo in BPM (e.g., 120): ").strip()

valid_styles = data["style"].unique().tolist()
valid_bpms = data["bpm"].unique().tolist()

if style not in valid_styles:
    print(f"⚠️ Unknown style '{style}'. Defaulting to '{valid_styles[0]}'")
    style = valid_styles[0]

try:
    bpm = int(bpm_input)
    if bpm not in valid_bpms:
        print(f"⚠️ Unknown BPM '{bpm}'. Defaulting to {valid_bpms[0]}")
        bpm = valid_bpms[0]
except ValueError:
    print("⚠️ Invalid BPM input. Defaulting to 120.")
    bpm = 120

# Generate sample pattern
steps = 12  # 3 bars
pattern_sequence = []

sample_data = sampler.rejection_sample(
    evidence=[("style", style), ("bpm", bpm)],
    size=steps
)

# Terminal Output
print("\nGenerated Drum Pattern Grid (1 = Hit, 0 = Silent):")
print("Step | KICK | SNARE | HIHAT | CRASH | TOM")
print("---------------------------------------------")

for i in range(steps):
    row = sample_data.iloc[i]

    pattern = {
        'kit': row['kit'],
        'kick': row['kick'],
        'snare': row['snare'],
        'hihat': row['hihat'],
        'crash': row['crash'],
        'tom': row['tom']
    }
    pattern_sequence.append(pattern)
    print(f"  {i+1:<2} |  {pattern['kick']}   |   {pattern['snare']}   |   {pattern['hihat']}   |   {pattern['crash']}    |   {pattern['tom']}")

# MIDI generation
def generate_midi_loop(pattern_sequence, bpm, filename="output/generated_loop.mid"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    midi = PrettyMIDI(initial_tempo=bpm)
    drum = Instrument(program=0, is_drum=True)

    mapping = {
        'kick': 36,
        'snare': 38,
        'hihat': 42,
        'crash': 49,
        'tom': 45
    }

    print("\n🎵 Drum Pattern Breakdown (MIDI Events):")
    for i, pattern in enumerate(pattern_sequence):
        for drum_part, value in pattern.items():
            if drum_part == 'kit' or value == 0:
                continue
            pitch = mapping[drum_part]
            import random
            # Only hi-hat gets swing
            if drum_part == "hihat":
                offset = random.uniform(-0.02, 0.02)  # ±20ms
            else:
                offset = 0

# Humanize velocity slightly for all
            velocity = random.randint(85, 110)

            start_time = i * 0.5
            end_time = start_time + 0.1
            note = Note(velocity=100, pitch=pitch, start=start_time, end=end_time)
            drum.notes.append(note)
            print(f"Time: {start_time:.2f}s | Drum: {note_number_to_drum_name(pitch)} | Velocity: 100")

    # Prevent cutoff
    dummy_note = Note(velocity=1, pitch=35, start=(len(pattern_sequence) * 0.5) + 0.1, end=(len(pattern_sequence) * 0.5) + 0.2)
    drum.notes.append(dummy_note)

    midi.instruments.append(drum)
    midi.write(filename)

# Save + Play
generate_midi_loop(pattern_sequence, bpm)
print("\n✅ Loop saved to output/generated_loop.mid")

output_path = os.path.abspath("output/generated_loop.mid")
print("🎧 Opening in Windows Media Player...")
os.startfile(output_path)
