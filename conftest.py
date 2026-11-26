import os

import pytest

from pages.booking_page import BookingPage


@pytest.fixture(scope="session")
def base_url(pytestconfig):
    """CLI --base-url takes precedence over BASE_URL and the demo address."""
    return (
        pytestconfig.getoption("--base-url")
        or os.environ.get("BASE_URL")
        or "https://rcsi-science.github.io/demo-roomly/"
    )


@pytest.fixture
def booking_page(page):
    """Page object формы бронирования переговорной комнаты."""
    return BookingPage(page)
