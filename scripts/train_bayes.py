import os
import pickle
import numpy as np
import pandas as pd
from pgmpy.models import BayesianNetwork
from pgmpy.estimators import MaximumLikelihoodEstimator
import joblib

DATA_DIR = '../data/parsed'
OUTPUT_DIR = '../models'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_genre_data(genre):
    files = [f for f in os.listdir(DATA_DIR) if f.lower().startswith(genre.lower()) and f.endswith('.npy')]
    all_data = []
    for file in files:
        path = os.path.join(DATA_DIR, file)
        arr = np.load(path)
        df = pd.DataFrame(arr, columns=['kick', 'snare', 'closed_hat', 'crash', 'low_tom'])
        all_data.append(df)
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

def filter_silent_steps(df):
    active = df[(df > 0).any(axis=1)]
    print(f"🧹 Filtered: {len(df)} ➡️ {len(active)} active steps.")
    return active

def train_and_save(genre, df):
    model = BayesianNetwork([
        ('kick', 'snare'),
        ('snare', 'closed_hat'),
        ('closed_hat', 'crash'),
        ('crash', 'low_tom')
    ])
    model.fit(df, estimator=MaximumLikelihoodEstimator)
    output_path = os.path.join(OUTPUT_DIR, f'{genre}_model.pkl')
    joblib.dump(model, output_path)
    print(f"✅ Model trained and saved: {output_path}")

genres = set(f.split('_')[0] for f in os.listdir(DATA_DIR) if f.endswith('.npy'))
for genre in genres:
    print(f"\n🎯 Training model for: {genre}")
    df = load_genre_data(genre)
    if df.empty:
        print(f"⚠️ No data found for {genre} — skipping.")
        continue
    df = filter_silent_steps(df)
    if len(df) < 5:
        print(f"⚠️ Not enough data after filtering for {genre}. Skipping.")
        continue
    train_and_save(genre, df)

print("\n🎉 Training complete!")
