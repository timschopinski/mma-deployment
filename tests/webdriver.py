from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class Webdriver:

    @classmethod
    def build(cls):
        options = Options()
        options.add_argument("--window-size=1920,1080")
        return webdriver.Chrome(options=options)
