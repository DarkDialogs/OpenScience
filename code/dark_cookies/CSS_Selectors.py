import requests
import sqlite3
import logging

### SCRAPING FUNCTIONS

# Function to update (delete old and insert new) 'EasyList' selectors to the HPDatabase
def update_easyList(hpdb_name):
    logging.info("Updating css selectors from https://easylist.to...")
    conn = sqlite3.connect(hpdb_name)
    c = conn.cursor()

    # Delete Old Easy List Entries from database
    c.execute("DELETE FROM specific_element_hiding_rules WHERE source = 'EasyList';")
    c.execute("DELETE FROM general_element_hiding_rules WHERE source = 'EasyList';")
    conn.commit()

    x = requests.get('https://secure.fanboy.co.nz/fanboy-cookiemonster.txt')
    content = x.text.split('\n')
    line  = 0


    # Skip the intial content to get to the starting line of the General element hiding rules
    while(content[line]!="!------------------------General element hiding rules-------------------------!"):
        line = line+1
    # Skip the first line as this is just the tag 
    line = line+1


    # General element hiding rules
    # Iterate through all of the General element hiding rules until we reach the next comment
    num_gen_elements = 0
    selectors = []
    while(content[line]!="!-------------------------Third-party blocking rules--------------------------!"):
        if content[line][0] != '!':
            new_line = content[line][2:]
            #selectors = selectors + new_line + ","
            selectors.append(new_line)
            num_gen_elements = num_gen_elements + 1
        line = line +1
    #selectors = selectors[:-1]
    for selector in selectors:
        try:
            c.execute("INSERT INTO general_element_hiding_rules VALUES(?, ?, datetime('now')) ",(selector, "EasyList")) 
        except Exception as e:
            pass
            logging.debug("Duplicate Entry for '" + selector + "'" )
    logging.info("Added " + str(num_gen_elements)+ " General element hiding rules." )


    # Skip the uneeded content to get to the starting line of the Specific element hiding rules
    while(content[line]!="!------------------------Specific element hiding rules------------------------!"):
        line = line +1
    # Iterate through all of the General element hiding rules until we reach the next comment
    line = line +1


    # Specific element hiding rules
    num_spec_elements = 0
    while(content[line]!="!---------------------------------Whitelists----------------------------------!"):
        # Need to check format of each entries as there are some extra comment lines
        # Currently using basic check on first character to check
        new_line = content[line].split("##")
        if (len(new_line) == 2):
            urls = new_line[0].split(",")
            selector = new_line[1]
            for url in urls:
                try:
                    c.execute("INSERT INTO specific_element_hiding_rules VALUES(?, ?, ?, datetime('now')) ",(url, selector, "EasyList")) 
                    num_spec_elements = num_spec_elements + 1   
                except Exception as e:
                    logging.debug("Duplicate Entry for '" + selector + "'" )
        line = line +1
    logging.info("Added " + str(num_spec_elements)+" Specific element hiding rules." )
    conn.commit()

    conn.close()


# Function to update (delete old and insert new) 'I dont Care about Cookies' selectors to the HPDatabase
def update_i_dont_care_about_cookies(hpdb_name):
    logging.info("Updating css selectors from https://www.i-dont-care-about-cookies.eu...")
    conn = sqlite3.connect(hpdb_name)
    c = conn.cursor()

    # Delete Old Easy List Entries from database
    c.execute("DELETE FROM specific_element_hiding_rules WHERE source = 'I Dont Care about Cookies';")
    c.execute("DELETE FROM general_element_hiding_rules WHERE source = 'I Dont Care about Cookies';")
    conn.commit()

    x = requests.get('https://www.i-dont-care-about-cookies.eu/abp/')
    content = x.text.split('\n')
    line  = 0


    # Skip the intial content to get to the starting line of the General element hiding rules
    while(content[line]!="! GLOBAL RULES"):
        line = line+1
    # Skip the first line as this is just the tag 
    line = line+2   


    # General element hiding rules
    # Iterate through all of the General element hiding rules until we reach the next comment
    num_gen_elements = 0
    while(content[line]!="! CUSTOM RULES"):
        if content[line][0] != '!' and content[line][0] !='~':
            selector = content[line][2:]
            #selectors = selectors + new_line + ","
            try:
                c.execute("INSERT INTO general_element_hiding_rules VALUES(?, ?, datetime('now')) ",(selector, "I Dont Care about Cookies")) 
                num_gen_elements = num_gen_elements + 1
            except Exception as e:
                logging.debug("Duplicate Entry for '" + selector + "'" )
        line = line +1
    #selectors = selectors[:-1]

    
    logging.info("Added " + str(num_gen_elements)+ " General element hiding rules." )
    
    # Specific element hiding rules
    num_spec_elements = 0
    while(content[line]!="! SCRIPT BLOCKING"):
        # Need to check format of each entries as there are some extra comment lines
        # Currently using basic check on first character to check
        new_line = content[line].split("##")
        if (len(new_line) >= 2):
            urls = new_line[0].split(",")
            selectors = new_line[1].split(",")
            for url in urls:
                for selector in selectors:
                    try:
                        c.execute("INSERT INTO specific_element_hiding_rules VALUES(?, ?, ?, datetime('now')) ",(url, selector, "I Dont Care about Cookies")) 
                        num_spec_elements = num_spec_elements + 1   
                    except Exception as e:
                        logging.debug("Duplicate Entry for '" + selector + "'" )
        line = line +1
    logging.info("Added " + str(num_spec_elements)+" Specific element hiding rules." )
    conn.commit()

    conn.close()
