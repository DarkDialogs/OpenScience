# Import the required Interfaces from the User Input Interface module.
from dark_cookies.uii import Checkbox_Input
from dark_cookies.id_like_checker import is_id_cookie
# Import the textstat module, used for text readability metrics.
import textstat
# Import the opencv pip module, used for image processing.
import cv2
import logging
import tldextract
import sqlite3

# Class which handles the automatic detection of Dark Patterns on the inital cookie dialog.
class Automatic_Dark_Patterns():
    def __init__(self, conf):
        # The WebDriver instance
        self.driver = conf.driver
        # The domain of the website
        self.domain = conf.domain
        # Enable to option to make the program fully automatic
        self.data_folder_name = conf.options.DATA_FOLDER_NAME 
        self.OPT_AUTO = conf.options.OPT_AUTO
        self.OPT_SAVE_COOKIES = conf.options.OPT_SAVE_COOKIES
        self.resultsDB = conf.resultsDB
    

    def find_dps(self):
        """ Function to find the auto dark patterns, get the user to validate them and add them to the database.
        """
        logging.info("Auto Detecting DPs for '"+str(self.domain)+"'...")
        # Define the intial values of the dark patterns (as tagged by the automatically)
        
        # Dark pattern descriptions
        dark_patterns_desc = {#"DP0" : "No Cookie Dialog present.",
                         "DP1" : "Only Opt-in option is present on initial Cookie Dialog.",
                         "DP2" : "Background color of Opt-in button leads to it being highlighted more compared to Opt-out button.",
                         "DP3" : "Dialog Obstructs the window.",
                         "DP4" : "Large amount of text on cookie dialog.",
                         "DP5" : "Multiple layers to a cookie dialog.",
                         "DP6" : "Ambiguous Close button (in addition to Accept button).",
                         "DP7" : "Multiple distinct Cookie Dialogs present on a page.",
                         "DP8" : "At least one Preference Slider is enabled by default.",
                         "DP9" : "Clicking Close button leads to more cookies being selected.",
                         "DP11": "More cookies are set regardless of Opt-out button being clicked."}
        # Create a dictionart to store the dark pattern values.
        dark_patterns = {d:False for d in dark_patterns_desc}
        
        # Get clickables numbers and store them in a dictionary.
        if self.OPT_AUTO:
            clickables = self.resultsDB.clickables.select_clickableNum_autoType(self.domain)
        else:
            clickables = self.resultsDB.clickables.select_clickableNum_type(self.domain)
        clickables = {c[0]:c[1] for c in clickables}
        # get the clickable types and store them in a set.
        clickables_types = set(clickables.values())
        
        # Analyse the cookie captures for ID-like cookies
        conn = sqlite3.connect(self.resultsDB.file_name)
        c = conn.cursor()
        c.execute("SELECT num_cookies FROM cookie_collections WHERE domain = :domain AND type = 'initial'", {"domain": self.domain,})
        num_intial = c.fetchall()
        if num_intial:
            _initial_domains, _initial_first_party_cookies, _initial_third_party_cookies, initial_id_like_cookies = self.check_cookies('initial')
        else:
            initial_id_like_cookies = 0
        logging.debug(f"initial_id_like_cookies {initial_id_like_cookies}")
        
        c.execute("SELECT num_cookies FROM cookie_collections WHERE domain = :domain AND type = 'opt-in option'", {"domain": self.domain,})
        num_opt_in = c.fetchall()
        if num_opt_in:
            _opt_in_domains, _opt_in_first_party_cookies, _opt_in_third_party_cookies, opt_in_id_like_cookies = self.check_cookies('opt-in option')
        else:
            opt_in_id_like_cookies = 0
        logging.debug(f"opt_in_id_like_cookies {opt_in_id_like_cookies}")
        
        c.execute("SELECT num_cookies FROM cookie_collections WHERE domain = :domain AND type = 'opt-out option'", {"domain": self.domain,})
        num_opt_out = c.fetchall()
        if num_opt_out:
            _opt_out_domains, _opt_out_first_party_cookies, _opt_out_third_party_cookies, opt_out_id_like_cookies = self.check_cookies('opt-out option')
        else:
            opt_out_id_like_cookies = 0
        logging.debug(f"opt_out_id_like_cookies {opt_out_id_like_cookies}")
        
        c.execute("SELECT num_cookies FROM cookie_collections WHERE domain = :domain AND type = 'close option'", {"domain": self.domain,})
        num_close_button = c.fetchall()
        if num_close_button:
            _close_domains, _close_first_party_cookies, _close_third_party_cookies, close_id_like_cookies = self.check_cookies('close option')
        else:
            close_id_like_cookies = 0
        logging.debug(f"close_id_like_cookies {close_id_like_cookies}")
        conn.close()  
        
        # DP 1: Only Opt-in option is present.
        # CRITERIA - Satisfies all of the following:
        # 1. There is a opt-in button present.
        # 2. There is not a more options button present.
        # 3. There is not a opt-out button present.
        if "opt-in option" in clickables_types and "more options" not in clickables_types and "opt-out option" not in clickables_types:
            dark_patterns["DP1"] = True
        
        # DP 2: Background color of Opt-in button makes it highlighted compared to Opt-out button.
        # CRITERIA: Satisfies all of the following:
        # 1. There is an opt-in option present.
        # 2. There is an opt-out option present or a more options button present.
        # 3. The opt-in button greyscale color is dark.
        # 4. The opt-out button greyscale color is light and the more options button greyscale color is light.
        if "opt-in option" in clickables_types and ("opt-out option" in clickables_types or "more options" in clickables_types):
            opt_in_num = [c for c in clickables if clickables[c] == "opt-in option"][0]
            if "opt-out option" in clickables_types:
                opt_out_num = [c for c in clickables if clickables[c] == "opt-out option"][0]
            else:
                opt_out_num = [c for c in clickables if clickables[c] == "more options"][0]
            opt_in_file_name = self.data_folder_name + "/screenshots/clickables/"+str(opt_in_num)+".png"
            opt_out_file_name = self.data_folder_name + "/screenshots/clickables/"+str(opt_out_num)+".png"
            opt_in_colour = self.check_image_greyscale(opt_in_file_name)
            opt_out_colour = self.check_image_greyscale(opt_out_file_name)
            if opt_in_colour == "dark" and opt_out_colour == "light":
                dark_patterns["DP2"] = True
         
        # DP 3: Size of dialog takes up more than 60% of the webpage.
        # CRITERIA - The area (length*width) of the dialog is greater than 60% of the area of the webpage.
        max_area = 1920 * 1080
        dialog_num = self.resultsDB.dialogs.select_dialognum_selector_where_domain_checked(self.domain, "True")[0][0]
        dialog_file_name = self.data_folder_name + "/screenshots/dialogs/"+str(dialog_num)+".png" 
        image = cv2.imread(dialog_file_name)
        dialog_dims = image.shape
        dialog_area = dialog_dims[0] * dialog_dims[1]
        area_percentage = float(dialog_area / max_area)
        if area_percentage > 0.6:
            dark_patterns["DP3"] = True
            
        # DP 4: Large amount of text on cookie dialog
        # CRITERIA - the FK score of the dialog is less than 50.
        text = self.resultsDB.dialogs.select_text(self.domain, dialog_num)
        fk_score = textstat.flesch_reading_ease(text)
        if fk_score < 50:
            dark_patterns["DP4"] = True
        
        # DP 5: Multiple layers to a cookie dialog
        # CRITERIA - a more options button is present.
        if "more options" in clickables_types:
            dark_patterns["DP5"] = True
                    
        # DP 6: Ambiguous Close button present.
        # CRITERIA - a close option is present.
        if "close option" in clickables_types:
            dark_patterns["DP6"] = True
        
        # DP 7: Multiple distinct Cookie Dialogs present on a page.
        # Dialog score must be positive and dialog text must not be a substring of another dialog.
        # CRITERIA - there are more than 1 distinct candidate dialogs which means:
        # 1. The candidate dialogs being considered all have a score greater than 0.
        # 2. At least one candidate is the same as or a substring of another candidate.
        diags = self.resultsDB.dialogs.select_text_where_score(self.domain, 0.0)
        diags = {d[0]:d[1] for d in diags} 
        distinct_diags = self.find_distict(diags)
        num_distinct_diags = len(distinct_diags)
        if num_distinct_diags > 1:
            dark_patterns["DP7"] = True
        
        # DP 8: At least one Preference Slider is enabled by default.
        # CRITERIA - a preference slider is present and satifies the following:
        # 1. The preference slider is enabled (is_enabled function of this element returns True).
        # 2. The preference slider is selected (is_seleted function of this element returns True).
        if "preference slider enabled" in clickables_types:
            dark_patterns["DP8"] = True
        
        # DP 9: Clicking the close button leads to more ID-like cookies being set.
        if close_id_like_cookies > initial_id_like_cookies:
            logging.debug("DP9: Clicking Close button leads to more cookies being selected.")
            dark_patterns["DP9"] = True
            
        # DP 11: More cookies are set regardless of the Opt-out button being clicked.
        if opt_out_id_like_cookies > initial_id_like_cookies:
            logging.debug("DP11: More cookies are set regardless of Opt-out button being clicked.")
            dark_patterns["DP11"] = True 
            
        # Save each dark pattern to the database
        for dp in dark_patterns:
            self.resultsDB.dark_patterns.insert_into(self.domain, dp, "unconfirmed", str(dark_patterns[dp]))
        if not self.OPT_AUTO:
            self.manual_validation(dark_patterns, dark_patterns_desc)


    def check_cookies(self, collection_type):
        website_domain = self.domain
        conn = sqlite3.connect(self.resultsDB.file_name)
        c = conn.cursor()
        c.execute("SELECT c.domain FROM cookies c JOIN cookie_collections cc ON cc.collection_num = c.collection_num WHERE cc.domain = :domain AND cc.type = :collection_type",{"domain":website_domain,"collection_type":collection_type})
        cookie_domains = c.fetchall()
        if cookie_domains:
            cookie_domains = cookie_domains
        else:
            cookie_domains = []
            
        domains = []
        first_party_cookies = 0
        third_party_cookies = 0
        for (cookie_domain,) in cookie_domains:
            #print(cookie_domain)
            cookie_domain = self.parse_domains(cookie_domain)
            if cookie_domain == website_domain:
                first_party_cookies += 1
            else:
                third_party_cookies += 1
            domains.append(cookie_domain)
        logging.debug("domains: "+str(domains))
        logging.debug("num domains: "+str(len(domains)))
        logging.debug("first_party_cookies: "+str(first_party_cookies))
        logging.debug("third_party_cookies: "+str(third_party_cookies))
        
        
        c.execute("SELECT cc.timestamp FROM cookie_collections cc WHERE cc.domain = :domain AND cc.type = :collection_type",{"domain":website_domain,"collection_type":collection_type})
        collection_timestamp = c.fetchone()
        if collection_timestamp:
            collection_timestamp = collection_timestamp[0]
        else:
            collection_timestamp = ""
        id_like_cookies = 0
        c.execute("SELECT value, expires FROM cookies c JOIN cookie_collections cc ON cc.collection_num = c.collection_num WHERE cc.domain = :domain AND cc.type = :collection_type",{"domain":website_domain,"collection_type":collection_type})
        cookie_value_expiry_pairs = c.fetchall()
        if cookie_value_expiry_pairs:
            cookie_value_expiry_pairs = cookie_value_expiry_pairs
        else:
            cookie_value_expiry_pairs = []
        
        for (value,expiry) in cookie_value_expiry_pairs:
            if is_id_cookie(collection_timestamp, value, expiry):
                id_like_cookies += 1
        c.execute("UPDATE cookie_collections SET num_first_party = :num_first_party, num_third_party = :num_third_party, num_id_like = :num_id_like WHERE domain = :domain AND type = :collection_type", {"num_first_party":first_party_cookies,"num_third_party":third_party_cookies, "num_id_like":id_like_cookies, "domain":self.domain, "collection_type":collection_type})
        conn.commit()
        conn.close() 
        return domains, first_party_cookies, third_party_cookies, id_like_cookies


    def parse_domains(self, raw_domain_value):
        result = tldextract.extract(raw_domain_value)
        return result.domain + "." + result.suffix

                
    def manual_validation(self, input_values, dark_patterns_desc):
        """ Function to prompt the user to manually validate the detected Dark Patterns.

        Args:
            input_values (dict[String->Boolean]): [description]
        """
        # Prompt the user to validate the auto DPs
        app = Checkbox_Input(input_values=input_values, input_descriptions=dark_patterns_desc, description="Check all the Auto Dark Patterns and then click confirm.", window_name="ADP")
        app.mainloop()
        # Update the value of each dark pattern to be the manually inputted value
        for dp in app.result:
            self.resultsDB.dark_patterns.update_value(self.domain, dp, str(app.result[dp].get()))
        
    
    def check_image(self, file_name):
        """ Function to determine wether an image is light or dark based on the average color of the image.

        Args:
            file_name (String): the file location of the image.

        Returns:
            String: 'light' or 'dark' specifiying the if the image is light or dark.
        """
        image = cv2.imread(file_name)
        blur = cv2.blur(image, (30, 30))  # With kernel size depending upon image size
        #cv2.imshow("yeet", blur) 
        #time.sleep(2)
        # Calculate average RGB values over all pixels
        mean = cv2.mean(blur)
        # Calculate average values of average RGB
        average = (mean[0] + mean[1] + mean[2])/3
        if average > 170:  # The range for a pixel's value in grayscale is (0-255), 127 lies midway
            return 'light' # (127 - 255) denotes light image
        else:
            return 'dark' # (0 - 127) denotes dark image        
        
        
    def check_image_greyscale(self, file_name):
        """ Function to determine wether an image is light or dark based on the average color of the greyscale image.

        Args:
            file_name (String): the file location of the image.

        Returns:
            String: 'light' or 'dark' specifiying the if the image is light or dark.
        """
        image = cv2.imread(file_name)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.blur(image, (30, 30))  # With kernel size depending upon image size
        # Calculate average RGB values over all pixels
        mean = cv2.mean(blur)
        if mean[0] > 170:
            return 'light' # (170 - 255) denotes light image
        else:
            return 'dark' # (0 - 127) denotes dark image
        
        
    def find_distict(self, dictionary):
        """ Function to determine to return only distinct values in a dictionary, that is values which are not the same or a substring of any other value in the dictionary. 
        Empty string or None values are not returned.

        Args:
            dictionary (dict[int -> String]): the input dictionary mapping a key to a value.

        Returns:
            dict[int -> String]: a dictionary with only the distinct values kept.
        """
        # Remove any entries with an empty string or None value.
        dictionary = {i:dictionary[i] for i in dictionary if dictionary[i] != None and dictionary[i].strip() != ""}
        # Determine the set values
        array = set(dictionary.values())
        # Create a temp dict to store the results
        final_array = {a:dictionary[a] for a in dictionary}
        # For each item in the dicionary
        for item in dictionary:
            # Get the value of item in the dict
            value = dictionary[item]
            # Get all the values that are not the item
            not_item = array.difference({value})
            # For each item that is not the value
            for n in not_item:
                # If the item is contained within (substring of) another item then
                if value in n:
                    # Remove the item fron the results
                    if item in final_array:
                        final_array.pop(item)
        # Remove duplicates
        temp = {val : key for key, val in final_array.items()}
        res = {val : key for key, val in temp.items()}
        return res