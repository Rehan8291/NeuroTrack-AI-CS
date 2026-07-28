def generate_feedback(study, scroll, sleep):

    if study < scroll:
        return ("You should spend more time studying and less time scrolling. "
                "Reduce your scrolling time by 30 min, this will help you a lot.")

    elif sleep < 6:
        return ("Do you know that sleep is crucial for brain health? "
                "Try to get at least 7-8 hours of sleep and then see the magic happen.")

    elif study >= 4:
        return ("OMG! You are doing great, buddy, keep it up! "
                "Study is the key to success and you are on track.")

    else:
        return "You are making some progress but you can do better!"
