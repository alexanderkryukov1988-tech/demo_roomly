import datetime
import re

from tests.data.booking_factory import booking_data


def fill_and_submit(booking_page, base_url, booking):
    """Открыть форму, заполнить её данными заявки и отправить."""
    booking_page.open_page(base_url)
    booking_page.fill_booking_form(booking)
    booking_page.submit()


def assert_rejected(booking_page):
    """Проверить, что бронь не создана."""
    assert not booking_page.is_success(), f"Ожидали отказ, но бронь создана: {booking_page.form_message()}"


BOOKING_KEYS = {
    "room": "room",
    "date": "date",
    "startTime": "start_time",
    "endTime": "end_time",
    "participants": "participants",
    "name": "name",
    "email": "email",
}


def booking_without(field):
    """Данные заявки с пустым значением указанного поля."""
    booking = booking_data()
    booking[BOOKING_KEYS[field]] = ""
    return booking


def test_cl_01_positive_booking(booking_page, base_url):
    """CL-01: корректно заполненная форма создаёт бронь."""
    fill_and_submit(booking_page, base_url, booking_data())
    assert booking_page.is_success(), f"Ожидали успех, но показано: {booking_page.form_message()}"


def test_cl_02_success_message_content(booking_page, base_url):
    """CL-02: сообщение содержит комнату, дату, время и имя заявителя."""
    booking = booking_data()
    fill_and_submit(booking_page, base_url, booking)

    message = booking_page.form_message()
    for part in ("Средняя", booking["date"], "10:00", "11:30", booking["name"]):
        assert part in message, f"В сообщении нет {part!r}: {message}"


def test_cl_03_room_required(booking_page, base_url):
    """CL-03: пустая переговорная даёт предупреждение."""
    fill_and_submit(booking_page, base_url, booking_without("room"))
    assert booking_page.has_warning("room")
    assert_rejected(booking_page)


def test_cl_04_date_required(booking_page, base_url):
    """CL-04: пустая дата даёт предупреждение."""
    fill_and_submit(booking_page, base_url, booking_without("date"))
    assert booking_page.has_warning("date")
    assert_rejected(booking_page)


def test_cl_05_start_time_required(booking_page, base_url):
    """CL-05: пустое время начала даёт предупреждение."""
    fill_and_submit(booking_page, base_url, booking_without("startTime"))
    assert booking_page.has_warning("startTime")
    assert_rejected(booking_page)


def test_cl_06_end_time_required(booking_page, base_url):
    """CL-06: пустое время окончания даёт предупреждение."""
    fill_and_submit(booking_page, base_url, booking_without("endTime"))
    assert booking_page.has_warning("endTime")
    assert_rejected(booking_page)


def test_cl_07_participants_required(booking_page, base_url):
    """CL-07: пустое количество участников даёт предупреждение."""
    fill_and_submit(booking_page, base_url, booking_without("participants"))
    assert booking_page.has_warning("participants")
    assert_rejected(booking_page)


def test_cl_08_name_required(booking_page, base_url):
    """CL-08: пустое имя даёт предупреждение."""
    fill_and_submit(booking_page, base_url, booking_without("name"))
    assert booking_page.has_warning("name")
    assert_rejected(booking_page)


def test_cl_09_email_required(booking_page, base_url):
    """CL-09: пустая почта даёт предупреждение."""
    fill_and_submit(booking_page, base_url, booking_without("email"))
    assert booking_page.has_warning("email")
    assert_rejected(booking_page)


def test_cl_10_empty_form_marks_all_fields(booking_page, base_url):
    """CL-10: отправка пустой формы отмечает все обязательные поля."""
    booking_page.open_page(base_url)
    booking_page.submit()

    warned = booking_page.warned_fields()
    assert set(warned) == {"room", "date", "startTime", "endTime", "participants", "name", "email"}, warned


def test_cl_11_past_date_rejected(booking_page, base_url):
    """CL-11: дата в прошлом отклоняется."""
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    fill_and_submit(booking_page, base_url, booking_data(date=yesterday))
    assert_rejected(booking_page)


def test_cl_12_past_dates_not_selectable(booking_page, base_url):
    """CL-12: минимальная дата в календаре — сегодняшняя."""
    booking_page.open_page(base_url)
    assert booking_page.date_min_attribute() == datetime.date.today().isoformat()


def test_cl_13_past_time_today_rejected(booking_page, base_url):
    """CL-13: для сегодняшней даты прошедшее время отклоняется."""
    now = datetime.datetime.now()
    if now.hour < 3:
        import pytest

        pytest.skip("Нет прошедшего времени в текущих сутках")

    booking = booking_data(
        date=now.date().isoformat(),
        start_time=(now - datetime.timedelta(hours=2)).strftime("%H:%M"),
        end_time=(now + datetime.timedelta(minutes=30)).strftime("%H:%M"),
    )
    fill_and_submit(booking_page, base_url, booking)
    assert_rejected(booking_page)


def test_cl_14_end_before_start_rejected(booking_page, base_url):
    """CL-14: время окончания раньше начала отклоняется."""
    fill_and_submit(booking_page, base_url, booking_data(start_time="11:00", end_time="10:00"))
    assert_rejected(booking_page)


def test_cl_15_equal_start_and_end_rejected(booking_page, base_url):
    """CL-15: равные начало и окончание отклоняются."""
    fill_and_submit(booking_page, base_url, booking_data(start_time="10:00", end_time="10:00"))
    assert_rejected(booking_page)


def test_cl_16_duration_less_than_30_minutes_rejected(booking_page, base_url):
    """CL-16: длительность меньше 30 минут отклоняется."""
    fill_and_submit(booking_page, base_url, booking_data(start_time="10:00", end_time="10:15"))
    assert_rejected(booking_page)


