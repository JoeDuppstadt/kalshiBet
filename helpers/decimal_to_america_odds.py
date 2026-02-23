def decimal_prob_to_american(prob):
    """
    Convert a decimal probability (0.0 < prob < 1.0) to American odds.
    Returns string like '+150' or '-200'
    """
    if not 0 < prob < 1:
        return "Invalid probability"

    if prob > 0.5:
        # Favorite: negative odds
        american = -round((prob / (1 - prob)) * 100)
    else:
        # Underdog: positive odds
        american = round(((1 - prob) / prob) * 100)
    return int(american)