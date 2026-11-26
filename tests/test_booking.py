import pytest

from tests.data.booking_factory import booking_data


@pytest.mark.positive
def test_successful_booking(booking_page, base_url):
    """Корректные данные показывают сообщение с комнатой, датой, временем и именем."""
    booking = booking_data()

    booking_page.open_page(base_url)
    booking_page.fill_booking_form(booking)
    booking_page.submit()

    booking_page.should_show_success(booking)


@pytest.mark.negative
def test_capacity_exceeded_is_rejected(booking_page, base_url):
    """Для «Малой» комнаты 10 участников превышают лимит в 4 человека."""
    booking = booking_data(room="small", participants=10)

    booking_page.open_page(base_url)
    booking_page.fill_booking_form(booking)
    booking_page.submit()

    booking_page.should_show_field_error("participants", "В комнате максимум 4 участника.")
    booking_page.should_not_show_success()


@pytest.mark.negative
@pytest.mark.xfail(
    strict=True,
    reason="BUG-01: бронь длительностью больше 4 часов создаётся без ошибки",
    raises=AssertionError,
)
def test_booking_longer_than_four_hours_is_rejected(booking_page, base_url):
    """Время окончания позже начала на 5 часов — длительность вне диапазона 30 минут – 4 часа."""
    booking = booking_data(room="large", start_time="10:00", end_time="15:00", participants=5)

    booking_page.open_page(base_url)
    booking_page.fill_booking_form(booking)
    booking_page.submit()

    booking_page.should_not_show_success()
