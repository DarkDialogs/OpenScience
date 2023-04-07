# From the sfl module import the required functions
from dark_cookies.sfl import save_cookies
from time import sleep
import logging


# Class which handles the additional cookie captures which require a fresh webpage to be loaded.
class Cookie_Capture:
    def __init__(self, conf):
        # The WebDriver instance
        self.driver = conf.driver
        self.conf = conf
        # The domain of the website
        self.domain = conf.domain
        # The option to make the program fully automatic
        self.OPT_AUTO = conf.options.OPT_AUTO
        # The option to enable Cookie Rejector
        self.OPT_CR = conf.options.OPT_CR
        self.resultsDB = conf.resultsDB
        
        
    def additional_captures(self):
        """ Main function which triggers the other captures functions as required.
        """
        # Capture cookies after clicking the opt-in button.
        self.opt_in_button_capture()
        # Capture cookies after clicking the close button.
        self.close_button_capture()
        # Capture cookies after clicking the opt-out button.
        self.opt_out_button_capture()
        
    
    def close_button_capture(self):
        """ Function which is used to click the close button on the cookie dialog and record the number of cookies after.
        """
        # Call the button function to click close buttons.
        self.button_type_click("close option")
        
        
    def opt_in_button_capture(self):
        """ Function which is used to click the opt-in button on the cookie dialog and record the number of cookies after.
        """
        # Call the opt-in function to click opt-in buttons.
        self.button_type_click("opt-in option")
        
    def opt_out_button_capture(self):
        """ Function which is used to click the opt-out button on the cookie dialog and record the number of cookies after.
        """
        # Call the opt-in function to click opt-out buttons.
        if not self.OPT_CR:
            self.button_type_click("opt-out option")
        
        
    def button_type_click(self, button_type):
        """[summary]

        Args:
            button_type (String): the type of button we are wanting to click used to select css selectors from the database.
        """
        # Retrieve the details of all the clickables that were found on the cookie dialog
        if self.OPT_AUTO:
            clickables = self.resultsDB.clickables.select_clickableNum_autoType(self.domain)
        else:
            clickables = self.resultsDB.clickables.select_clickableNum_type(self.domain)
        clickables = {c[0]:c[1] for c in clickables}
        clickables_types = set(clickables.values())
        # If the close option was present on the cookie dialog then
        if button_type in clickables_types:
            logging.info("Capturing '"+ str(button_type) +"' cookies...")
            # Create a fresh webdriver instance
            self.conf.create_webdriver()
            button_num = list({c for c in clickables if clickables[c] == button_type})[0]
            button_html = self.resultsDB.clickables.select_rawHTML(self.domain, button_num)
            button_text = self.resultsDB.clickables.select_text(self.domain, button_num)
            try:
                # Get the css selector for the close button
                if self.OPT_AUTO:
                    clickable_selectors = self.resultsDB.clickables.select_CSSSelector_where_autoType(self.domain, button_type)
                else:
                    clickable_selectors = self.resultsDB.clickables.select_CSSSelector_where_type(self.domain, button_type)
                for clickable_selector in clickable_selectors:
                    clickable_selector = clickable_selector[0]
                    # Find the close button element on the webpage and click it.
                    buttons = self.conf.driver.find_elements_by_css_selector(clickable_selector)
                    for button in buttons:
                        html = button.get_attribute('outerHTML')
                        text = button.text
                        if html == button_html or text == button_text:
                            try:
                                button.click()
                                sleep(30)
                                # Save cookies after the close button was clicked using the sfl function
                                save_cookies(self.conf.driver, self.domain, self.resultsDB, button_type)
                                break
                            except Exception as e:
                                logging.debug("Error: Failed to click element.")
            except Exception as e:
                logging.debug("Error: Failed to "+str(button_type))
            finally:
                self.conf.close_webdriver()