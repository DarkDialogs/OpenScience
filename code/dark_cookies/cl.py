# Import the required Interfaces from the User Input Interface module.
from dark_cookies.uii import Clickable_Checker
# Import the preprocessing class from the Natrual Language Processing Module.
from dark_cookies.nlp import Preprocessor
# Import the Beatuiful soup library.
from bs4 import BeautifulSoup
# Import the By class from selenium.
from selenium.webdriver.common.by import By
import logging


# Class which handles the location and type identification of clickables on a cookie dialog.
class Clickable_Locator:
    def __init__(self, conf):
        # The WebDriver instance
        self.driver = conf.driver
        # The domain of the website
        self.domain = conf.domain
        # Enable to option to make the program fully automatic
        self.OPT_AUTO = conf.options.OPT_AUTO
        # The Preprocessor class instance used for text preprocesisng.
        self.preprocessor = Preprocessor()
        # Data folder name 
        self.data_folder_name = conf.options.DATA_FOLDER_NAME 
        self.resultsDB = conf.resultsDB
        self.hpdb = conf.hpdb
        
        
    def find_clickables(self):
        """Function to find all the clickables on a page, screenshot them and save them to the clickables table in the database.
        """
        # STEP 1: LOCATE ALL CANDIDATE CLICKABLES
        auto_clickable_types = self.locate_candidates()
        # STEP 2: FILTER ALL CANDIDATE CLICKABLES TO REMOVE DUPLICATES
        auto_clickable_types= self.filter_canididates(auto_clickable_types)
        # STEP 3: TYPE VALIDATION
        # If not automatic then prompt the user to validate the clickables.
        if not self.OPT_AUTO:
            self.manual_validation(auto_clickable_types)


    def locate_candidates(self):
        """Fuction to find all the clickables on a dialog, screenshot them and saved them to the clickables table in the database.

        Returns:
            dict[Integer -> String]: dictionary containing a mapping of clickable number to the type of clickable.
        """        
        # Get the valid dialog.
        selectors = self.resultsDB.dialogs.select_dialognum_selector_where_domain_checked(self.domain, 'True')
        (dialog_num, dialog_css_selector) = selectors[0]
        dialog_html = self.resultsDB.dialogs.select_rawHTML(self.domain, dialog_num)
        logging.info("Finding clickables for dialog #"+ str(dialog_num)+" with the css selector: '"+dialog_css_selector+"'"+"...")
        
        # Create a variable to store the number of clickables found on the page.
        clickable_nums = []
        
        # Retrieve all the css selectors for clickables from the database.
        clickable_selectors = self.hpdb.dictionaries.select_words("clickable_selectors").split("\n")
        
        #Create dictionary to store clickable types
        auto_clickable_types = {}

        # Check if dialog is an iframe
        is_iframe = False
        # Get the capture type of the dialog from the database
        capture_type = self.resultsDB.dialogs.select_captureType(self.domain, dialog_num)
        # If the dialog was an iframe then we need to switch to the iframe
        if capture_type[0:6] == "iframe":
            is_iframe = True
            try:
                iframe_num = int(dialog_css_selector)
                # Switch to the iframe
                self.driver.switch_to.frame(iframe_num)
                dialog_css_selector = ""
            except Exception as e:
                logging.debug("Failed to switch to iframe "+ str(iframe_num))

        # For each clickable selector, look for clickables using css selectors which commonly specifiy clickables.    
        for clickable_selector in clickable_selectors:
            clickable_selector = dialog_css_selector + " " + clickable_selector
            clickables = self.driver.find_elements_by_css_selector(clickable_selector)
            # For each clickable found using the css selector screenshot it and save it to the clickables database
            for clickable in clickables:
                clickable_text = clickable.text
                # If the clickable text is empty then
                raw_html = clickable.get_attribute('outerHTML')
                if clickable_text.replace(" ","") == "":
                    # Use beautiful soup to read the text
                    soup = BeautifulSoup(raw_html, 'html.parser')
                    # Get the text content from the html
                    clickable_text = soup.text
                    # If the text is still blank then get the text of the parent node.
                    if clickable_text.replace(" ","") == "":
                        try:
                            # Get parent of the clickable and search for text in that
                            clickable_text = clickable.find_element(By.XPATH, "./..").text
                        except Exception as e:
                            logging.debug("Failed to get the parent using css selector "+str(clickable_selector))
                # Function to translate the clickable text to English.
                clickable_text = self.preprocessor.translate_text(clickable_text)
                if raw_html in dialog_html:
                    # Save the clickable to the database with auto_type and type set to untagged
                    (clickable_num, parent) = self.save_clickable(self.domain, dialog_num,'untagged','untagged', clickable_selector, clickable_text, clickable)    
                    # If the clickable was added to the database then
                    if clickable_num != -1:
                        # Append it's number to the list of clickables.
                        clickable_nums.append(clickable_num)
                        # Auto tag the type of clickable
                        clickable_type = self.tag_button(clickable, clickable_text, clickable_num, parent)
                        auto_clickable_types[clickable_num] = clickable_type
                        # Update the auto_type of the clickable
                        self.resultsDB.clickables.update_autotype(self.domain, clickable_num, clickable_type)
        logging.info(str(len(clickable_nums)) + " clickables screenshotted and saved to the database.")
        
        # If the dialog is an iframe then we need to switch back to the default context.
        if is_iframe:
            self.driver.switch_to.default_content()
        return auto_clickable_types

        
    def filter_canididates(self, auto_clickable_types):
        """Function to filter out any invalid or duplicate clickables.

        Args:
            auto_clickable_types (dict[Integer -> String]): dictionary containing a mapping of clickable number to the type of clickable.

        Returns:
            dict[Integer -> String]: the updated dictionary containing a mapping of clickable number to the type of clickable.
        """
        # Get the clickable numbers
        clickable_nums = list(auto_clickable_types)
        # Create a copy of the clickable types
        final_auto_clickable_types = {c:auto_clickable_types[c] for c in auto_clickable_types}
        # Get the html content of each clickable and store it in a dictionary
        clickable_rawHTML = {c:self.resultsDB.clickables.select_rawHTML(self.domain, c) for c in clickable_nums}
        # Compare each clickable with the others
        for a in clickable_nums:
            for b in clickable_nums:
                if a != b:
                    # If the clickables have the same html then
                    if clickable_rawHTML[a] == clickable_rawHTML[b] and a in final_auto_clickable_types and b in auto_clickable_types:
                        # Remove the clickable from the dictionary
                        final_auto_clickable_types.pop(b)
                        # Update the clickable type in the dictionary to be
                        self.resultsDB.clickables.update_type(self.domain, b, "duplicate")
                        self.resultsDB.clickables.update_autotype(self.domain, b, "duplicate")
        # Update the clickbale types
        auto_clickable_types = final_auto_clickable_types
        
        return auto_clickable_types
    
    
    def manual_validation(self, auto_clickable_types):
        """ Function to prompt the user to manually validate the clickables.

        Args:
            auto_clickable_types ([type]): [description]
        """
        # Create list to store all the types of cookies that the user can choose from.
        possible_choices = ["other", "opt-in option","opt-out option","more options","preference slider", "confirm preferences", "close option", "policy link", "duplicate"]

        # Prompt the user to validate the type of cookie.
        app = Clickable_Checker(input_values=auto_clickable_types, choices=possible_choices, default_choice="other", data_folder_name=self.data_folder_name)
        app.mainloop()
        manual_clickable_types = app.result

        # Update the clickable type of each clickable based on the results the user tagged.
        for c in manual_clickable_types:
            self.resultsDB.clickables.update_type(self.domain, c, app.result[c].get())
            

    def tag_button(self, clickable, clickable_text, clickable_num, parent):
        """ Function to classify the type of clickable.

        Args:
            clickable_text (String): the text content of the clickable
            clickable_num (Integer): the number of the clickable corresponding to its entry in the database

        Returns:
            String: the type of the clickable.
        """
        # Preprocess the text
        clickable_text = clickable_text.replace("\n"," ")
        preprocessed_text = self.preprocessor.preprocess(clickable_text, normalise = True)
        # Get the html content of the clickable
        raw_html = self.resultsDB.clickables.select_rawHTML(self.domain, clickable_num)
        
        if parent:
            # TYPE: preference sliders
            # CASE: any word in keywords_preference_sliders
            keywords_preference_sliders = {"on","off"}
            if keywords_preference_sliders.intersection(preprocessed_text):
                    return "preference slider" + self.check_selected(clickable)
            # Check if the element is a preference slider
            # Parse the html with Beautiful soup
            soup = BeautifulSoup(raw_html, 'html.parser')
            # Retreieve the preference slider selectors from the database
            preference_slider_selectors = self.hpdb.dictionaries.select_words("clickable_preference_slider_selectors")
            if preference_slider_selectors != None:
                preference_slider_selectors = preference_slider_selectors.split("\n")
                # Create a list to store any preference slider
                preference_elements = []
                # For each selector
                for preference_selector in preference_slider_selectors:
                    # Select the elements using the selector
                    preference_elements += soup.select(preference_selector)
                # If there was a preference slider element then the clickable is a preference slider
                if preference_elements != []:
                    return "preference slider" + self.check_selected(clickable)
            return "other"
        
        # Check if the element is a preference slider
        # Parse the html with Beautiful soup
        soup = BeautifulSoup(raw_html, 'html.parser')
        # Retreieve the preference slider selectors from the database
        preference_slider_selectors = self.hpdb.dictionaries.select_words("clickable_preference_slider_selectors")
        if preference_slider_selectors != None:
            preference_slider_selectors = preference_slider_selectors.split("\n")
            # Create a list to store any preference sliders
            preference_elements = []
            # For each selector
            for preference_selector in preference_slider_selectors:
                # Select the elements using the selector
                preference_elements += soup.select(preference_selector)
            # If there was a close element then the clickable is a preference slider
            if preference_elements != []:                
                return "preference slider" + self.check_selected(clickable)
            
        # If there are more than 10 words on the clickable then it is likely not a useful clickable so return other
        if len(preprocessed_text) > 10:
            return "other"
        
        # Convert the preprocessed text to a set.
        preprocessed_text = set(preprocessed_text)
        
        # TYPE: preference sliders
        # CASE: any word in keywords_preference_sliders
        keywords_preference_sliders = {"on","off"}
        if keywords_preference_sliders.intersection(preprocessed_text):
                return "preference slider" + self.check_selected(clickable)
        
        # Key words for opting in to cookies
        keywords_opt_in = {"ok", "confirm", "accept", "agre","opt-in", "fine", "yes", "allow", "continu", "enabl","consent","understand", "understood","assent","enter", "okay","proceed","activ"}

        # TYPE: opt-out option
        # CASE: any word in keywords_opt_out_1
        keywords_opt_out_1 = {"disagre","reject","declin","refus","deactiv"}
        if keywords_opt_out_1.intersection(preprocessed_text):
            return "opt-out option"
        # CASE: any word in keywords_opt_in AND any word in keywords_opt_out_2
        keywords_opt_out_2 = {"necessari","essenti","requir"}
        if keywords_opt_in.intersection(preprocessed_text) and keywords_opt_out_2.intersection(preprocessed_text):
            return "opt-out option"
        # CASE: all words in keywords_opt_out_3 AND any word in keywords_opt_out_2
        keywords_opt_out_3 = {"cooki", "onli"}
        if not(keywords_opt_out_3.difference(preprocessed_text)) and keywords_opt_out_2.intersection(preprocessed_text):
            return "opt-out option"
        # CASE: all words in keywords_opt_out_3
        keywords_opt_out_3 = {"turn","cooki","off"}
        if not(keywords_opt_out_3.difference(preprocessed_text)):
            return "opt-out option"
        # CASE: any words in not_keywords_opt_out AND any word in keywords_opt_out_4
        keywords_opt_out_4 = {"not", "no", "dont"}
        keywords_opt_out_3 = {"track", "consent", "accept"}
        if keywords_opt_out_4.intersection(preprocessed_text) and keywords_opt_out_3.intersection(preprocessed_text):
            return "opt-out option"
        
        # CASE: all words in keywords_opt_out_5
        keywords_opt_out_5 = {"continu", "without", "accept"}
        if not(keywords_opt_out_5.difference(preprocessed_text)):
            return "opt-out option"

        # TYPE: confirm preferences
        # CASE: any word in keywords_confirm_preferences_1
        keywords_confirm_preferences_1 = {"save","submit"}
        if keywords_confirm_preferences_1.intersection(preprocessed_text):
                return "confirm preferences"
        # CASE: any word in keywords_opt_in AND any word in 2 keywords_confirm_preferences_2
        keywords_confirm_preferences_2 = {"select","choic","custom","prefer"}
        if keywords_opt_in.intersection(preprocessed_text) and keywords_confirm_preferences_2.intersection(preprocessed_text):
                return "confirm preferences"
            
        # TYPE: opt-in option
        # CASE: NOT any word in not_keywords_opt_in AND any word in keywords_opt_in
        not_keywords_opt_in = {"not","no","dont"}
        if not(not_keywords_opt_in.intersection(preprocessed_text)) and keywords_opt_in.intersection(preprocessed_text):
            return "opt-in option"
        # CASE: all words in all_keywords_opt_in_1 OR all word in all_keywords_opt_in_2
        all_keywords_opt_in_1 = {"got", "it"}
        all_keywords_opt_in_2 = {"i", "am", "happi", "with", "all", "cooki"}
        if not(all_keywords_opt_in_1.difference(preprocessed_text)) or not(all_keywords_opt_in_2.difference(preprocessed_text)):
            return "opt-in option"

        # TYPE: more options
        # CASE: any word in keywords_more_options
        keywords_more_options_1 = {'manag','prefer','set','choic','option','customis','custom',"personali","configur","advanc","purpos","tool","adjust"}
        if keywords_more_options_1.intersection(preprocessed_text):
            return "more options"
        # CASE: all words in keywords_more_options_2
        keywords_more_options_2 = {"let","me","choos"}
        if not(keywords_more_options_2.difference(preprocessed_text)):
            return "more options"
        # CASE: all words in keywords_more_options_2
        keywords_more_options_3 = {"select","cooki"}
        if not(keywords_more_options_3.difference(preprocessed_text)):
            return "more options"
        
        # TYPE: close option
        # CASE: any word in keywords_close
        keywords_close = {"close","dismiss","exit","x","×","hide"}
        if keywords_close.intersection(preprocessed_text):
                return "close option"
        # Check if the element is a close button
        # Parse the html with Beautiful soup
        soup = BeautifulSoup(raw_html, 'html.parser')
        # Retreieve the close button selectors from the database
        close_button_selectors = self.hpdb.dictionaries.select_words("clickable_close_selectors").split("\n")
        # Create a list to store any close elements found
        close_elements = []
        # For each selector
        for close_selector in close_button_selectors:
            # Select the elements using the selector
            close_elements += soup.select(close_selector)
        # If there was a close element then the clickable is a close button
        if close_elements != []:
            return "close option"

        # TYPE: policy link
        # CASE: any word in keywords_policy
        keywords_policy_1 = {'privaci',"polici","notic","here","cooki","vendor","partner"}
        if keywords_policy_1.intersection(preprocessed_text):
            return "policy link"
        # CASE: all word in keywords_policy_2
        keywords_policy_2 = {"use","of","cooki"}
        if not(keywords_policy_2.difference(preprocessed_text)):
            return "policy link"
        # CASE: all word in keywords_policy_3
        keywords_policy_3 = {"data","protect"}
        if not(keywords_policy_3.difference(preprocessed_text)) :
            return "policy link"
        # CASE: all word in keywords_policy_4
        keywords_policy_4 = {"terms","servic"}
        if not(keywords_policy_4.difference(preprocessed_text)) :
            return "policy link"
        # CASE: all word in keywords_policy_5
        keywords_policy_5 = {"read","more"}
        if not(keywords_policy_5.difference(preprocessed_text)) :
            return "policy link"
        # CASE: all word in keywords_policy_6
        keywords_policy_6 = {"learn","more"}
        if not(keywords_policy_6.difference(preprocessed_text)) :
            return "policy link"
        # CASE: all word in keywords_policy_7
        keywords_policy_7 = {"tell","me","more"}
        if not(keywords_policy_7.difference(preprocessed_text)) :
            return "policy link"
        # CASE: all word in keywords_policy_8
        keywords_policy_8 = {"more","inform"}
        if not(keywords_policy_8.difference(preprocessed_text)) :
            return "policy link"
        # CASE: all word in keywords_policy_9
        keywords_policy_9 = {"see","detail"}
        if not(keywords_policy_9.difference(preprocessed_text)) :
            return "policy link"
        # CASE: all word in keywords_policy_10
        keywords_policy_10 = {"more","detail"}
        if not(keywords_policy_10.difference(preprocessed_text)) :
            return "policy link"
        
        return "other"
    
    
    def check_selected(self, clickable):
        """Function to check if a clickable is selected and enabled. Used to check if preference sliders are selected.

        Args:
            clickable (Selenium element): the clickable element we want to check.

        Returns:
            String: either an empty string or "enabled" which specifies if the element was enabled or not.
        """
        # Additonal classifcation for prefence sliders which requires access to the selenum element.
        try:
            # If the clickable is selected and enabled then return enabled.
            if clickable.is_selected() and clickable.is_enabled():
                return " enabled"
            else:
                return ""
        except Exception as e:
            logging.debug("Failed to check if the clickable is enabled or selected.")
        return ""

    
    def save_clickable(self, domain, dialog_num, auto_type, type, css_selector, text, clickable):
        """Function to handle the saving of clickables to the database.

        Args:
            domain (String): a string specifiying the base domain of the webpage that we are analysing.
            dialog_num (Integer): the dialog number 
            auto_type (String): the automatically tagged type of the clickable
            type (String): the type of clickable
            css_selector (String): the css_selector used to select the clickable.
            text (String): the text content of the clickable.
            clickable (Selenium Element): the clickable element retreieved by the webdriver which will be screenshotted.

        Returns:
            [type]: [description]
        """
        # If the clickable cannot be added to the database return -1
        clickable_num = -1
        parent_bool = False
        try:
            #clickable_num = HPDatabase.get_next_clickable_num(domain)
            clickable_num = self.resultsDB.clickables.generate_clickable_num(domain)
            # Screenshot the clickable and save it to to the clikables folder using the clickable_num as the dialog number
            screenshot_location = self.data_folder_name + "/screenshots/clickables/"+str(clickable_num)+".png"
            clickable.screenshot(screenshot_location)
            # Add the clickable to the database
            self.resultsDB.clickables.insert_into(domain, clickable_num, dialog_num, auto_type, type, css_selector, text, clickable.get_attribute('outerHTML'), screenshot_location)
        except Exception as e:
            try:
                # If their was an erro screenshotting the clickable then try to screenshot the parent.
                parent = clickable.find_element(By.XPATH, "./..")
                parent.screenshot(screenshot_location)
                parent_bool = True
                self.resultsDB.clickables.insert_into(domain, clickable_num, dialog_num, auto_type, type, css_selector, text, clickable.get_attribute('outerHTML'), screenshot_location)
            except Exception as e:
                logging.debug("Failed to screenshot the clickable.")
                return -1, parent_bool
            
        return clickable_num, parent_bool