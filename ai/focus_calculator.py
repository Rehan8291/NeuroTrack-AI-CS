def calculate_focus_score(study, sleep, exercise, scroll):
    """
    Focus Score formula:

        50 (base)
        + study * 10
        + sleep * 3
        + exercise * 5
        - scroll * 8

    Clamped between 0 and 100.
    """

    score = 50

    score += study * 10
    score += sleep * 3
    score += exercise * 5
    score -= scroll * 8

    if score > 100:
        score = 100

    if score < 0:
        score = 0

    return round(score)
