import data
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


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

    # Tarifa Comfort y botón principal
    smart_button = (By.XPATH, '//button[contains(text(), "Pedir un taxi")]')
    comfort_tariff_button = (By.XPATH,
                             "//*[contains(text(), 'Comfort')]/ancestor::div[contains(@class, 'tarriff-card') or contains(@class, 'card')]")

    # Modal Teléfono
    phone_button = (By.CLASS_NAME, 'np-text')
    phone_input = (By.ID, 'phone')
    next_button_phone = (By.XPATH, '//button[contains(text(), "Siguiente")]')
    code_input = (By.ID, 'code')
    confirm_button_phone = (By.XPATH, '//button[contains(text(), "Confirmar")]')

    # Pago
    payment_method_value = (By.CLASS_NAME, 'pp-value')
    payment_method_button = (By.CLASS_NAME, 'pp-text')
    add_card_button = (By.XPATH, '//div[contains(@class, "pp-row") and .//div[text()="Agregar tarjeta"]]')
    card_number_field = (By.ID, 'number')
    card_code_field = (By.XPATH, '//div[contains(@class, "card-code-input")]//input[@id="code"]')

    # Botón "Agregar" en el modal de tarjeta
    link_card_button = (By.XPATH, '//div[@class="pp-buttons"]//button[type="submit" or text()="Agregar"]')

    # Botón "X" de cierre
    close_payment_modal = (By.XPATH, '//div[contains(@class, "payment-picker")]//button[contains(@class, "close-button")]')

    # Extras y Comentarios
    driver_message_field = (By.ID, 'comment')
    blanket_switch = (By.XPATH,
                      "//div[contains(text(), 'Manta')]/following-sibling::div[contains(@class, 'r-sw')]//span[contains(@class, 'slider')]")
    blanket_checkbox = (By.XPATH,
                        "//div[contains(text(), 'Manta')]/following-sibling::div[contains(@class, 'r-sw')]//input")

    ice_cream_plus_button = (By.XPATH,
                             "//div[contains(text(), 'Helado')]/following-sibling::div[contains(@class, 'r-counter')]//div[contains(@class, 'counter-plus')]")
    ice_cream_count = (By.XPATH,
                       "//div[contains(text(), 'Helado')]/following-sibling::div[contains(@class, 'r-counter')]//div[contains(@class, 'counter-value')]")

    order_taxi_button = (By.XPATH, '//button[contains(@class, "smart-button") or contains(., "Pedir un taxi")]')
    search_modal = (By.CLASS_NAME, 'order-body')
    driver_info_modal = (By.CLASS_NAME, 'order-header-title')

    def __init__(self, driver):
        self.driver = driver

    def set_from(self, from_address):
        field = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.from_field)
        )
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        field.send_keys(from_address)

    def set_to(self, to_address):
        field = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.to_field)
        )
        field.send_keys(Keys.CONTROL + "a")
        field.send_keys(Keys.BACKSPACE)
        field.send_keys(to_address)

    def set_route(self, from_address, to_address):
        self.set_from(from_address)
        self.set_to(to_address)

    def get_from(self):
        return self.driver.find_element(*self.from_field).get_property('value')

    def get_to(self):
        return self.driver.find_element(*self.to_field).get_property('value')

    def select_comfort_tariff(self):
        comfort_card = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH,
                                            "//div[contains(@class, 'tarriff-card')]//div[text()='Comfort'] | //*[contains(text(), 'Comfort')]"))
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", comfort_card)
        self.driver.execute_script("arguments[0].click();", comfort_card)

    def click_phone_button(self):
        phone_btn = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.phone_button)
        )
        self.driver.execute_script("arguments[0].click();", phone_btn)

    def set_phone_number(self, phone_number):
        phone_field = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.phone_input)
        )
        phone_field.clear()
        phone_field.send_keys(phone_number)

    def click_next_phone(self):
        next_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.next_button_phone)
        )
        next_button.click()

    def enter_phone_code(self, code):
        code_field = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.code_input)
        )
        code_field.clear()
        code_field.send_keys(code)
        self.click_confirm_phone()

    def click_confirm_phone(self):
        confirm_btn = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.confirm_button_phone)
        )
        self.driver.execute_script("arguments[0].click();", confirm_btn)

    def add_credit_card(self, card_number, card_code):
        # 1. Abrir modal de Método de pago
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.payment_method_button)
        ).click()

        # 2. Clic en "Agregar tarjeta"
        add_card = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.add_card_button)
        )
        self.driver.execute_script("arguments[0].click();", add_card)

        # 3. Ingresar número de tarjeta
        card_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.card_number_field)
        )
        card_input.clear()
        card_input.send_keys(card_number)

        # 4. Ingresar CVV y presionar TAB para desenfocar (habilita el botón "Agregar")
        code_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.card_code_field)
        )
        code_input.clear()
        code_input.send_keys(card_code)
        code_input.send_keys(Keys.TAB)

        # 5. Clic en el botón azul "Agregar"
        link_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.link_card_button)
        )
        link_btn.click()

        # 6. Cerrar el modal de Método de pago (clic en la X)
        close_btn = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.close_payment_modal)
        )
        self.driver.execute_script("arguments[0].click();", close_btn)

    def get_payment_method_text(self):
        return WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.payment_method_value)
        ).text

    def set_driver_message(self, message):
        msg_field = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.driver_message_field)
        )
        msg_field.send_keys(message)

    def order_blanket_and_tissues(self):
        blanket = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.blanket_switch)
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", blanket)
        self.driver.execute_script("arguments[0].click();", blanket)

    def add_ice_creams(self, count: int = 2):
        plus_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.ice_cream_plus_button)
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", plus_btn)

        for _ in range(count):
            self.driver.execute_script("arguments[0].click();", plus_btn)

    def click_order_taxi(self):
        order_btn = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.order_taxi_button)
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", order_btn)
        self.driver.execute_script("arguments[0].click();", order_btn)


