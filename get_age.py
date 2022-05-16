from datetime import date

def get_age(birthdate):
    birthdate = birthdate.split('/')
    birthdate.reverse()
    birthdate = list(map(int, birthdate))
    birthdate = date(birthdate[0], birthdate[1], birthdate[2])
    print(birthdate)
    today = date.today()
    age_year = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    age_month = today.month - birthdate.month
    if age_month < 0:
        age_month = 12 + age_month

    return age_year, age_month