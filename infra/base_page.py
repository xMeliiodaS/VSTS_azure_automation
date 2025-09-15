from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC


class BasePage:
    """
    Base class for all page objects. Contains common methods and attributes.
    """

    def __init__(self, driver, default_timeout: int = 20):
        """
        Initialize the BasePage with a WebDriver instance.

        :param driver: The WebDriver instance to use for browser interactions.
        """
        self._driver = driver
        self._timeout = default_timeout

    # ---------- Core ----------
    def refresh_page(self):
        self._driver.refresh()

    def get_current_url(self):
        return self._driver.current_url

    def navigate_back(self):
        self._driver.back()

    # ---------- Wait helpers ----------
    def wait_visible(self, by: By, value: str, timeout: int | None = None):
        return WebDriverWait(self._driver, timeout or self._timeout).until(
            EC.visibility_of_element_located((by, value))
        )

    def wait_clickable(self, by: By, value: str, timeout: int | None = None):
        return WebDriverWait(self._driver, timeout or self._timeout).until(
            EC.element_to_be_clickable((by, value))
        )

    def wait_present(self, by: By, value: str, timeout: int | None = None):
        return WebDriverWait(self._driver, timeout or self._timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def scroll_to_element(self, element):
        """
        Scroll the specified element into view and center it in the middle of the screen.

        :param element: The WebElement to scroll into view.
        """
        self._driver.execute_script("""
            var element = arguments[0];
            element.scrollIntoView({
                block: 'center',
                behavior: 'smooth'
            });
        """, element)

    def navigate_with_retry(self, url: str, retries: int = 3):
        """Navigate to a URL and retry if the page fails to load completely."""
        for attempt in range(1, retries + 1):
            try:
                self._driver.get(url)
                WebDriverWait(self._driver, self._timeout).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                return
            except TimeoutException:
                print(f"[BasePage] Attempt {attempt} failed, refreshing page...")
                self._driver.refresh()
        raise TimeoutException(f"Failed to load {url} after {retries} attempts")
