import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Locators:
    """Загружает локаторы страниц из JSON-файлов каталога locators."""

    def __call__(self, page_name):
        return self.__get_locators(page_name)

    def __get_locators(self, page_name):
        path = os.path.join(BASE_DIR, "locators", f"{page_name}.json")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Локаторы страницы '{page_name}' не найдены: {path}")
        with open(path, "r", encoding="utf8") as file:
            return json.load(file)
