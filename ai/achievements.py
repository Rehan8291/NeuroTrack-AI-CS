from database.db import (
    get_all_logs,
    get_total_study,
    get_total_logs,
    get_average_focus,
    get_average_sleep,
    get_current_streak,
    add_achievement,
    get_earned_badges,
)


# Master list of all possible badges: (badge_name, icon, description)
BADGE_DEFINITIONS = [
    ("7 Day Streak", "🥇", "Log your data 7 days in a row"),
    ("100 Study Hours", "📚", "Reach 100 total hours of study"),
    ("Sleep Champion", "😴", "Average 7+ hours of sleep"),
    ("Fitness Badge", "🏃", "Average 45+ minutes of exercise a day"),
    ("Focus Master", "🎯", "Reach an average focus score of 85+"),
    ("Consistency Badge", "🔥", "Log your data at least 10 times"),
]


def check_and_award_achievements(username):
    """
    Looks at the user's current stats, awards any newly-earned badges
    to the database, and returns the full badge list with earned status.
    """

    logs = get_all_logs(username)

    if logs:
        total_study = get_total_study(username)
        total_logs = get_total_logs(username)
        avg_focus = get_average_focus(username)
        avg_sleep = get_average_sleep(username)
        streak = get_current_streak(username)

        avg_exercise_hours = sum(row[2] for row in logs) / len(logs)

        if streak >= 7:
            add_achievement(username, "7 Day Streak")

        if total_study >= 100:
            add_achievement(username, "100 Study Hours")

        if avg_sleep >= 7:
            add_achievement(username, "Sleep Champion")

        if avg_exercise_hours >= 0.75:
            add_achievement(username, "Fitness Badge")

        if avg_focus >= 85:
            add_achievement(username, "Focus Master")

        if total_logs >= 10:
            add_achievement(username, "Consistency Badge")

    earned = set(get_earned_badges(username))

    result = []

    for name, icon, description in BADGE_DEFINITIONS:
        result.append({
            "name": name,
            "icon": icon,
            "description": description,
            "earned": name in earned,
        })

    return result
