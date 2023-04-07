# Import the required Interfaces from the User Input Interface module.
from dark_cookies.uii import Checkbox_Input
import logging


class Manual_Dark_Patterns():
    def __init__(self, conf):
        # The WebDriver instance
        self.driver = conf.driver
        # The domain of the website
        self.domain = conf.domain
        # Class attributes for the required configuartion options
        self.OPT_SAVE_COOKIES = conf.options.OPT_SAVE_COOKIES
        self.OPT_CR = conf.options.OPT_CR
        self.resultsDB = conf.resultsDB
        
        
    def find_dps(self):
        """ Function to allow the user to input any other DPs them and add them to the database.
        """
        logging.debug("Manually Adding DPs for '"+str(self.domain)+"'...")
        
        # Dark pattern descriptions
        dark_patterns_desc = {
                         "DP10" : "Takes more clicks to Opt-out than Opt-in or Opt-out option is not clearly visible.",
                         "DP12" : "Poorly Labelled preference sliders to the extent that their purpose is ambiguous.",
                         "DP13" : "In the context of the Cookie Dialog text the standard meaning of the Opt-in and Opt-out buttons is inverted.",
                         "DP14" : "Opt-out button is named in such a way to guilt them for selecting it.",
                         "DP15" : "When user clicks Opt-out button they are asked to confirm their choice."}
        
        # Define the intial values of the dark patterns (will all be False)
        dark_patterns = {d:False for d in dark_patterns_desc}
        
        clickables = self.resultsDB.clickables.select_clickableNum_type(self.domain)
        clickables = {c[0]:c[1] for c in clickables}
        clickables_types = set(clickables.values())
        
        # DP10: Takes more clicks to Opt-out than Opt-in or Opt-out option is not clearly visible.
        if self.OPT_CR:
            num_clicks = self.resultsDB.dark_patterns.select_numClicks(self.domain)
            if ("more options" not in clickables_types and "opt-out option" not in clickables_types) or ("opt-in option" in clickables_types and num_clicks > 1 ):
                dark_patterns["DP10"] = True
        
        # Save each dark pattern to the database
        for dp in dark_patterns:
           self.resultsDB.dark_patterns.insert_into(self.domain, dp, "unconfirmed", "unconfirmed")
        
        # Prompt the user to validate the auto DPs
        app = Checkbox_Input(input_values=dark_patterns, input_descriptions=dark_patterns_desc, description="Check all the Manual Dark Patterns and then click confirm.", window_name="MDP")
        app.mainloop()
        # Update the value of each dark pattern to be the manually inputted value
        for dp in app.result:
            self.resultsDB.dark_patterns.update_value(self.domain, dp, str(app.result[dp].get()))