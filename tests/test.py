from webdriver import Webdriver
from selenium_manager import SeleniumManager
import time


if __name__ == '__main__':
    driver = Webdriver.build()
    manager = SeleniumManager(driver, 'http:localhost:8080/')
    manager.go_to_main_page()
    time.sleep(2)
    manager.add_products_to_cart(3)
    manager.go_to_main_page()
    time.sleep(2)
    manager.add_random_product_from_search("buty")
    time.sleep(2)
    manager.remove_products_from_cart(3)
    time.sleep(2)
    manager.register_account()
    time.sleep(2)
    manager.finalize_order()
    time.sleep(2)
    manager.check_order()
    time.sleep(2)
    manager.check_file()
    time.sleep(5)