# Dark Cookies: Python library for the analysis of cookie dialogs.
Cookie dialogs (aka Cookie Consent Banners or Cookie Privacy Warnings) allow users to select the level of cookie enablement that matches their personal privacy preferences.  Ideally, cookie dialogs should provide a range of options for users to choose from and there should be no bias towards accepting more cookies. However, many cookie dialogs employ subtle design techniques to nudge users towards accepting more cookies than is necessary. These techniques are known as dark patterns. We have designed and implemented an automated system that can locate cookie dialogs and then analyse them for dark patterns. The system is capable of detecting 10 different dark patterns automatically. 

This system was created as part of a Computer Science undergraduate thesis at the University of Edinburgh and as part of an internship at [TULiPS](https://groups.inf.ed.ac.uk/tulips/) lab. We will be publishing a paper on our findings at the [Euro S&P 2023](https://www.ieee-security.org/TC/EuroSP2023/) conference.
The datasets that we collected using this tool have also been released on [datashare](https://datashare.ed.ac.uk/handle/10283/4453).

# Sections
- [Feature Overview](#feature-overview)
- [Installation](#installation)
- [Usage](#usage)
- [Acknowledgements](#acknowledgements)
# Feature Overview
The main features of the system are:
- **Customisable Webscraping Framework:** the system abstracts the webscraping process to allow easy collection of data.
  - A range of [options](#options) are provided to toggle the data collected.  This allows basic use-cases such as just collecting screenshots of cookie dialogs or more complex use-cases such as detecting dark patterns on cookie dialogs.
  - The system automatically updates itself with the latest set of CSS selectors which are used to detect cookie dialogs.
  - Identify the category of the website (based on categories tagged by [curlie.org](https://curlie.org/docs/en/license.html) ) using the [homepage2vec](https://github.com/epfl-dlab/Homepage2vec) classifer.
- **Cookie Dialog Collection:** the system can automatically collect cookie dialogs from webpages.
  - Uses ranking-based approach to locate cookie dialogs with an accuracy of 98.8%.
  - Determine if cookie dialogs come from a popular Content Management Providers (CMPs).
- **Clickable Location:** the system can detect and classify the type of clickables (the interactable elements) on cookie dialogs.
- **Cookie Behavior Analysis:** the system can interact with clickables and measure the change in cookies after the interaction.
- **Dark Pattern Detection:** the system can detect 10 common dark patterns automatically.
- **User Interface:** a user interface is provided that allows a researcher to manually validate the output of the system. This allows a researcher to validate that the cookie dialog has been located correctly, all clickables have been located and that all dark patterns have been detected.
# Installation
## Prerequisites
The system requires the following software to be installed:
1. Python 3 (any version should work, we used version 3.9.1).
2. Google Chrome (any version should work).
3. We have tested the system on Ubuntu 20.04 and Windows 10/11, so we recommend using one of these operating systems.

## Installation instructions
Run the following commands inside the directory that contains `requirements.txt`:
1. **(Recomended) Create a Python Virtual Environment.**

    Note: You will need to activate this again when you close the terminal.

    Windows
    ```terminal
        python3 -m venv dc_venv
        dc_venv/Scripts/activate 
    ```


    Linux
    ```terminal
        python3 -m venv dc_venv
        source dc_venv/bin/activate 
    ```
2. **Linux only: install the tkinter package required for the user interface.**
    ```terminal
    sudo apt-get install python3-tk
    ```
3. **Install the required pip packages.**
    ```terminal
    pip install -r requirements.txt
    ```
4. **Download the version of chromedriver that matches your system and Chrome version from [here](https://chromedriver.chromium.org/downloads). Place this file in the directory you are running the system from and make sure it is called 'chromedriver' (Linux) or 'chromedriver.exe' (Windows).**
# Usage
The `dc.py` file provides a Command Line Interface (CLI) to run some basic commands on the system.

Results from the system are stored in a `sqlite` database in the following location `data/Results.db`. We recommend using the [DB Browser](https://sqlitebrowser.org/) tool or the Python [sqlite3](https://docs.python.org/3/library/sqlite3.html) library to access the results. 

### Run Tool on a single website
```terminal
python3 dc.py <website_name>
```

### Run Tool on a list of websites from a file.
Note: File must contain a domain on each line
```terminal
python3 dc.py from <file-name>
```

### Activate the virtual environment.
```terminal
hp_venv/scripts/activate
```


## Options
The configuration options can be found in `dark_cookies/CDA_Options.py`.

`True` = enabled, `False` = disabled.
- **OPT_AUTO:** Enable option to make the program fully automated (default: True). When True this disables the user interface which allows the researcher to manually validate the data.
- **OPT_CL:** Enable the collection of clickable elements if a cookie dialog is found (default: True).
- **OPT_ADP:** Enable the automatic detection of dark patterns if a cookie dialog is found (default: True).
- **OPT_CR:** Enable the option which prompts the researcher to manually opt-out/reject cookies and record the number of clicks this takes (default: True).
- **OPT_MDP:** Enable the user interface which allows the researcher to input any further dark patterns they observed on the dialog. (default: True).
- **OPT_SAVE_COOKIES:** Enable the option to collect cookies from the website and save them to the database (default: True).
- **OPT_WEBSITE_CATEGORY:** Enable option to use homepage2_vec classifer to detect the category of website (default: True).
- **OPT_DETECT_CMPS:** Enable to detect if collected cookie dialogs are from a Content Management Provider (default: True).
- **AUTO_UPDATE_CSS_SELECTORS:** Enable option to have CSS selectors updated automatically on a daily basis from the online CSS selector lists (default: True).
- **CSS_SELECTOR_LISTS:** The enabled CSS selector lists (default: 'easylist' and 'i dont care about cookies').
- **DATA_FOLDER_NAME:** The name of the folder where all the data will be stored (default: 'data').

## Example Code
Example: automatically locate a cookie dialog and dark patterns on 'microsoft.com'.
```py
from dark_cookies import CDA
from dark_cookies.CDA_Options import Options
options = Options()
CDA("microsoft.com", options=options)
```
# Acknowledgements
## Python libraries used by the system
- [Selenium](https://pypi.org/project/selenium/4.3.0/)
  - Used to provide the majority of the webscraping.
- [Tkinter](https://docs.python.org/3/library/tkinter.html)
  - Used to create the user interface.
- [textstat](https://pypi.org/project/textstat/0.7.2/)
  - Used to calculate fk scores.
- [zxcvbn](https://pypi.org/project/zxcvbn/4.4.28/)
  - Used to check the strength of cookie value fields as an identifier.
- [homepage2vec](https://pypi.org/project/homepage2vec/0.0.3rc0/)
  - Used to classify the type of website in website_categories.py
- [Pillow](https://pypi.org/project/Pillow/8.2.0/)
  - Used to render images on the user interface and to check the dimensions of screenshots of cookie dialogs.
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/4.10.0/)
  - Used for deep CSS selector search when collecting cookie dialogs.
  - Reading clickable text, parsing the HTML of close and preference sliders clickables.
- [python-dateutil](https://pypi.org/project/python-dateutil/2.8.2)
  - Used to parse cookie dates in id_like_checker.
- [opencv-python](https://pypi.org/project/opencv-python/4.5.4.58/)
  - Used to detect the colour of clickable elements.
- [tldextract](https://pypi.org/project/tldextract/3.3.0/)
  - Used to extract the top level domain from cookie strings.
- [pynput](https://pypi.org/project/pynput/1.7.4/)
  - Used to record the number of mouse clicks that it takes to reject cookies.
- [googletrans](https://pypi.org/project/googletrans/4.0.0rc1/)
  - Used to translate text in nlp.
- [Requests](https://pypi.org/project/requests/2.25.1/)
  - Used to update CSS selectors.
- [nltk](https://pypi.org/project/nltk/3.6.7/)
  - Used to create ngrams and stem text.
- [stemming](https://pypi.org/project/stemming/1.0/)
  - Used to stem text.
