import data
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# no modificar
def retrieve_phone_code(driver) -> str:
    """Este código devuelve un número de confirmación de teléfono y lo devuelve como un string.
    Utilízalo cuando la aplicación espere el código de confirmación para pasarlo a tus pruebas.
    El código de confirmación del teléfono solo se puede obtener después de haberlo solicitado en la aplicación."""

    import json
    import time
    from selenium.common import WebDriverException
    code = None
    for i in range(10):
        try:
            logs = [log["message"] for log in driver.get_log('performance') if log.get("message")
                    and 'api/v1/number?number' in log.get("message")]
            for log in reversed(logs):
                message_data = json.loads(log)["message"]
                body = driver.execute_cdp_cmd('Network.getResponseBody',
                                              {'requestId': message_data["params"]["requestId"]})
                code = ''.join([x for x in body['body'] if x.isdigit()])
        except WebDriverException:
            time.sleep(1)
            continue
        if not code:
            raise Exception("No se encontró el código de confirmación del teléfono.\n"
                            "Utiliza 'retrieve_phone_code' solo después de haber solicitado el código en tu aplicación.")
        return code


class UrbanRoutesPage:
    from_field = (By.ID, 'from')
    to_field = (By.ID, 'to')

    smart_button = (By.XPATH, '//button[contains(text(), "Pedir un taxi")]')  # o según la UI
    comfort_tariff = (By.XPATH, '//div[contains(text(), "Comfort")]')
    phone_button = (By.CLASS_NAME, 'np-text')
    phone_input = (By.ID, 'phone')
    next_button_phone = (By.XPATH, '//button[contains(text(), "Siguiente")]')
    code_input = (By.ID, 'code')
    confirm_button_phone = (By.XPATH, '//button[contains(text(), "Confirmar")]')

    payment_method_button = (By.CLASS_NAME, 'pp-text')
    add_card_button = (By.CLASS_NAME, 'pp-plus')
    card_number_field = (By.ID, 'number')
    card_code_field = (By.XPATH, '//input[@id="code" and @class="card-input"]')
    link_card_button = (By.XPATH, '//button[contains(text(), "Enlazar")]')
    close_payment_modal = (By.XPATH, '//div[@class="payment-picker open"]//button[@class="close-button"]')

    driver_message_field = (By.ID, 'comment')
    blanket_switch = (By.XPATH, '//span[contains(text(), "Manta")]/following-sibling::span[@class="slider round"]')
    blanket_checkbox = (By.XPATH, '//input[@class="r-type-checkbox"]')

    ice_cream_plus_button = (By.XPATH, '//div[contains(text(), "Helado")]/..//div[@class="counter-plus"]')
    ice_cream_count = (By.XPATH, '//div[contains(text(), "Helado")]/..//div[@class="counter-value"]')

    order_taxi_button = (By.CLASS_NAME, 'smart-button-main')
    search_modal = (By.CLASS_NAME, 'order-body')
    driver_info_modal = (By.CLASS_NAME, 'order-header-title')

    def __init__(self, driver):
        self.driver = driver

    def set_from(self, from_address):
        # Espera hasta 10 segundos a que el campo "Desde" sea visible
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.from_field)
        ).send_keys(from_address)

    def set_to(self, to_address):
        # Espera hasta 10 segundos a que el campo "Hasta" sea visible
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.to_field)
        ).send_keys(to_address)

    def set_route(self, from_address, to_address):
        self.set_from(from_address)
        self.set_to(to_address)

    def get_from(self):
        return self.driver.find_element(*self.from_field).get_property('value')

    def get_to(self):
        return self.driver.find_element(*self.to_field).get_property('value')

    # --- Métodos de Interacción ---
    def select_comfort_tariff(self):
        # Hace clic en pedir taxi para desplegar tarifas y selecciona Comfort
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.smart_button)).click()
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.comfort_tariff)).click()

    def set_phone_number(self, phone):
        self.driver.find_element(*self.phone_button).click()
        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(self.phone_input)).send_keys(phone)
        self.driver.find_element(*self.next_button_phone).click()

    def enter_phone_code(self, code):
        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(self.code_input)).send_keys(code)
        self.driver.find_element(*self.confirm_button_phone).click()

    def add_credit_card(self, number, code):
        self.driver.find_element(*self.payment_method_button).click()
        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(self.add_card_button)).click()

        self.driver.find_element(*self.card_number_field).send_keys(number)
        card_code_elem = self.driver.find_element(*self.card_code_field)
        card_code_elem.send_keys(code)
        card_code_elem.send_keys(Keys.TAB)  # Cambia el enfoque para activar el botón

        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(self.link_card_button)).click()
        self.driver.find_element(*self.close_payment_modal).click()

    def set_driver_message(self, message):
        self.driver.find_element(*self.driver_message_field).send_keys(message)

    def order_blanket_and_tissues(self):
        self.driver.find_element(*self.blanket_switch).click()

    def add_ice_creams(self, count=2):
        plus_btn = self.driver.find_element(*self.ice_cream_plus_button)
        for _ in range(count):
            plus_btn.click()

    def click_order_taxi(self):
        self.driver.find_element(*self.order_taxi_button).click()

class TestUrbanRoutes:

    driver = None

    @classmethod
    def setup_class(cls):
        # no lo modifiques, ya que necesitamos un registro adicional habilitado para recuperar el código de confirmación del teléfono
        from selenium.webdriver import DesiredCapabilities
        capabilities = DesiredCapabilities.CHROME
        capabilities["goog:loggingPrefs"] = {'performance': 'ALL'}
        cls.driver = webdriver.Chrome(desired_capabilities=capabilities)

    def test_set_route(self):
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)
        address_from = data.address_from
        address_to = data.address_to
        routes_page.set_route(address_from, address_to)
        assert routes_page.get_from() == address_from
        assert routes_page.get_to() == address_to

    @classmethod
    def setup_class(cls):
        from selenium.webdriver.chrome.options import Options
        options = Options()
        options.set_capability("goog:loggingPrefs", {'performance': 'ALL'})
        cls.driver = webdriver.Chrome(options=options)
