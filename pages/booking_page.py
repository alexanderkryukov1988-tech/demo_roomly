from locators import Locators
from pages._base import Page

ROOM_NAMES = {"small": "Малая", "medium": "Средняя", "large": "Большая"}

FIELD_LOCATORS = {
    "room": "room_select",
    "date": "date_input",
    "startTime": "start_time_input",
    "endTime": "end_time_input",
    "participants": "participants_input",
    "name": "name_input",
    "email": "email_input",
}


class BookingPage(Page):
    """Страница бронирования переговорной комнаты."""

    def __init__(self, page, loc=None):
        super().__init__(page)
        loc = loc or Locators()
        self.booking_loc = loc("booking")
        self.console_errors = []
        self.page.on(
            "console",
            lambda message: self.console_errors.append(message.text)
            if message.type == "error"
            else None,
        )

    def open_page(self, url):
        """Открыть форму бронирования."""
        self.navigate(url)
        self.wait_for_element_visible(self.booking_loc["form"])

    def fill_booking_form(self, booking):
        """Заполнить форму данными заявки."""
        self.select_option(self.booking_loc["room_select"], booking["room"])
        self.type_text(self.booking_loc["date_input"], booking["date"])
        self.type_text(self.booking_loc["start_time_input"], booking["start_time"])
        self.type_text(self.booking_loc["end_time_input"], booking["end_time"])
        self.type_text(self.booking_loc["participants_input"], booking["participants"])
        self.type_text(self.booking_loc["name_input"], booking["name"])
        self.type_text(self.booking_loc["email_input"], booking["email"])

    def select_room(self, room):
        """Выбрать переговорную по значению опции."""
        self.select_option(self.booking_loc["room_select"], room)

    def clear_field(self, field):
        """Очистить поле формы по имени поля."""
        self.page.fill(self._field_selector(field), "")

    def fill_field(self, field, value):
        """Заполнить одно поле формы по имени поля."""
        self.type_text(self._field_selector(field), value)

    def submit(self):
        """Нажать «Забронировать» и дождаться сообщения под формой."""
        self.click_element(self.booking_loc["submit_button"])
        self.wait_for_text(self.booking_loc["form_status"])

    def warning(self, field):
        """Текст предупреждения у поля формы."""
        selector = self.booking_loc["field_error"].format(name=field)
        return self.get_element_text(selector) if self.page.locator(selector).count() else ""

    def has_warning(self, field):
        """Есть ли предупреждение у поля формы."""
        return bool(self.warning(field))

    def warned_fields(self):
        """Список полей, у которых есть предупреждение."""
        return [field for field in FIELD_LOCATORS if self.has_warning(field)]

    def form_message(self):
        """Текст сообщения под формой."""
        return self.get_element_text(self.booking_loc["form_status"])

    def is_success(self):
        """Показано ли сообщение об успешной брони."""
        return "success" in self.get_element_attribute(self.booking_loc["form_status"], "class")

    def field_value(self, field):
        """Текущее значение поля формы."""
        return self.page.locator(self._field_selector(field)).input_value()

    def placeholder(self, field):
        """Подсказка поля формы."""
        return self.page.locator(self._field_selector(field)).get_attribute("placeholder") or ""

    def date_min_attribute(self):
        """Минимально допустимая дата в поле «Дата»."""
        return self.get_element_attribute(self.booking_loc["date_input"], "min")

    def reload_page(self):
        """Перезагрузить страницу с формой."""
        self.page.reload(wait_until="domcontentloaded")
        self.wait_for_element_visible(self.booking_loc["form"])

    def set_viewport(self, width, height=800):
        """Установить размер окна браузера."""
        self.page.set_viewport_size({"width": width, "height": height})

    def has_horizontal_scroll(self):
        """Есть ли горизонтальная прокрутка страницы."""
        return self.page.evaluate(
            "() => document.documentElement.scrollWidth > document.documentElement.clientWidth"
        )

    def tab_focus_sequence(self, presses):
        """Последовательность id элементов, получающих фокус по Tab."""
        focused = []
        for _ in range(presses):
            self.page.keyboard.press("Tab")
            focused.append(self.page.evaluate("() => document.activeElement?.id || ''"))
        return focused

    def focus_field(self, field):
        """Поставить фокус в поле формы."""
        self.page.locator(self._field_selector(field)).focus()

    def press_enter(self):
        """Нажать Enter в текущем поле ввода."""
        self.page.keyboard.press("Enter")

    def clear_warning_by_typing(self, field, value):
        """Ввести значение в поле, чтобы снять предупреждение."""
        self.type_text(self._field_selector(field), value)

    def page_has_script_error(self):
        """Зафиксированы ли ошибки JavaScript в консоли."""
        return bool(self.console_errors)

    def js_state(self, expression):
        """Прочитать значение выражения в контексте страницы."""
        return self.page.evaluate(expression)

    def _field_selector(self, field):
        return self.booking_loc[FIELD_LOCATORS[field]]

    def should_show_success(self, booking):
        """Проверить, что бронь создана и сообщение содержит данные заявки."""
        status_selector = self.booking_loc["form_status"]
        self.wait_for_element_visible(f"{status_selector}.success")
        message = self.get_element_text(status_selector)

        expected_parts = (
            ROOM_NAMES[booking["room"]],
            booking["date"],
            booking["start_time"],
            booking["end_time"],
            booking["name"],
        )
        for part in expected_parts:
            assert part in message, f"В сообщении об успехе нет {part!r}: {message}"

    def should_show_field_error(self, field, expected_text):
        """Проверить текст предупреждения конкретного поля."""
        error_selector = self.booking_loc["field_error"].format(name=field)
        self.wait_for_element_visible(error_selector)
        actual_text = self.get_element_text(error_selector)
        assert actual_text == expected_text, f"Ожидали {expected_text!r}, получили {actual_text!r}"

    def should_not_show_success(self):
        """Проверить, что бронирование не создано."""
        status_selector = self.booking_loc["form_status"]
        status_class = self.get_element_attribute(status_selector, "class")
        status_text = self.get_element_text(status_selector)
        assert "success" not in status_class, f"Ожидали отказ в бронировании, но показано: {status_text}"
