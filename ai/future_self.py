def predict_future(focus_score):

    if focus_score >= 85:
        return (
            "High Productivity",
            "85%"
        )

    elif focus_score >= 70:
        return (
            "Good Productivity",
            "70%"
        )

    elif focus_score >= 50:
        return (
            "Moderate Productivity",
            "55%"
        )

    else:
        return (
            "Low Productivity",
            "25%"
        )