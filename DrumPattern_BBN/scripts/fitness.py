# fitness.py

def compute_note_density(pattern):
    """Calculates the number of drum hits in the pattern."""
    return len(pattern)

def compute_instrument_distribution(pattern):
    """Returns the frequency distribution of instruments in the pattern."""
    distribution = {}
    for instrument in pattern:
        distribution[instrument] = distribution.get(instrument, 0) + 1
    total = len(pattern)
    for instrument in distribution:
        distribution[instrument] /= total
    return distribution

def compute_position_accuracy(pattern, expected_positions):
    """
    Compares expected instrument positions to generated ones.
    expected_positions = {'Kick': [0, 2], 'Snare': [1, 3]} (ideal positions)
    """
    score = 0
    for i, instrument in enumerate(pattern):
        if instrument in expected_positions and i in expected_positions[instrument]:
            score += 1
    return score / len(pattern) if pattern else 0

def fitness_function(pattern, training_stats, expected_positions):
    """
    Combines multiple evaluation metrics into one fitness score.
    """
    generated_density = compute_note_density(pattern)
    training_density = training_stats['density']

    density_score = 1 - abs(generated_density - training_density) / max(training_density, 1)

    generated_distribution = compute_instrument_distribution(pattern)
    expected_distribution = training_stats['instrument_distribution']

    distribution_score = 1 - sum(
        abs(generated_distribution.get(instr, 0) - expected_distribution.get(instr, 0))
        for instr in expected_distribution
    )

    position_score = compute_position_accuracy(pattern, expected_positions)

    final_score = (density_score * 0.4) + (distribution_score * 0.3) + (position_score * 0.3)

    return final_score
