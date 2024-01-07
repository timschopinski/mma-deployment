from ast import List
from typing import Any
from selenium import webdriver
import settings
from selenium.common import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC, expected_conditions
from selenium.webdriver.common.keys import Keys
import time
import time
import random


class SeleniumManager:

    def __init__(self, wd: webdriver, base_url: str):
        self.wd = wd
        self.base_url = base_url
        self.timeout = 10

    def go_to_main_page(self):
        self.wd.get(self.base_url)

    def go_to_admin_page(self):
        self.wd.get("http://localhost:8080/admin602y5pfqv")

    def go_to(self, path: str):
        self.wd.get(self.base_url + path)

    def click_login_button(self):
        login_button = WebDriverWait(
            self.wd, self.timeout
        ).until(expected_conditions.presence_of_element_located((By.XPATH,  "//span[contains(text(),'Zaloguj się')]")))
        login_button.click()

    def click_process_order(self):
        order_button = WebDriverWait(
            self.wd, self.timeout
        ).until(expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="main"]/div/div[2]/div[1]/div[2]/div/a')))
        order_button.click()

    def click_register_button(self):
        register_button = WebDriverWait(
            self.wd, self.timeout
        ).until(expected_conditions.presence_of_element_located((By.XPATH,  "//a[contains(text(),'Nie masz konta? Załóż je tutaj')]")))
        register_button.click()

    def click_cart_button(self):
        view_cart_button = WebDriverWait(
            self.wd, self.timeout
        ).until(expected_conditions.presence_of_element_located((By.XPATH,  "//span[normalize-space()='Koszyk']")))
        view_cart_button.click()

    def set_product_quantity(self, quantity: int = 1):
        quantity_box = WebDriverWait(
            self.wd, self.timeout
        ).until(expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="quantity_wanted"]')))

        quantity_box = self.wd.find_element(By.XPATH, '//*[@id="quantity_wanted"]')
        quantity_box.send_keys(Keys.DELETE)
        quantity_box.send_keys(quantity)

    def click_continue_shopping(self):
        time.sleep(1)
        continue_shopping_button = WebDriverWait(
            self.wd, self.timeout
            ).until(expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="blockcart-modal"]/div/div/div[2]/div/div[2]/div/div/button')))
        continue_shopping_button.click()

    def go_back(self, pages_num: int = 1):
        self.wd.execute_script(f"window.history.go(-{pages_num})")

    def remove_products_from_cart(self, amount: int):
        self.click_cart_button()
        for i in range(1, amount + 1):
            try:
                remove_product_button = WebDriverWait(
                    self.wd, self.timeout
                ).until(expected_conditions.presence_of_element_located((By.XPATH, f"//li[{i}]//div[1]//div[3]//div[1]//div[3]//div[1]//a[1]//i[1]")))
                remove_product_button.click()
            except Exception as e:
                print(e)
            time.sleep(0.5)

    def add_item_to_cart(self, item: Any, quantity=1):
        time.sleep(0.5)
        item.click()
        self.set_product_quantity(quantity)
        add_to_cart_button = WebDriverWait(
            self.wd, self.timeout
            ).until(expected_conditions.presence_of_element_located((By.XPATH, "//button[@class='btn btn-primary add-to-cart']")))
        add_to_cart_button.click()
        self.click_continue_shopping()
        time.sleep(0.5)

    def add_random_product_from_search(self, search_phrase: str):
        search_box = WebDriverWait(
            self.wd, self.timeout
        ).until(expected_conditions.presence_of_element_located((By.XPATH, "//input[@placeholder='Szukaj w naszym katalogu']")))
        search_box.send_keys(search_phrase)
        search_box.send_keys(Keys.ENTER)
        time.sleep(1)
        items = self.wd.find_elements(By.XPATH, "//div[*]//article[1]//div[1]//div[1]//a[1]//img[1]")
        print(items)
        self.add_item_to_cart(random.choice(items))


    def add_products_to_cart(self, amount: int = 10):
        num_of_items = 0
        for category_path in settings.CATEGORY_PATHS:
            self.go_to(category_path)
            items_count = len(self.wd.find_elements(By.XPATH, '//*[@id="js-product-list"]/div[1]/div[*]/article/div/div[1]/a/img'))
            limit = items_count if items_count <= amount - 1 else amount - num_of_items
            limit = 2
            for i in range(limit):
                item = self.wd.find_elements(By.XPATH, '//*[@id="js-product-list"]/div[1]/div[*]/article/div/div[1]/a/img')[i]
                self.add_item_to_cart(item, quantity=random.randint(1, 3))
                self.go_to(category_path)
            num_of_items += items_count
            if num_of_items >= 2:
                break
        print("finish")

    def complete_register_form(self):
        first_name = "Marta"
        second_name = "Mokra"
        email = f"mokramarta{random.randint(1,10000)}@gmail.com"
        password = "martunia123"
        birthday_date = "1928-11-19"

        gender_button = self.wd.find_element(By.XPATH, f"//input[@id='field-id_gender-{random.randint(1, 2)}']")
        gender_button.click()

        self.wd.find_element(By.XPATH, "//input[@id='field-firstname']").send_keys(first_name)
        self.wd.find_element(By.XPATH, "//input[@id='field-lastname']").send_keys(second_name)
        self.wd.find_element(By.XPATH, "//input[@id='field-email']").send_keys(email)
        self.wd.find_element(By.XPATH, "//input[@id='field-password']").send_keys(password)
        self.wd.find_element(By.XPATH, "//input[@id='field-birthday']").send_keys(birthday_date)

        self.wd.find_element(By.XPATH, "//input[@name='customer_privacy']").click()
        self.wd.find_element(By.XPATH, "//input[@name='psgdpr']").click()
        self.wd.find_element(By.XPATH, "//button[@type='submit']").click()

    def register_account(self):
        self.click_login_button()
        time.sleep(1)
        self.click_register_button()
        time.sleep(1)
        self.complete_register_form()
        time.sleep(1)

    def finalize_order(self):
        self.go_to("koszyk?action=show")
        time.sleep(1)
        order_button = WebDriverWait(
            self.wd, self.timeout
        ).until(expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="main"]/div/div[2]/div[1]/div[2]/div/a')))
        order_button.click()
        adres_box = self.wd.find_element(By.XPATH, '//*[@id="field-address1"]')
        adres_box.send_keys("Giewont")
        code_box = self.wd.find_element(By.XPATH, '//*[@id="field-postcode"]')
        code_box.send_keys("80-123")
        city_box = self.wd.find_element(By.XPATH, '//*[@id="field-city"]')
        city_box.send_keys("Gnojewo")
        time.sleep(1)

        order_button = WebDriverWait(
            self.wd, self.timeout
        ).until(
            expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="delivery-address"]/div/footer/button')))
        order_button.click()
        time.sleep(1)

        order_button = WebDriverWait(
            self.wd, self.timeout
        ).until(
            expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="js-delivery"]/button')))
        order_button.click()
        time.sleep(1)

        order_button = WebDriverWait(
            self.wd, self.timeout
        ).until(
            expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="payment-option-2"]')))
        order_button.click()

        order_button = WebDriverWait(
            self.wd, self.timeout
        ).until(
            expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="conditions_to_approve[terms-and-conditions]"]')))
        order_button.click()

        order_button = WebDriverWait(
            self.wd, self.timeout
        ).until(
            expected_conditions.presence_of_element_located((By.XPATH,
                                                            '//*[@id="payment-confirmation"]/div[1]/button')))
        order_button.click()
        time.sleep(1)
        self.go_to_main_page()


    def check_order(self):
        self.go_to("historia-zamowien")

    def check_file(self):
        self.go_to_admin_page()
        email_box = self.wd.find_element(By.XPATH, '//*[@id="email"]')
        email_box.send_keys("s188810@student.pg.edu.pl")
        password_box = self.wd.find_element(By.XPATH, '//*[@id="passwd"]')
        password_box.send_keys("BkVpreNKaP")
        order_button = WebDriverWait(
            self.wd, self.timeout
        ).until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//*[@id="submit_login"]')))
        order_button.click()

        order_button = WebDriverWait(
            self.wd, self.timeout
        ).until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//*[@id="subtab-AdminParentOrders"]/a')))
        order_button.click()

        order_button = WebDriverWait(
            self.wd, self.timeout
        ).until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//*[@id="subtab-AdminOrders"]/a')))
        order_button.click()

        order_button = WebDriverWait(
            self.wd, self.timeout
        ).until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//*[@id="order_grid_table"]/tbody/tr[1]/td[9]/div/button'))) #Tutaj jest zla sciezzka
        order_button.click()

        order_button = WebDriverWait(
            self.wd, self.timeout
        ).until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//*[@id="order_grid_table"]/tbody/tr[1]/td[9]/div/div/button[5]')))
        order_button.click()

        self.go_to_main_page()
        order_button = WebDriverWait(
            self.wd, self.timeout
        ).until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//*[@id="_desktop_user_info"]/div/a[2]')))
        order_button.click()

        order_button = WebDriverWait(
            self.wd, self.timeout
        ).until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//*[@id="history-link"]')))
        order_button.click()

        order_button = WebDriverWait(
            self.wd, self.timeout
        ).until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//*[@id="content"]/table/tbody/tr/td[5]/a'))) #Tutaj jest zla sciezzka
        order_button.click()