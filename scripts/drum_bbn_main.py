import random
import joblib
from pgmpy.inference import VariableElimination
import os
from pretty_midi import PrettyMIDI, Instrument, Note

# === LOAD MODEL ===
STYLE = input("Enter drum style (rock, jazz, latin,..): ").strip().lower()
MODEL_PATH = f"../models/{STYLE}_model.pkl"

if not os.path.exists(MODEL_PATH):
    print(f"❌ Model for '{STYLE}' not found! Train it first.")
    exit()

model = joblib.load(MODEL_PATH)
inference = VariableElimination(model)

# === GENERATE PATTERN ===
print("\nGenerated Drum Pattern Grid (1 = Hit, 0 = Silent):")
print("Step | KICK | SNARE | CLOSED_HAT | CRASH | LOW_TOM")
print("-------------------------------------------")

pattern_sequence = []

for step in range(16):
    # Use sampling instead of always choosing the most probable hit
    sampled = inference.query(
        variables=['kick', 'snare', 'closed_hat', 'crash', 'low_tom']
    ).sample(n=1).to_dict('records')[0]

    pattern_sequence.append(sampled)

    print(f"{step + 1:>4} |  {sampled['kick']:>3} |  {sampled['snare']:>3} |"
          f"  {sampled['closed_hat']:>6} |  {sampled['crash']:>3} |  {sampled['low_tom']:>3}")

# === BUILD MIDI WITH SWING + VELOCITY ===
midi = PrettyMIDI()
drum_track = Instrument(program=0, is_drum=True)
note_map = {'kick': 36, 'snare': 38, 'closed_hat': 42, 'crash': 49, 'low_tom': 45}

for i, pattern in enumerate(pattern_sequence):
    for drum, hit in pattern.items():
        if hit:
            start = i * 0.5
            # Apply hi-hat swing
            if drum == 'closed_hat' and i % 2 == 1:
                start += random.uniform(0.02, 0.05)
            velocity = random.randint(85, 115)
            note = Note(
                velocity=velocity,
                pitch=note_map[drum],
                start=start,
                end=start + 0.1
            )
            drum_track.notes.append(note)

midi.instruments.append(drum_track)

# === SAVE & PLAY ===
os.makedirs("../output", exist_ok=True)
outfile = f"../output/generated_loop_{random.randint(10000,99999)}.mid"
midi.write(outfile)

print(f"\n✅ Loop saved to {os.path.abspath(outfile)}")

try:
    os.startfile(os.path.abspath(outfile))
except Exception as e:
    print(f"⚠️ Could not open file automatically: {e}")

from fitness import fitness_function

# Example: generated drum pattern from your Bayesian model
generated_pattern = ['Kick', 'Snare', 'Kick', 'Snare']

# Example: training dataset statistics (replace with your real values!)
training_stats = {
    'density': 4,
    'instrument_distribution': {'Kick': 0.5, 'Snare': 0.5}
}

expected_positions = {'Kick': [0, 2], 'Snare': [1, 3]}

# Evaluate the fitness
score = fitness_function(generated_pattern, training_stats, expected_positions)

print(f"Pattern: {generated_pattern}")
print(f"Fitness Score: {score:.2f}")

# Optional: automatic rejection logic
if score < 0.7:
    print("Rejected: Pattern quality too low. Rerunning generation...")
else:
    print("Accepted: Pattern quality is good!")
