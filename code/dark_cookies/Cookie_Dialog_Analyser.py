from os.path import exists, dirname, join
from os import makedirs, listdir, remove, getcwd
from datetime import date
from selenium import webdriver
import logging
import sqlite3
import time
from dark_cookies.Config_File_Interface import Config_File
from dark_cookies.CSS_Selectors import update_i_dont_care_about_cookies, update_easyList
from dark_cookies.CDA_Options import Options
from dark_cookies.cdc import Cookie_Dialog_Collector
from dark_cookies.cl import Clickable_Locator
from dark_cookies.adp import Automatic_Dark_Patterns
from dark_cookies.cr import Cookie_Rejector
from dark_cookies.mdp import Manual_Dark_Patterns
from dark_cookies.cc import Cookie_Capture
from dark_cookies.dbi import ResultsDB, HPDB
from dark_cookies.sfl import save_cookies
from dark_cookies.website_categories import detect_homepage2vec_category


class CDA():
    def __init__(self, domain, options=Options()) -> None:
        self.domain = domain
        self.driver = None
        self.options = options
        self.check_dependencies()
        self.clear_screenshots()
        self.create_webdriver()
        self.resultsDB = ResultsDB(self.options.DATA_FOLDER_NAME+"/ResultsDB.db")
        self.hpdb = HPDB(self.options.DATA_FOLDER_NAME+"/HPDB.db")
        if self.driver == None:
            logging.debug("Failed to start webdriver.")
        else:
            logging.debug("CDA Ready to go!")
            self.analyse_website()
    
    def analyse_website(self):
        try:
            logging.debug("<STAGE 0: Website Setup>")
            self.resultsDB.websites.insert_into(self.domain,'website saved', "disabled")
            if self.driver == None:
                # Display an error message.
                logging.error("Failed to connect to the website.")
                # Update the website status.
                self.resultsDB.websites.update_status(self.domain, 'failed to connect')
            # If the website was connected to successfully then
            else:
                self.detect_website_category()
                dialog_found = self.collect_cookie_dialog()
                # If a cookie dialog was found then
                if dialog_found:
                    self.locate_clickables()
                    self.analyse_cookie_setting_behavior()
                    self.detect_dark_patterns()
                    self.resultsDB.websites.update_status(self.domain, 'completed')
                # Else no cookie dialog was found
                else:
                    # Update the website status.
                    self.resultsDB.websites.update_status(self.domain, 'no dialog found')
                    # Display a message.
                    logging.info("No cookie dialog was found.")
        # If an exception occurs print the error and set the website status to error.
        except Exception as e:
            print(e)
            self.resultsDB.websites.update_status(self.domain, 'error')
        # Finally close the webdriver.
        finally:
            if self.driver != None:
                self.close_webdriver()
            
    def detect_website_category(self):
        if self.options.OPT_WEBSITE_CATEGORY:
            category = detect_homepage2vec_category(self.domain)
            if category:
                self.resultsDB.websites.update_category(self.domain, str(category))
            
            
    def collect_cookie_dialog(self):
        logging.debug("<STAGE 1: Cookie Dialog Collector>")
        ### STAGE 1: Cookie Dialog Collector
        # Find the valid dialog on the webpage if one is present.
        cdc = Cookie_Dialog_Collector(self)
        dialog_num = cdc.find_dialog()

        # If a cookie dialog was found then
        if dialog_num != -1:
            ### STAGE 2: Clickable Locator
            # Update the website status
            self.resultsDB.websites.update_status(self.domain, 'dialog collected')
            return True
        return False
    
    
    def locate_clickables(self):
        if self.options.OPT_CL:
            logging.debug("<STAGE 2: Clickable Locator>")
            cl = Clickable_Locator(self)
            # Tag all the clickables with their types on the valid dialog.
            cl.find_clickables()
            # Update the website status
            self.resultsDB.websites.update_status(self.domain, 'clickables located')
    
    
    def analyse_cookie_setting_behavior(self):
        if self.options.OPT_SAVE_COOKIES:
            logging.debug("<STAGE 3: Cookie Behavior Analyser>")
            # Save the intial cookies present on the website.
            save_cookies(self.driver, self.domain, self.resultsDB, 'initial')
            if self.options.OPT_CR and not self.options.OPT_AUTO:
                # Count the number of clicks it takes to reject cookies.
                cookie_rejector = Cookie_Rejector(self)
                cookie_rejector.reject_cookies()
                # Update the website status
                self.resultsDB.websites.update_status(self.domain, 'cookies rejected')
            # Close the webdriver
            self.close_webdriver()
            # Complete the addtional cookie captures.
            cc = Cookie_Capture(self)
            cc.additional_captures()  


    def detect_dark_patterns(self):
        if self.options.OPT_ADP:
            logging.debug("<STAGE 4: Dark Pattern Detector>")
            adp = Automatic_Dark_Patterns(self)
            # Find all the Auto Dark Patterns
            adp.find_dps()
            # Update the website status
            self.resultsDB.websites.update_status(self.domain, 'adp complete')
        if self.options.OPT_MDP and not self.options.OPT_AUTO:
            mdp = Manual_Dark_Patterns(self)
            # Find all the Manual Dark Patterns
            mdp.find_dps()
            # Update the website status
            self.resultsDB.websites.update_status(self.domain, 'mdp complete')
    
    
    def create_webdriver(self, path = getcwd() + "/"):
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        try:
            self.driver = webdriver.Chrome(options=options, executable_path=path+"/chromedriver")
        except Exception as e:
            if "'chromedriver.exe' executable needs to be in PATH." in str(e):
                logging.error("chromedriver.exe could not be found - Please install the version of chromedriver that matches your version of Chrome from https://sites.google.com/chromium.org/driver/downloads and place the'chromedriver.exe' file in the same directory as you are running the script from.")
                self.driver = None
            elif "This version of ChromeDriver only supports Chrome version" in str(e):
                logging.error("'chromedriver.exe' was found but it does not support your current version of chrome. Please check your version of Chrome, download the corresponding version of chromedriver from https://sites.google.com/chromium.org/driver/downloads and place the'chromedriver.exe' file in the same directory as you are running the script from.")
                self.driver = None
            else:
                logging.error(e)
                self.driver = None
        if self.driver is not None:
            connected = False
            # Navigate to the url using the driver
            # ATTEMPT 1: try https://www.
            try:
                url = "https://www." + self.domain
                self.driver.get(url)
                connected = True
            except Exception as e:
                logging.info("Failed to connect to '" + url + "'.")
                connected = False
            # ATTEMPT 2: try http://www.
            if not(connected):
                try:
                    url = "http://www." + self.domain
                    self.driver.get(url)
                    connected = True
                except Exception as e:
                    logging.info("Failed to connect to '" + url + "'.")
                    connected = False
            # ATTEMPT 3: try https://
            if not(connected):
                try:
                    url = "https://" + self.domain
                    self.driver.get(url)
                    connected = True
                except Exception as e:
                    logging.info("Failed to connect to '" + url + "'.")
                    connected = False
            # ATTEMPT 4: try http://
            if not(connected):
                try:
                    url = "http://" + self.domain
                    self.driver.get(url)
                    connected = True
                except Exception as e:
                    logging.info("Failed to connect to '" + url + "'.")
                    connected = False
            if not(connected):
                self.driver.close()
                self.driver = None
            else:
                # Maximise the size of the driver window
                self.driver.maximize_window()
                # Make the program sleep for 2 seconds to allow the page to load.
                time.sleep(2)
                
    def close_webdriver(self):
        '''
        param driver: WebDriver
            an instance of a selenium webdriver used to interact with the webpage.
        '''
        logging.debug("Web driver closing...")
        if self.driver is not None:
            self.driver.quit()
            self.driver = None
        else:
            logging.warning("The webdriver has already been closed.")
            
    def check_dependencies(self):
        # Name of the data folder
        cda_folder_name = self.options.DATA_FOLDER_NAME
        
        # Create directory        
        if exists(cda_folder_name):
            pass
        else:
            makedirs(cda_folder_name)
            
        # Create screenshots directories
        screenshots_folder = cda_folder_name + "/screenshots"
        if exists(screenshots_folder):
            pass
        else:
            makedirs(screenshots_folder)
        # Create clickables directories
        clickables_folder = screenshots_folder + "/clickables"
        if exists(clickables_folder):
            pass
        else:
            makedirs(clickables_folder)
        # Create dialogs directories
        dialogs_folder = screenshots_folder + "/dialogs"
        if exists(dialogs_folder):
            pass
        else:
            makedirs(dialogs_folder)
            
        # Database setup
        hpdb_name = cda_folder_name + "/" + 'HPDB.db'
        sql_file_name = dirname(__file__)+'/HPDB.sql'
        if exists(sql_file_name):
            with open(sql_file_name, 'r') as sql_file:
                sql_script = sql_file.read()
            db = sqlite3.connect(hpdb_name)
            cursor = db.cursor()
            cursor.executescript(sql_script)
            db.commit()
            db.close()
            logging.debug("Successfully connected to internal database located at "+str(hpdb_name)+".")
        else: 
            logging.error("Failed Dependency: Internal database - Failed to locate the SQL file for the internal database (HPDB.db)")
        
        # Add HPDB data values
        sql_file_name = dirname(__file__)+'/data.sql'
        if exists(sql_file_name):
            with open(sql_file_name, 'r') as sql_file:
                sql_script = sql_file.read()
            try:
                db = sqlite3.connect(hpdb_name)
                cursor = db.cursor()
                cursor.executescript(sql_script)
                db.commit()
                db.close()
                logging.debug("Successfully connected to internal database located at "+str(hpdb_name)+".")
            except Exception as e:
                pass
        else: 
            logging.error("Failed Dependency: Internal database - Failed to locate the SQL file for the data (HPDB.db)")
        
        # data file setup
        data_file_name = cda_folder_name + "/" + '.cda_data.txt'
        resultsdb_name = cda_folder_name + "/" + 'ResultsDB.db'
        sql_file_name = dirname(__file__)+'/ResultsDB.sql'
        if exists(sql_file_name):
            with open(sql_file_name, 'r') as sql_file:
                sql_script = sql_file.read()
            db = sqlite3.connect(resultsdb_name)
            cursor = db.cursor()
            cursor.executescript(sql_script)
            db.commit()
            db.close()
            logging.info("Successfully connected to results database located at "+str(resultsdb_name)+".")
        else: 
            logging.error("Failed Dependency: Results database - Failed to locate the SQL file for the results database (ResultsDB.db)")
        
        # Update the CSS Selectors
        if self.options.AUTO_UPDATE_CSS_SELECTORS:
            cf = Config_File(data_file_name) 
            if exists(data_file_name):
                last_updated_date= cf.get_value("last_updated")
            else:
                last_updated_date = str(date.today())
                cf.add_value("last_updated", last_updated_date)
            
            if last_updated_date is not None:
                try:
                    last_updated_datetime = date.fromisoformat(last_updated_date)
                except Exception as e:
                    last_updated_date = None
                
            if last_updated_date is None or date.today() > last_updated_datetime:
                logging.info("Updating CSS selectors...")
                cf.add_value("last_updated", str(date.today()))
                if 'easylist' in self.options.CSS_SELECTOR_LISTS:
                    update_easyList(hpdb_name)
                if 'i dont care about cookies' in self.options.CSS_SELECTOR_LISTS:
                    update_i_dont_care_about_cookies(hpdb_name)
            else:
                logging.info("CSS Selectors are all up to date.")
                
    # Function to clear all screenshots from the screenshots folder.
    def clear_screenshots(self):
        # Delete all files in the dialogs folder.
        mydir = self.options.DATA_FOLDER_NAME+ "/screenshots/dialogs"
        filelist = [ f for f in listdir(mydir) ]
        for f in filelist:
            remove(join(mydir, f))
            
        # Delete all files in the clickables folder.
        mydir = self.options.DATA_FOLDER_NAME+"/screenshots/clickables"
        filelist = [ f for f in listdir(mydir) ]
        for f in filelist:
            remove(join(mydir, f))
        
        
    def next_stage(self):
        if self.stage == "1":
            print("Stage 2")
            self.stage = "2"
            return True
        elif self.stage == "2":
            print("Stage 3")
            self.stage = "3"
            return True
        else:
            print("No more stages.")
            return False