class TestUrbanRoutes:
    def setup_method(self):
        options = Options()
        options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        self.driver = webdriver.Chrome(options=options)
        self.driver.get(data.urban_routes_url)
        self.routes_page = UrbanRoutesPage(self.driver)

    def teardown_method(self):
        self.driver.quit()

    def prepare_order(self):
        self.routes_page.set_route(data.address_from, data.address_to)
        self.routes_page.click_order_taxi()
        self.routes_page.select_comfort_tariff()

    def test_set_route(self):
        self.routes_page.set_route(data.address_from, data.address_to)
        assert self.routes_page.get_from() == data.address_from
        assert self.routes_page.get_to() == data.address_to

    def test_select_comfort_tariff(self):
        self.routes_page.set_route(data.address_from, data.address_to)
        self.routes_page.click_order_taxi()
        self.routes_page.select_comfort_tariff()
        active_tariff = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'tarriff-card') and contains(@class, 'active')]//div[contains(@class, 'name')] | //*[contains(text(), 'Comfort')]"))
        )
        assert "Comfort" in active_tariff.text

    def test_set_phone_number(self):
        self.prepare_order()
        self.routes_page.click_phone_button()
        self.routes_page.set_phone_number(data.phone_number)
        self.routes_page.click_next_phone()

        code = retrieve_phone_code(self.driver)
        self.routes_page.enter_phone_code(code)

        phone_button = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.routes_page.phone_button)
        )
        assert phone_button.text != ""

    def test_add_credit_card(self):
        self.prepare_order()
        self.routes_page.add_credit_card(data.card_number, data.card_code)

        # Leemos la casilla que cambia dinámicamente (.pp-value)
        payment_value = self.routes_page.get_payment_method_text()
        assert '9100' in payment_value or 'Tarjeta' in payment_value

    def test_set_driver_message(self):
        self.prepare_order()
        self.routes_page.set_driver_message(data.message_for_driver)
        comment_field = self.driver.find_element(*self.routes_page.driver_message_field)
        assert comment_field.get_attribute("value") == data.message_for_driver

    def test_order_blanket_and_tissues(self):
        self.prepare_order()
        self.routes_page.order_blanket_and_tissues()
        blanket = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.routes_page.blanket_checkbox)
        )
        assert blanket.is_selected()

    def test_add_two_ice_creams(self):
        self.prepare_order()
        self.routes_page.add_ice_creams(2)
        count = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.routes_page.ice_cream_count)
        )
        assert count.text == "2"

    def test_search_taxi_modal_is_displayed(self):
        self.prepare_order()

        # 1. Teléfono y código
        self.routes_page.click_phone_button()
        self.routes_page.set_phone_number(data.phone_number)
        self.routes_page.click_next_phone()
        code = retrieve_phone_code(self.driver)
        self.routes_page.enter_phone_code(code)

        # 2. Tarjeta y adicionales
        self.routes_page.add_credit_card(data.card_number, data.card_code)
        self.routes_page.set_driver_message(data.message_for_driver)
        self.routes_page.order_blanket_and_tissues()
        self.routes_page.add_ice_creams(2)

        # 3. Pedir taxi (clic directo sobre el botón inteligente principal)
        smart_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "smart-button"))
        )
        self.driver.execute_script("arguments[0].click();", smart_btn)

        # 4. Validar la presencia del modal (.order-body)
        modal = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.routes_page.search_modal)
        )
        assert modal.is_displayed()