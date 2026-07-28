def get_focus_age(focus_score, real_age):
    if focus_score >= 80:
        return real_age + 5
    elif focus_score >= 60:
        return real_age 
    else :
        return real_age - 5
    