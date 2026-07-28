def get_animal(study, scroll, sleep):

    if study >= 5 and scroll <= 2 and sleep >= 7:
        return "🦅 Eagle"

    elif study >= 3 and scroll <= 4:
        return "🐺 Wolf"

    elif study >= 2 and sleep >= 7:
        return "🐬 Dolphin"

    elif scroll >= 5:
        return "🐼 Panda"

    else:
        return "🐢 Turtle"