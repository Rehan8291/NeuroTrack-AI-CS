import random

def get_challenge():

    challenges = [
        "Study 30 minutes extra",
        "Reduce scrolling by 20 minutes",
        "Sleep before 11 PM",
        "Walk for 20 minutes",
        "Read 10 pages of a book"
    ]

    return random.choice(challenges)