def test_cl_17_duration_more_than_4_hours_rejected(booking_page, base_url):
    """CL-17: длительность больше 4 часов отклоняется."""
    fill_and_submit(
        booking_page,
        base_url,
        booking_data(room="large", start_time="10:00", end_time="15:00", participants=5),
    )
    assert_rejected(booking_page)


def test_cl_18_duration_exactly_30_minutes_accepted(booking_page, base_url):
    """CL-18: длительность ровно 30 минут принимается."""
    fill_and_submit(booking_page, base_url, booking_data(start_time="10:00", end_time="10:30"))
    assert booking_page.is_success(), booking_page.form_message()


def test_cl_19_duration_exactly_4_hours_accepted(booking_page, base_url):
    """CL-19: длительность ровно 4 часа принимается."""
    fill_and_submit(
        booking_page,
        base_url,
        booking_data(room="large", start_time="10:00", end_time="14:00", participants=5),
    )
    assert booking_page.is_success(), booking_page.form_message()


def test_cl_20_participants_over_capacity_rejected(booking_page, base_url):
    """CL-20: участников больше вместимости комнаты отклоняется."""
    fill_and_submit(booking_page, base_url, booking_data(room="small", participants=5))
    assert "максимум 4" in booking_page.warning("participants"), booking_page.warning("participants")
    assert_rejected(booking_page)


def test_cl_21_participants_less_than_one_rejected(booking_page, base_url):
    """CL-21: количество участников меньше 1 отклоняется."""
    fill_and_submit(booking_page, base_url, booking_data(participants=0))
    assert booking_page.has_warning("participants")
    assert_rejected(booking_page)


def test_cl_22_participants_more_than_20_rejected(booking_page, base_url):
    """CL-22: количество участников больше 20 отклоняется."""
    fill_and_submit(booking_page, base_url, booking_data(room="large", participants=21))
    assert_rejected(booking_page)


def test_cl_23_participants_equal_capacity_accepted(booking_page, base_url):
    """CL-23: 20 участников для «Большой» комнаты принимаются."""
    fill_and_submit(booking_page, base_url, booking_data(room="large", participants=20))
    assert booking_page.is_success(), booking_page.form_message()


def test_cl_24_email_without_at_rejected(booking_page, base_url):
    """CL-24: почта без символа «@» отклоняется."""
    fill_and_submit(booking_page, base_url, booking_data(email="anna.testova.example.ru"))
    assert booking_page.has_warning("email")
    assert_rejected(booking_page)


def test_cl_25_email_without_top_level_domain_rejected(booking_page, base_url):
    """CL-25: почта с доменом без точки в верхнем уровне отклоняется."""
    fill_and_submit(booking_page, base_url, booking_data(email="anna@company"))
    assert booking_page.has_warning("email")
    assert_rejected(booking_page)


def test_cl_26_name_of_spaces_rejected(booking_page, base_url):
    """CL-26: имя из одних пробелов отклоняется."""
    fill_and_submit(booking_page, base_url, booking_data(name="   "))
    assert booking_page.has_warning("name")
    assert_rejected(booking_page)


def test_cl_27_warning_clears_on_input(booking_page, base_url):
    """CL-27: предупреждение поля исчезает при исправлении."""
    booking_page.open_page(base_url)
    booking_page.clear_field("name")
    booking_page.fill_booking_form(booking_data())
    booking_page.clear_field("name")
    booking_page.submit()

    assert booking_page.has_warning("name")
    booking_page.clear_warning_by_typing("name", "Анна Тестова")
    assert not booking_page.has_warning("name")


def test_cl_28_data_not_saved_after_reload(booking_page, base_url):
    """CL-28: после перезагрузки данные формы не сохраняются."""
    fill_and_submit(booking_page, base_url, booking_data())
    booking_page.reload_page()

    assert booking_page.field_value("name") == ""
    assert booking_page.field_value("room") == ""
    assert booking_page.form_message() == ""


def test_cl_29_angle_brackets_in_name_rejected(booking_page, base_url):
    """CL-29: символы < и > в имени отклоняются с предупреждением."""
    fill_and_submit(booking_page, base_url, booking_data(name="Анна <b>Тестова</b>"))

    assert booking_page.has_warning("name"), "Ожидали предупреждение о недопустимых символах в имени"
    assert_rejected(booking_page)


def test_cl_30_enter_submits_form(booking_page, base_url):
    """CL-30: форма отправляется клавишей Enter."""
    booking_page.open_page(base_url)
    booking_page.fill_booking_form(booking_data())
    booking_page.focus_field("name")
    booking_page.press_enter()
    booking_page.wait_for_text(booking_page.booking_loc["form_status"])

    assert booking_page.is_success(), booking_page.form_message()


def test_cl_31_no_js_errors_in_console(booking_page, base_url):
    """CL-31: консоль браузера остаётся без ошибок JavaScript."""
    fill_and_submit(booking_page, base_url, booking_data())
    assert not booking_page.page_has_script_error(), booking_page.console_errors


def test_cl_32_fields_reachable_by_tab(booking_page, base_url):
    """CL-32: все поля доступны с клавиатуры через табуляцию."""
    booking_page.open_page(base_url)
    booking_page.focus_field("room")

    expected = ["date", "start-time", "end-time", "participants", "name", "email"]
    focused = booking_page.tab_focus_sequence(20)
    reached = list(dict.fromkeys(field for field in focused if field in expected))
    assert reached == expected, focused


def test_cl_33_no_horizontal_scroll_on_mobile(booking_page, base_url):
    """CL-33: на ширине 375 px нет горизонтальной прокрутки."""
    booking_page.set_viewport(375)
    booking_page.open_page(base_url)
    assert not booking_page.has_horizontal_scroll()
