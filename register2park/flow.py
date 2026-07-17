from __future__ import annotations

import time
from collections.abc import Sequence
from dataclasses import dataclass

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from register2park.config import RegistrationConfig

REGISTER2PARK_URL = "https://register2park.com"


class FlowError(RuntimeError):
    """Raised when the live registration workflow cannot continue safely."""


@dataclass(frozen=True, slots=True)
class Selectors:
    register_button: tuple[str, str] = (By.CSS_SELECTOR, "a.btn.btn-lg.btn-info")
    property_search: tuple[str, str] = (By.ID, "propertyName")
    confirm_property: tuple[str, str] = (By.ID, "confirmProperty")
    property_result: tuple[str, str] = (By.CSS_SELECTOR, "button.select-property")
    visitor_registration: tuple[str, str] = (By.ID, "registrationTypeVisitor")
    unit: tuple[str, str] = (By.ID, "vehicleApt")
    vehicle_make: tuple[str, str] = (By.ID, "vehicleMake")
    vehicle_model: tuple[str, str] = (By.ID, "vehicleModel")
    plate: tuple[str, str] = (By.ID, "vehicleLicensePlate")
    plate_confirmation: tuple[str, str] = (By.ID, "vehicleLicensePlateConfirm")
    vehicle_information_submit: tuple[str, str] = (By.ID, "vehicleInformation")
    email_confirmation: tuple[str, str] = (By.ID, "email-confirmation")
    email_input: tuple[str, str] = (By.ID, "emailConfirmationEmailView")
    email_send: tuple[str, str] = (By.ID, "email-confirmation-send-view")


class ParkingRegistrationFlow:
    def __init__(
        self,
        config: RegistrationConfig,
        *,
        timeout_seconds: float = 15,
        headless: bool = False,
        keep_open_seconds: float = 8,
        selectors: Selectors | None = None,
    ) -> None:
        self.config = config
        self.timeout_seconds = timeout_seconds
        self.headless = headless
        self.keep_open_seconds = keep_open_seconds
        self.selectors = selectors or Selectors()

    def run(self, *, submit: bool) -> str:
        driver: webdriver.Chrome | None = None
        try:
            driver = _build_driver(headless=self.headless)
            wait = WebDriverWait(driver, self.timeout_seconds)
            driver.get(REGISTER2PARK_URL)
            print("Opened the registration site.")

            wait.until(EC.element_to_be_clickable(self.selectors.register_button)).click()
            print("Opened the guest registration flow.")

            self._select_property(wait)
            wait.until(EC.element_to_be_clickable(self.selectors.visitor_registration)).click()
            print("Selected visitor registration.")

            self._fill_vehicle_form(wait)
            print("Filled the private vehicle form without printing its values.")

            if not submit:
                print("Review mode complete. No registration was submitted.")
                return "reviewed"

            wait.until(
                EC.element_to_be_clickable(self.selectors.vehicle_information_submit)
            ).click()
            print("Submitted the authorized vehicle registration.")

            try:
                self._request_email_confirmation(wait)
            except (TimeoutException, WebDriverException):
                print(
                    "Registration submitted, but the confirmation email step did not finish. "
                    "Check the existing registration before attempting another submission."
                )
                return "submitted_without_email"
            else:
                print("Requested the confirmation email.")
                return "submitted"
        except TimeoutException as exc:
            raise FlowError(
                "The site did not reach the expected step before the timeout. "
                "Review the current page and selectors before retrying."
            ) from exc
        except WebDriverException as exc:
            raise FlowError(f"The browser workflow failed: {exc.msg}") from exc
        finally:
            if driver is not None and self.keep_open_seconds > 0:
                time.sleep(self.keep_open_seconds)
            if driver is not None:
                driver.quit()

    def _select_property(self, wait: WebDriverWait) -> None:
        search = wait.until(EC.visibility_of_element_located(self.selectors.property_search))
        _replace_text(search, self.config.property_query)
        wait.until(EC.element_to_be_clickable(self.selectors.confirm_property)).click()

        buttons = wait.until(EC.presence_of_all_elements_located(self.selectors.property_result))
        labels = [_result_context(button) for button in buttons]
        result_index = find_property_result(labels, self.config.property_result_match)
        buttons[result_index].click()
        print("Selected the configured property result.")

    def _fill_vehicle_form(self, wait: WebDriverWait) -> None:
        fields = (
            (self.selectors.unit, self.config.unit),
            (self.selectors.vehicle_make, self.config.vehicle_make),
            (self.selectors.vehicle_model, self.config.vehicle_model),
            (self.selectors.plate, self.config.license_plate),
            (self.selectors.plate_confirmation, self.config.license_plate),
        )
        for locator, value in fields:
            element = wait.until(EC.visibility_of_element_located(locator))
            _replace_text(element, value)

    def _request_email_confirmation(self, wait: WebDriverWait) -> None:
        wait.until(EC.element_to_be_clickable(self.selectors.email_confirmation)).click()
        email_input = wait.until(EC.element_to_be_clickable(self.selectors.email_input))
        _replace_text(email_input, self.config.confirmation_email)
        wait.until(EC.element_to_be_clickable(self.selectors.email_send)).click()


def find_property_result(labels: Sequence[str], expected_text: str) -> int:
    if not labels:
        raise FlowError("The property search returned no selectable results.")

    expected = expected_text.casefold()
    matches = [index for index, label in enumerate(labels) if expected in label.casefold()]

    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise FlowError("More than one property result matched the configured text.")
    if len(labels) == 1:
        raise FlowError(
            "The only property result did not contain property.result_match. "
            "Update the private config after visually checking the result."
        )
    raise FlowError("No property result matched property.result_match.")


def _build_driver(*, headless: bool) -> webdriver.Chrome:
    options = Options()
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1440,1000")
    else:
        options.add_argument("--start-maximized")
    return webdriver.Chrome(options=options)


def _replace_text(element: WebElement, value: str) -> None:
    element.clear()
    element.send_keys(value)


def _result_context(button: WebElement) -> str:
    parent = button.find_element(By.XPATH, "..")
    return parent.text.strip()
