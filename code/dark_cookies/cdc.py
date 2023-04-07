# Import the required Interfaces from the User Input Interface module.
from dark_cookies.uii import Dialog_Checker, UII_Inputbox
# Import the beautiful soup library,
from bs4 import BeautifulSoup
# Import the timeit module.
import timeit
# Import the By keyword from the selenium library
from selenium.webdriver.common.by import By
# Import the decimal class
from decimal import *
# Import the Preprocessor class
from dark_cookies.nlp import Preprocessor
# Import the Image class from the pillow library
from PIL import Image
import logging

# Class which handles the location of cookie dialogs on a webpage.
class Cookie_Dialog_Collector:
    def __init__(self, conf):
        # The WebDriver instance
        self.driver = conf.driver
        # The domain of the website
        self.domain = conf.domain
        # The ngrams used to score dialogs
        self.dialog_ngrams = dict()
        # The maximum length of an ngram
        self.ngrams_num = 5
        # Enable to option to make the program fully automatic
        self.OPT_AUTO = conf.options.OPT_AUTO
        # Data folder name 
        self.data_folder_name = conf.options.DATA_FOLDER_NAME
        # The Preprocessor class instance used for text preprocesisng.
        self.preprocessor = Preprocessor()
        self.resultsDB = conf.resultsDB
        self.hpdb = conf.hpdb
        # Retreive the ngrams from the database.
        content = self.hpdb.dictionaries.select_words("dialog_ngrams").split("\n")
        # Parse the ngrams into the dictionary.
        for line in content:
            (n,ngrams) = line[:-1].split(":")
            self.dialog_ngrams[int(n)] = [str(n) for n in ngrams.split(',')]
        # Variables to store the dimensions of the webpage.
        self.rendered_width = 0
        self.rendered_height = 0


    def find_dialog(self):
        """Function used to handle the processing of finding a valid cookie dialog.

        Returns:
            Integer: the number of the correct dialog corresponding to a dialog stored in the database.
        """
        # Find the dimensions of the webpage.
        # Location of where to save screenshot of full webpage.
        im_location = self.data_folder_name + "/screenshots/dialogs/full.png"
        # Save screenshot of webpage
        self.driver.save_screenshot(im_location)
        # Open the image with pillow.
        im = Image.open(im_location)
        # Get the dimensions of the image.
        dims = im.size
        # Save the dimensions of the image.
        self.rendered_width = dims[0]
        self.rendered_height = dims[1] 
        # Close the image.
        im.close()      
        
        ### STEP 1: LOCATE ALL CANDIDATE DIALOGS
        dialog_nums = self.locate_candidates()

        ### STEP 2: RANK THE CANIDIDATE DIALOGS
        dialog_nums = self.rank_dialogs(dialog_nums)

        ### STEP 3: RANKING VALIDATION 
        # Check if the process should be automatic or include manual validation.
        # If automatic then select the highest ranked dialog.
        if self.OPT_AUTO:
            # If any dialogs were found then
            if len(dialog_nums) > 0:
                # Return the first dialog
                checked_dialog_num = dialog_nums[0]
                logging.debug("Selected dialog number " + str(checked_dialog_num) + " as the valid cookie dialog.")
            # Else Return -1
            else:
                checked_dialog_num = -1
                logging.debug("No cookie dialog was found.")
        # Else prompt the user to select or enter the valid dialog.
        else:
            checked_dialog_num = self.manual_validation(dialog_nums)
        
        # Set the checked field in the dialog table to be set to 'True' to indicate that this dialog has been checked by the user.
        self.resultsDB.dialogs.update_checked(self.domain, checked_dialog_num)
        
        self.check_for_cmps()
        
        return checked_dialog_num

    def check_for_cmps(self):
        raw_html = self.resultsDB.dialogs.select_rawHTML_where_checked_and_domain(self.domain)
        text = self.resultsDB.dialogs.select_text_where_checked_and_domain(self.domain).replace("\n", "").replace("\t", "")
        logging.debug(f"raw_html {raw_html}")
        logging.debug(f"text {text}")
        fingerprints = self.hpdb.cmp_fingerprints.select_all()
        logging.debug(f"cmp fingerprints {fingerprints}")
        for fingerprint in fingerprints:
            cmp_name, fingerprint_type, fingerprint_value = fingerprint
            logging.debug(f"name {cmp_name}")
            logging.debug(f"fingerprint_type {fingerprint_type}")
            logging.debug(f"fingerprint_value {fingerprint_value}")
            if fingerprint_type == "raw_html":
                if fingerprint_value in raw_html:
                    self.resultsDB.dialogs.update_cmp_where_checked(self.domain, cmp_name)
                    logging.info(f"The CMP provider for the dialog is '{cmp_name}'.")
                    return True
            elif fingerprint_type == "text":
                if fingerprint_value in text:
                    self.resultsDB.dialogs.update_cmp_where_checked(self.domain, cmp_name)
                    logging.warning(f"cmps found {cmp_name}")
                    return True
        logging.info(f"The dialog did not match any of the CMP fingerprints.")
        return False
    

    def manual_validation(self, dialog_nums):
        """Function to prompt the user to manually validate the dialogs or input another using a css selector.

        Args:
            dialog_nums (List<Integer>): list of the dialog numbers which are to be validated.

        Returns:
            Integer: the number of the correct dialog corresponding to a dialog stored in the database.
        """
        # Open the Dialog Checker tk window to allow the user to select the valid dialog from the those found on the page.
        app = Dialog_Checker(dialog_nums=dialog_nums, data_folder_name=self.data_folder_name)
        app.mainloop()
        checked_dialog_num = app.result.get()

        # Loop until a valid css selector has been inputted and validated by the user.
        while checked_dialog_num == -1:
            # Reset the dialog nums as any previous dialogs will have been marked as invalid by the user.
            dialog_nums = []
            # Ask the for the user to input a css selector for the dialog and store the string in the selector variable.
            app = UII_Inputbox(description='Enter the css selector for the cookie dialog:', title="Cookie Dialog CSS Selector Input")
            app.mainloop()
            selector = app.result.get()
            logging.debug("Selector: "+str(selector))
            # Check if the user inputted string is "" if so then return the checked_dialog_num (this will be -1)
            if selector == "":
                logging.info("The user did not input a selector.")
                # Add dark pattern for the case when their is no dark pattern present
                self.resultsDB.dark_patterns.insert_into(self.domain, 'no cookie dialog', str(True), str(True))
                return checked_dialog_num
            else:
                dialog_nums = self.search_selectors(self.driver, self.domain, [selector], "User Input")            
                app = Dialog_Checker(dialog_nums=dialog_nums)
                app.mainloop()
                checked_dialog_num = app.result.get()

        return checked_dialog_num


    
    def rank_dialogs(self, dialog_nums):
        """Function to determine a ranking for the cookie dialogs.

        Args:
            dialog_nums (List<Integer>): list of the dialog numbers which are to be ranked.

        Returns:
            List<Integer>: list of the ranked dialog numbers.
        """
        # If there are 0 or less dialogs in the list of dialog numbers then the list is already sorted so return it.
        if len(dialog_nums) == 0:
            return dialog_nums

        # Create a dictionary to store the scores of each dialog
        scores = {d:0 for d in dialog_nums}

        # Get the text, rawHTML and length of text for each dialog and store them in dictionaries.
        dialog_texts = {d:self.resultsDB.dialogs.select_text(self.domain,d) for d in dialog_nums}
        dialog_rawHTML ={d:self.resultsDB.dialogs.select_rawHTML(self.domain,d) for d in dialog_nums}
        dialog_captureType ={d:self.resultsDB.dialogs.select_captureType(self.domain,d) for d in dialog_nums}
        dialog_text_length = {d: len(dialog_texts[d].split()) for d in dialog_nums}
        # Calculate the average length of the text
        avg_dialog_text_length = sum( v for v in dialog_text_length.values() ) / len(dialog_text_length)
        
        
        # METHOD 0: Score dialogs based on their capture type
        for d in dialog_nums:
            if dialog_captureType[d] == "Specific Element Hiding Rules":
                scores[d] += 10
            elif dialog_captureType[d] == "General Element Hiding Rules (Quick)":
                scores[d] += 5
                
        # Create a dictioanry to store the final scores
        final_scores = {d:scores[d] for d in scores}
        
        # METHOD 1: Remove any dialogs with duplicate rawHTML
        final_dialog_nums = [d for d in dialog_nums]
        # Compare all of the dialogs
        for a in dialog_nums:
            for b in dialog_nums:
                if a != b:
                    # If the dialogs have the same HTML then remove one of them
                    if dialog_rawHTML[a] == dialog_rawHTML[b] and b in final_dialog_nums and a in final_dialog_nums:
                        final_dialog_nums.remove(b)
                        final_scores.pop(b)
        # Update the dialog numbers
        dialog_nums = [d for d in final_dialog_nums]
        
        # METHOD 2: Score the dialogs based on wether they contain dialog ngrams
        # Score is currently based on length of ngram - unigram = 1, bigram = 2, ...
        # For each dialog
        for a in dialog_nums:
            a_text = dialog_texts[a]
            # Split the text into sentences
            sentences = a_text.split("\n")
            a_text = []
            # For each sentence
            for s in sentences:
                # Preprocess the text and join it into 1 string
                test_text = " ".join(self.preprocessor.preprocess(s))
                # Add the sentence to the dialog text
                a_text.append(test_text)
            # Find all the ngrams for the dialog text
            a_text = self.preprocessor.find_ngrams(a_text, self.ngrams_num)
            # For each phrase in the dialog text
            for phrase in a_text:
                # Check if each phrase is in the list of ngrams
                for n in self.dialog_ngrams.keys():
                    if phrase in self.dialog_ngrams[n]:
                        scores[a] += n
            
        # METHOD 3: Check for overlapping html content (lowers rank of dialog with less html)
        # Compare all the dialogs to check if any dialogs are contained within other dialogs.
        for a in dialog_nums:
            for b in dialog_nums:
                if a != b:
                    a_html = dialog_rawHTML[a]
                    b_html = dialog_rawHTML[b]
                    # If the html of dialog b is a substring of the html of dialog b then
                    if b_html in a_html:
                        a_text = dialog_texts[a]
                        b_text = dialog_texts[b]
                        # If the text of the two dialogs is equal then
                        if a_text == b_text:
                            # Lower the score of the substring dialog.
                            scores[b] -= 1

        # METHOD 4: Check for text length less than 5 or greater than the average length of the text plus 100
        # For each dialog
        for a in dialog_nums:
            # If the length of the text is invalid then
            if dialog_text_length[a] < 5 or dialog_text_length[a] > avg_dialog_text_length+100:
                # Lower the score of the dialog
                scores[a] -= 20

        # METHOD 5: Check for empty text content
        # For each dialog
        for a in dialog_nums:
            a_text = dialog_texts[a]
            #if the text content is empty then lower the score.
            if a_text.rstrip() == "":
                    scores[a] -= 100
                    
        # Update scores of each dialog in database
        final_dialog_nums = [d for d in dialog_nums] 
        for d in scores:       
            self.resultsDB.dialogs.update_score(self.domain, d, scores[d])
        
        # Remove any dialogs with score of 0 or less
        scores = {d:scores[d] for d in final_scores}
        for d in scores:
            if scores[d] <= 0:
                final_dialog_nums.remove(d)
                final_scores.pop(d)
        dialog_nums = [d for d in final_dialog_nums]
        scores = {d:scores[d] for d in final_scores}
        
        # Rank the dialogs by their scores
        scores = {key: value for key, value in sorted(scores.items(), key=lambda item: (-item[1], item[0]))}
        dialog_nums = list(scores)
        
        return dialog_nums


    def locate_candidates(self):
        """Fuction to find all the dialogs on a page, screenshot them and saved them to the dialogs table in the database.

        Returns:
            List<Integer>: list of the candidate dialogs numbers corresponding to dialogs in the database.
        """
        # Total number of dialogs (iframes are not counted)
        num_dialogs = 0
        # Dialog Numbers of the newly found dialogs
        dialog_nums = []
        
        ### ROUND 1.1: SPECIFIC SELECTORS
        logging.info("Finding dialogs for the domain: '"+str(self.domain)+"'.")
        # Get the specific element hiding rules from the database corresponding to the url
        specific_element_hiding_rules = self.hpdb.specific_element_hiding_rules.select_selector(self.domain)
        logging.debug("Retrieved " + str(len(specific_element_hiding_rules)) + " specific element hiding rules for the domain: '"+ str(self.domain) + "'")
        # Search for dialogs using the specific element hiding rules.
        dialog_nums += self.search_selectors(self.driver, self.domain, specific_element_hiding_rules, "Specific Element Hiding Rules")
        
        ### ROUND 1.2: iframes
        # Locate any <iframe> tags on the page
        iframes = len(self.driver.find_elements(By.TAG_NAME, "iframe"))
        logging.debug("Found " + str(iframes)+ " iframes.")
        # Number of iframes saved successfully
        num_iframes = 0
        # For each iframe
        for i in range(0, iframes):
            try:
                # Switch the context to the iframe
                self.driver.switch_to.frame(i)
                # Get the raw html of the iframe
                raw_html = self.driver.page_source
                # Locate the <body> tag on the iframe
                body = self.driver.find_element(By.TAG_NAME, "body")
                # Get the dialog number for the iframe
                dialog_num = self.resultsDB.dialogs.generate_dialog_num(self.domain)
                # Screenshot the dialog and save it to to the dialogs folder using the dialog_num as the dialog number.
                screenshot_location = self.data_folder_name + "/screenshots/dialogs/"+str(dialog_num)+".png"
                body.screenshot(screenshot_location)
                # Translate the dialog text to English
                dialog_text = self.preprocessor.translate_text(body.text)
                # Insert the diframe into the dialogs table in the database.
                self.resultsDB.dialogs.insert_into(self.domain, dialog_num, "False", "iframe", None,  i, dialog_text, raw_html, screenshot_location)
                # Add the dialog number to the list of dialog numbers
                dialog_nums.append(dialog_num)
                # Increment the number of iframes saved successfully.
                num_iframes += 1
            # Catch any exception
            except Exception as e:
                logging.debug("Screenshot failed for iframe " + str(i)+".")
            # Return to context to the defult page 
            self.driver.switch_to.default_content()

        ### ROUND 1.3: QUICK GENERAL SELECTORS
        # If the specific element hiding rules didnt find any dialogs then try using the general element hiding rules.
        start = timeit.default_timer()
        # Get the general element hiding rules from the database.
        general_element_hiding_rules = set(self.hpdb.general_element_hiding_rules.select_selector())
        logging.debug("Retrieved " + str(len(general_element_hiding_rules)) + " general element hiding rules.")
        logging.debug("Searching for dialogs using general css selectors...")
        # Create a set to store all the valid selectors
        valid_selectors = set()
        # Get the html content of the webpage
        html = self.driver.page_source
        # Check if the string of each general rule is present in the source document
        for selector in general_element_hiding_rules:
            # If the selector starts with a # or . then remove the first character before searching
            if(selector[0] == '#' or selector[0] == "."): 
                if(selector[1:] in html):
                    valid_selectors.add(selector)
            elif(selector in html):
                    valid_selectors.add(selector)
        # Search using the general selectors that were present in the string content of the webpage.
        dialog_nums += self.search_selectors(self.driver, self.domain, valid_selectors, "General Element Hiding Rules (Quick)")
        stop = timeit.default_timer()
        #logging.debug('Took '+ str(stop - start) + 's to quick search all general selectors (quick)')
            
        ### ROUND 1.4: Search div tags for common terms
        dialog_selectors = self.hpdb.dictionaries.select_words("dialog_additional_div_selectors").split("\n")
        dialog_nums += self.search_selectors(self.driver, self.domain, dialog_selectors, "div Keyword CSS Selectors")
        ### ROUND 1.5: Search all tags for common terms
        dialog_selectors = self.hpdb.dictionaries.select_words("dialog_additional_selectors").split("\n")
        dialog_nums += self.search_selectors(self.driver, self.domain, dialog_selectors, "Keyword CSS Selectors")
        num_dialogs = len(dialog_nums) - num_iframes
        
        ### ROUND 2: DEEP GENERAL SELECTORS
        # Search using all the general css selectors we haven't tried already
        # NOTE: this round is time consuming so it is currently disabled.
        OPT_DEEP = False
        if (num_dialogs <= 0 and OPT_DEEP):
            start = timeit.default_timer()
            valid_selectors = general_element_hiding_rules.difference(valid_selectors)
            logging.debug(len(valid_selectors))
            dialog_nums += self.search_selectors_deep(self.driver, self.domain, valid_selectors, "General Element Hiding Rules (Deep)")
            stop = timeit.default_timer()
            logging.debug('Took '+ str(stop - start) + 's to deep search all general selectors (deep)')
            num_dialogs = len(dialog_nums) - num_iframes
                
        # Print the number of dialogs that were successfully screenshotted and saved.
        logging.debug(str(len(dialog_nums)) + " candidate dialogs screenshotted and saved to the database.")
        return dialog_nums
    
    
    def save_dialog(self, domain, checked, dialog,  capture_type, css_selector):
        """ Function to handle the saving of dialogs to the database.

        Args:
            domain (String): a string specifiying the base domain of the webpage that we are analysing.
            checked (String): value which specifies if the dialog has been checked by the user.
            dialog (Selenium element): the dialog element retreieved by the webdriver which will be screenshotted.
            capture_type (String): a string specifying the method used to capture the dialog.
            css_selector (String): a string specifying the css selector used to find the dialog.

        Returns:
            Integer: the number of the dialog that was added to the database.
        """
        # Get the dialog number used to index the dialogsin the database.
        dialog_num = self.resultsDB.dialogs.generate_dialog_num(domain)
        # Screenshot the dialog and save it to to the dialogs folder using the dialog_num as the dialog number.
        screenshot_location = self.data_folder_name +"/screenshots/dialogs/"+str(dialog_num)+".png"
        location = dialog.location
        size = dialog.size
        width = location['x'] + size['width']
        height = location['y'] + size['height']
        if width > self.rendered_width:
            logging.debug("Element outwidth viewable page.")
            dialog_num = -1
        else:
            try:
                dialog.screenshot(screenshot_location)
            except Exception as e:
                pass
                try:
                    #parent = dialog.find_element(By.XPATH, "./..")
                    #parent.screenshot(screenshot_location)
                    child = dialog.find_element(By.XPATH, "//*")
                    child.screenshot(screenshot_location)
                except Exception as e:
                    logging.debug(e)
                    pass
            # Translate the text of the dialog
            dialog_text = self.preprocessor.translate_text(dialog.text) 
            # Save the dialog to the database.
            self.resultsDB.dialogs.insert_into(domain, dialog_num, checked, capture_type, None, css_selector, dialog_text, dialog.get_attribute('outerHTML'), screenshot_location)
        
        # Check if the css selector has been inputted by the user, if so then add the selector to the specific_element_hiding_rules table.
        if capture_type == "User Input":
            try:
                self.hpdb.specific_element_hiding_rules.insert_into(domain, css_selector, 'User Input')
            except Exception as e:
                logging.debug(e)
                pass
        return dialog_num


    def search_selectors(self, driver, domain, selectors, capture_type):
        """Function to search for dialogs using a list of css selectors.

        Args:
            driver (WebDriver): an instance of a selenium webdriver used to interact with the webpage.
            domain (String): a string specifiying the base domain of the webpage that we are analysing.
            selectors (List[String]): the css selectors that we want to search using.
            capture_type (String): a string specifying the method used to capture the dialog.

        Returns:
            List[Integers]: the candidate dialog numbers corresponding to dialogs in the database.
        """
        # Create a list to store the dialog numbers
        dialog_nums = []
        # For each selector search using the selector and save any dialogs found to the database.
        for selector in selectors:
            # Find elements using a css selector and store them in the results variable.
            results = driver.find_elements_by_css_selector(selector)
            # For each dialog in the results screenshot and save the dialog to the dialogs table in the database.
            for dialog in results:
                #logging.debug("Dialog found for css selector: '"+selector+"'.")
                # Attempt to screenshot and save the dialog to the dialogs table in the database.
                try:
                    # Save the dialog to the database.
                    dialog_num = self.save_dialog(domain, 'False', dialog,capture_type,selector)
                    if dialog_num != -1:
                        #logging.debug("Screenshot for css selector: '"+selector+"' saved as '"+str(dialog_num)+".png'.")
                        # Add the new dialog num to the list of dialog numbers
                        dialog_nums.append(dialog_num)
                # Catch any exceptions that may occur and print an error message.
                except Exception as e:
                    logging.debug("Screenshot failed for css selector '"+selector+"'.")
        return dialog_nums


    def search_selectors_deep(self, driver, domain, selectors, capture_type, OPT_FIND_ONE=True):
        """ Function to search for dialogs using a list of css selectors using beautiful soup to speed up the search process.

        Args:
            driver (WebDriver): an instance of a selenium webdriver used to interact with the webpage.
            domain (String): a string specifiying the base domain of the webpage that we are analysing.
            selectors (List[String]): the css selectors that we want to search using.
            capture_type (String): a string specifying the method used to capture the dialog.
            OPT_FIND_ONE (bool, optional): an option specifying if we should just find the first valid css selector.

        Returns:
            List[Integers]: the candidate dialog numbers corresponding to dialogs in the database.
        """
        # Get the html content of the webpage
        html = driver.page_source
        # intialise the beautiful soup html parser
        bso = BeautifulSoup(html, 'html.parser')

        # Create a set to store all the valid css selectors
        valid_selectors = set()
        # For each selector search using the selector.
        for selector in selectors:
            try:
                # Use the select method to search for elements with the css selector.
                results = bso.select(selector)
                # if results is not empty then add the selector to the set of valid selectors.
                if results != []:
                    valid_selectors.add(selector)
                    # If option specifying if we should just find the first valid css selector is enabled
                    # the break the loop once we find a css selector, this speeds up the search process as we don't always have to search all selectors.
                    if OPT_FIND_ONE:
                        break
            except Exception as e:
                logging.debug("Failed to search using the following css selector: '"+selector+"'")
        # Search for each valid selector and save any dialogs to the database.
        dialog_nums = self.search_selectors(driver, domain, valid_selectors, capture_type)
        return dialog_nums