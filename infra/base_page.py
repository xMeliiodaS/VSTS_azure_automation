class BasePage:
    """
    Base class for all page objects. Contains common methods and attributes.
    """

    # Always get driver
    def __init__(self, driver):
        """
        Initialize the BasePage with a WebDriver instance.

        :param driver: The WebDriver instance to use for browser interactions.
        """
        self._driver = driver

    def refresh_page(self):
        """
        Refresh the current page.
        """
        self._driver.refresh()

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

    def get_current_url(self):
        return self._driver.current_url

    def navigate_back(self):
        """
        Navigate back in the browser history (Browser's back arrow).
        """
        self._driver.back()
