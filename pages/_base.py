class Page:
    """Базовые действия над страницей: навигация, ввод, клики и ожидания."""

    default_timeout = 10_000

    def __init__(self, page):
        self.page = page

    def navigate(self, url):
        """Открыть страницу и дождаться загрузки DOM."""
        self.page.goto(url, wait_until="domcontentloaded")

    def type_text(self, selector, text):
        self.page.fill(selector, str(text))

    def select_option(self, selector, value):
        self.page.select_option(selector, value)

    def click_element(self, selector):
        self.page.click(selector)

    def get_element_text(self, selector):
        return self.page.locator(selector).inner_text().strip()

    def get_element_attribute(self, selector, attribute):
        return self.page.locator(selector).get_attribute(attribute) or ""

    def wait_for_element_visible(self, selector):
        self.page.wait_for_selector(selector, state="visible", timeout=self.default_timeout)

    def wait_for_text(self, selector):
        self.page.wait_for_function(
            "(selector) => Boolean(document.querySelector(selector)?.textContent.trim())",
            arg=selector,
            timeout=self.default_timeout,
        )
