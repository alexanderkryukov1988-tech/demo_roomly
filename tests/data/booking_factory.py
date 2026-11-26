import datetime


def tomorrow():
    """Возвращает завтрашнюю дату в формате поля type=date."""
    return (datetime.date.today() + datetime.timedelta(days=1)).isoformat()


def booking_data(**overrides):
    """Данные заявки по умолчанию: корректная бронь на завтра, 10:00–11:30."""
    data = {
        "room": "medium",
        "date": tomorrow(),
        "start_time": "10:00",
        "end_time": "11:30",
        "participants": 6,
        "name": "Анна Тестова",
        "email": "anna.testova@example.ru",
    }
    data.update(overrides)
    return data
