class Options():
    def __init__(self, OPT_CL = True, OPT_ADP = True, OPT_CR = True, OPT_MDP = True, OPT_SAVE_COOKIES = True, OPT_AUTO = False, OPT_WEBSITE_CATEGORY= True, OPT_DETECT_CMPS= True, AUTO_UPDATE_CSS_SELECTORS=True, CSS_SELECTOR_LISTS = ['easylist','i dont care about cookies'], DATA_FOLDER_NAME = 'data') -> None:
        ### Configuration options for Cookie Dialog Analyser
        # Change the default values of each option above.
        # True = enabled, False = disabled
        # Enable the collection of clickable elements if a cookie dialog is found.
        self.OPT_AUTO = OPT_AUTO
        #Enable the collection of clickable elements if a cookie dialog is found.
        self.OPT_CL = OPT_CL
        # Enable the automatic detection of dark patterns if a cookie dialog is found.
        self.OPT_ADP = OPT_ADP
        # Enable the option which prompts the researcher to manually opt-out/reject cookies and record the number of clicks this takes.
        self.OPT_CR = OPT_CR
        # Enable the user interface which allows the researcher to input any further dark patterns they observed on the dialog.
        self.OPT_MDP = OPT_MDP
        # Enable the option to collect cookies from the website and save them to the database.
        self.OPT_SAVE_COOKIES = OPT_SAVE_COOKIES
        # Enable option to use homepage2_vec classifer to detect the category of website.
        self.OPT_WEBSITE_CATEGORY = OPT_WEBSITE_CATEGORY
        # Enable to detect if collected cookie dialogs are from a Content Management Provider.
        self.OPT_DETECT_CMPS = OPT_DETECT_CMPS
        # Enable option to have CSS selectors updated automatically on a daily basis from the online CSS selector lists.
        self.AUTO_UPDATE_CSS_SELECTORS = AUTO_UPDATE_CSS_SELECTORS
        # The enabled CSS selector lists.
        self.CSS_SELECTOR_LISTS = CSS_SELECTOR_LISTS
        # The folder where all the data collected will be stored.
        self.DATA_FOLDER_NAME = DATA_FOLDER_NAME

# Note: the classes below are commonly used pre-configured options.   
# Manual Dialog Collection Only
class Options_Dialog(Options):
    def __init__(self):
        Options.__init__(self, OPT_CL = False, OPT_ADP = False, OPT_CR = False, OPT_MDP = False, OPT_SAVE_COOKIES = False, OPT_AUTO = False)

# Auto Dialog Collection Only
class Options_Auto_Dialog(Options):
    def __init__(self):
        Options.__init__(self, OPT_CL = False, OPT_ADP = False, OPT_CR = False, OPT_MDP = False, OPT_SAVE_COOKIES = False, OPT_AUTO = True)
        
# Manual Dialogs and Clickables only
class Options_Dialog_Clickables(Options):
    def __init__(self):
        Options.__init__(self, OPT_CL = True, OPT_ADP = False, OPT_CR = False, OPT_MDP = False, OPT_SAVE_COOKIES = False, OPT_AUTO = False)
        
# Auto Dialogs and Clickables only
class Options_Auto_Dialog_Clickables(Options):
    def __init__(self):
        Options.__init__(self, OPT_CL = True, OPT_ADP = False, OPT_CR = False, OPT_MDP = False, OPT_SAVE_COOKIES = False, OPT_AUTO = True)

# Manual Dialogs, Clickales and Dark Pattern analysis
class Options_All(Options):
    def __init__(self):
        Options.__init__(self, OPT_CL = True, OPT_ADP = True, OPT_CR = True, OPT_MDP = True, OPT_SAVE_COOKIES = True, OPT_AUTO = False)

# Auto Dialogs, Clickales and Dark Pattern analysis
class Options_Auto_All(Options):
    def __init__(self):
        Options.__init__(self, OPT_CL = True, OPT_ADP = True, OPT_CR = False, OPT_MDP = False, OPT_SAVE_COOKIES = True, OPT_AUTO = True)