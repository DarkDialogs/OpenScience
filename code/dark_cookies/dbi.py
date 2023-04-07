import sqlite3

### SKELETON TABLE
class Database_table:
    def __init__(self, _file_name, _name, _fields = "Check SQLite File", _key_fields = "Check SQLite File"):
        self.file_name = _file_name
        self.name = _name
        self.fields = _fields
        self.key_fields = _key_fields
    
    def insert_into(self, values = None):
        #code to insert new entry into table
        pass

    def select_all(self, key):
        #code to select all values from a record using key as a key.
        pass

    def delete_where(self, key):
        pass

    def detete_all(self):
        #code to delete all entries from the table
        pass


### HPDB
class HPDB:
    def __init__(self, _file_name=".cda/HPDB.db"):
        self.file_name = _file_name
        self.general_element_hiding_rules = General_element_hiding_rules_table(_file_name=self.file_name)
        self.specific_element_hiding_rules = Specific_element_hiding_rules_table(_file_name=self.file_name)
        self.user_css_selectors = None
        self.dictionaries = Dictionaries_table(_file_name=self.file_name)
        self.tranco_websites = Tranco_websites_table(_file_name=self.file_name)
        self.cmp_fingerprints = Cmp_fingerprints(_file_name=self.file_name)


class Dictionaries_table(Database_table):
    def __init__(self, _file_name=None ,_name="dictionaries"):
        super().__init__(_file_name, _name)  
    
    def insert_into(self, name, words, source):
        #code to insert new entry into table
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("INSERT INTO dictionaries VALUES(?, ?, ?, datetime('now')) ",(name, words, source)) 
        conn.commit()
        conn.close()
    
    def select_words(self, name):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("SELECT words FROM dictionaries WHERE name = :name;",{'name' : name})
        results = c.fetchall()
        if results == None:
            return None
        conn.commit()
        conn.close()
        return results[0][0]
    

class General_element_hiding_rules_table(Database_table):
    def __init__(self, _file_name=None, _name="general_element_hiding_rules"):
        super().__init__(_file_name, _name)  

    # Function to query the HPDB and return a list of general element hiding rules
    def select_selector(self):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("SELECT selector FROM general_element_hiding_rules;")
        result = c.fetchall()
        conn.commit()
        conn.close()
        general_element_hiding_rules = []
        for row in result:
            general_element_hiding_rules.append(row[0])
        return general_element_hiding_rules

    def insert_into(self, selector, source):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("INSERT INTO general_element_hiding_rules VALUES(?, ?, datetime('now')) ",(selector, source)) 
        conn.commit()
        conn.close()      


class Specific_element_hiding_rules_table(Database_table):
    def __init__(self, _file_name=None ,_name="specific_element_hiding_rules"):
        super().__init__(_file_name, _name)  

    # Function to query the HPDatabase and return a list of specific element hiding rules for a domain
    # NOTE: url should be shortened to remove protocol and any file paths
    # Example: https://www.bbc.co.uk/news should be bbc.co.uk
    def select_selector(self, url):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("SELECT selector FROM specific_element_hiding_rules WHERE url = :url;",{'url' : url})
        result = c.fetchall()
        conn.commit()
        conn.close()
        specific_element_hiding_rules = []
        for row in result:
            specific_element_hiding_rules.append(row[0])
        return specific_element_hiding_rules
    
    def insert_into(self, domain, selector, source):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("INSERT INTO specific_element_hiding_rules VALUES(?, ?, ?, datetime('now')) ",(domain, selector, source)) 
        conn.commit()
        conn.close()              


class Tranco_websites_table(Database_table):
    def __init__(self, _file_name=None ,_name="tranco_websites"):
        super().__init__(_file_name, _name)  

    def select_domain_where_rank(self,start, finish):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("SELECT domain FROM tranco_websites WHERE rank >= :start AND rank <= :finish;",{'start' : start, 'finish': finish})
        results = c.fetchall()
        conn.commit()
        conn.close()
        domains = [domain[0] for domain in results]
        return domains
    
class Cmp_fingerprints(Database_table):
    def __init__(self, _file_name=None ,_name="cmp_fingerprints"):
        super().__init__(_file_name, _name)  

    def select_all(self):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("SELECT * FROM cmp_fingerprints;")
        results = c.fetchall()
        conn.commit()
        conn.close()
        return results

### ResultsDB
class ResultsDB:
    def __init__(self, _file_name=".cda/ResultsDB.db"):
        self.file_name = _file_name
        self.websites = Websites_table(_file_name=self.file_name)
        self.dialogs = Dialogs_table(_file_name=self.file_name)
        self.clickables = Clickables_table(_file_name=self.file_name)
        self.cookie_collections = Cookie_collections_table(_file_name=self.file_name)
        self.cookies = Cookies_table(_file_name=self.file_name)
        self.dark_patterns = Dark_patterns_table(_file_name=self.file_name)


class Websites_table(Database_table):
    def __init__(self, _file_name=None, _name="websites"):
        super().__init__(_file_name, _name)  

    def insert_into(self, domain, status, location, time=0.0):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("DELETE FROM websites WHERE domain = :domain ;",{'domain': domain})
        c.execute("DELETE FROM dialogs WHERE domain = :domain ;",{'domain': domain})
        c.execute("DELETE FROM clickables WHERE domain = :domain ;",{'domain': domain})

        # Need to delete the corresponding cookies for each cookie_collection 
        c.execute("SELECT collection_num FROM cookie_collections WHERE domain = :domain;",{'domain': domain})
        results = c.fetchall()
        for collection_num in results:
            collection_num = collection_num[0]
            c.execute("DELETE FROM cookies WHERE collection_num = :collection_num ;",{'collection_num': collection_num})

        c.execute("DELETE FROM cookie_collections WHERE domain = :domain ;",{'domain': domain})
        c.execute("DELETE FROM dark_patterns WHERE domain = :domain ;",{'domain': domain})
        c.execute("INSERT INTO websites (domain, status, location, timestamp, time) values (?,?,?,datetime('now'),?);", (domain, status, location, time))
        conn.commit()
        conn.close()

    def update_status(self, domain, status):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("UPDATE websites SET status = (?) WHERE domain = (?);", (status, domain))
        conn.commit()
        conn.close()
        
    def update_category(self, domain, category):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("UPDATE websites SET category = (?) WHERE domain = (?);", (category, domain))
        conn.commit()
        conn.close()

    def update_time(self, domain, time):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("UPDATE websites SET time = (?) WHERE domain = (?);", (time, domain))
        conn.commit()
        conn.close()


class Dialogs_table(Database_table):
    def __init__(self, _file_name=None, _name="dialogs"):
        super().__init__(_file_name, _name)

    # Function to add a new dialog to the dialogs table in the ResultsDB.
    def insert_into(self, domain, dialog_num, checked, capture_type, score, css_selector, text, raw_html, screenshot_location):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        file = open(screenshot_location,'rb')
        c.execute("INSERT INTO dialogs (domain, dialog_num, checked, capture_type, score, css_selector, text, raw_html, screenshot) values (?,?,?,?,?,?,?,?,?);", (domain, dialog_num, checked, capture_type, score, css_selector, text, raw_html, sqlite3.Binary(file.read())))
        conn.commit()
        conn.close()

    def select_captureType(self, domain, dialog_num):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("SELECT capture_type FROM dialogs WHERE domain = :domain AND dialog_num = :dialog_num",{'domain': domain, 'dialog_num': dialog_num})
        results = c.fetchall()
        conn.commit()
        conn.close()
        return results[0][0]

    def select_cssSelector(self, domain, dialog_num):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("SELECT css_selector FROM dialogs WHERE domain = :domain AND dialog_num = :dialog_num",{'domain': domain, 'dialog_num': dialog_num})
        results = c.fetchall()
        conn.commit()
        conn.close()
        return results[0][0]

    def select_rawHTML(self, domain, dialog_num):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("SELECT raw_html FROM dialogs WHERE domain = :domain AND dialog_num = :dialog_num",{'domain': domain, 'dialog_num': dialog_num})
        results = c.fetchall()
        conn.commit()
        conn.close()
        return results[0][0]


    def select_captureType(self, domain, dialog_num):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("SELECT capture_type FROM dialogs WHERE domain = :domain AND dialog_num = :dialog_num",{'domain': domain, 'dialog_num': dialog_num})
        results = c.fetchall()
        conn.commit()
        conn.close()
        return results[0][0]

    def select_text(self, domain, dialog_num):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("SELECT text FROM dialogs WHERE domain = :domain AND dialog_num = :dialog_num",{'domain': domain, 'dialog_num': dialog_num})
        results = c.fetchall()
        conn.commit()
        conn.close()
        return results[0][0]


    def select_text_where_checked(self):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("SELECT text FROM dialogs WHERE checked = 'True';")
        results = c.fetchall()
        conn.commit()
        conn.close()
        return results
    
    def select_text_where_checked_and_domain(self, domain):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("SELECT text FROM dialogs WHERE checked = 'True' AND domain = :domain;", {'domain':domain, })
        results = c.fetchall()
        conn.commit()
        conn.close()
        return results[0][0]
    
    def select_rawHTML_where_checked_and_domain(self, domain):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("SELECT raw_html FROM dialogs WHERE checked = 'True' AND domain = :domain;", {'domain':domain, })
        results = c.fetchall()
        conn.commit()
        conn.close()
        return results[0][0]
    
    def select_cssSelector_where_checked(self, domain):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("SELECT css_selector FROM dialogs WHERE domain = :domain AND checked = 'True';", {'domain':domain, })
        results = c.fetchall()
        conn.commit()
        conn.close()
        return results
    
    def select_text_where_score(self, domain, score):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("SELECT dialog_num, text FROM dialogs WHERE domain = :domain AND score > :score AND score NOT NULL;",{'domain' : domain, 'score' : score})
        results = c.fetchall()
        conn.commit()
        conn.close()
        return results
    
    # Function to set the checked field in the dialogs table to 'True' when called.
    def update_checked(self, domain, dialog_num):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("UPDATE dialogs SET checked = 'True' WHERE domain = :domain AND dialog_num = :dialog_num;",{'domain' : domain, 'dialog_num' : dialog_num})
        conn.commit()
        conn.close()
        
    def update_score(self, domain, dialog_num, score):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("UPDATE dialogs SET score = :score WHERE domain = :domain AND dialog_num = :dialog_num;",{'score' :score, 'domain' : domain, 'dialog_num' : dialog_num})
        conn.commit()
        conn.close()
        
    def update_cmp_where_checked(self, domain, cmp):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("UPDATE dialogs SET cmp = :cmp WHERE domain = :domain AND checked = 'True';",{'domain' : domain, 'cmp' : cmp})
        conn.commit()
        conn.close()

    # Function to return the next dialog_num to be added to the dialogs table.
    # Ensures that the unique constraint is maintained by picking the largest dialog number and adding 1.
    def generate_dialog_num(self, domain):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("SELECT MAX(dialog_num) FROM dialogs WHERE domain = :domain;",{'domain' : domain})
        result = c.fetchall()
        conn.commit()
        conn.close()
        if result[0][0] == None:
            return 0
        return int(result[0][0]) + 1

    def select_dialognum_selector_where_domain_checked(self, domain, checked):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("SELECT dialog_num, css_selector FROM dialogs WHERE domain = :domain AND checked = :checked;",{'domain' : domain, 'checked' : checked})
        results = c.fetchall()
        conn.commit()
        conn.close()
        #results = [result[0] for result in results]
        return results
    
    def compute_accuracy(self):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        TP_sql = '''SELECT COUNT(domain) FROM websites w WHERE EXISTS (SELECT domain FROM dialogs d WHERE d.domain = w.domain AND score >0 AND capture_type <> 'User Input') AND EXISTS (SELECT domain FROM dialogs d WHERE d.domain = w.domain AND checked = 'True')'''
        c.execute(TP_sql)
        TP = c.fetchall()[0][0]
        TN_sql = '''SELECT COUNT(domain) FROM websites w WHERE NOT EXISTS (SELECT domain FROM dialogs d WHERE d.domain = w.domain AND score >0 AND capture_type <> 'User Input' ) AND NOT EXISTS (SELECT domain FROM dialogs d WHERE d.domain = w.domain AND checked = 'True')'''
        c.execute(TN_sql)
        TN = c.fetchall()[0][0]
        Total_sql = 'SELECT COUNT(domain) FROM websites'
        c.execute(Total_sql)
        Total = c.fetchall()[0][0]
        conn.commit()
        conn.close()
        #results = [result[0] for result in results]
        return (TP, TN, Total)


class Clickables_table(Database_table):
    def __init__(self, _file_name=None, _name="clickables"):
        super().__init__(_file_name, _name)
    
    def insert_into(self, domain, clickable_num, dialog_num, auto_type, type, css_selector, text, raw_html, screenshot_location):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        file = open(screenshot_location,'rb')
        c.execute("INSERT INTO clickables (domain, clickable_num, dialog_num, auto_type,  type, css_selector, text, raw_html, screenshot) values (?,?,?,?,?,?,?,?,?);", (domain, clickable_num, dialog_num, auto_type, type, css_selector, text, raw_html, sqlite3.Binary(file.read())))
        conn.commit()
        conn.close()

    def generate_clickable_num(self, domain):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("SELECT MAX(clickable_num) FROM clickables WHERE domain = :domain;",{'domain' : domain})
        result = c.fetchall()
        conn.commit()
        conn.close()
        if result[0][0] == None:
            return 0
        return int(result[0][0]) + 1

    def update_type(self, domain, clickable_num, type):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("UPDATE clickables SET type = :type WHERE domain = :domain AND clickable_num = :clickable_num;",{'domain' : domain, 'clickable_num':clickable_num, 'type':type})
        conn.commit()
        conn.close()
    
    def update_autotype(self, domain, clickable_num, auto_type):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("UPDATE clickables SET auto_type = :type WHERE domain = :domain AND clickable_num = :clickable_num;",{'domain' : domain, 'clickable_num':clickable_num, 'type':auto_type})
        conn.commit()
        conn.close()
        
    def select_rawHTML(self, domain, clickable_num):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("SELECT raw_html FROM clickables WHERE domain = :domain AND clickable_num = :clickable_num",{'domain': domain, 'clickable_num': clickable_num})
        results = c.fetchall()
        conn.commit()
        conn.close()
        return results[0][0]
    
    def select_text(self, domain, clickable_num):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("SELECT text FROM clickables WHERE domain = :domain AND clickable_num = :clickable_num",{'domain': domain, 'clickable_num': clickable_num})
        results = c.fetchall()
        conn.commit()
        conn.close()
        return results[0][0]
    
    def select_clickableNum_type(self, domain):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("SELECT clickable_num, type FROM clickables WHERE domain = :domain",{'domain': domain,})
        results = c.fetchall()
        conn.commit()
        conn.close()
        return results
    
    def select_clickableNum_autoType(self, domain):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("SELECT clickable_num, auto_type FROM clickables WHERE domain = :domain",{'domain': domain,})
        results = c.fetchall()
        conn.commit()
        conn.close()
        return results
    
    def select_CSSSelector_where_type(self, domain, type):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("SELECT css_selector FROM clickables WHERE domain = :domain AND type = :type",{'domain': domain, 'type':type})
        results = c.fetchall()
        conn.commit()
        conn.close()
        return results
    
    def select_CSSSelector_where_autoType(self, domain, type):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("SELECT css_selector FROM clickables WHERE domain = :domain AND auto_type = :type",{'domain': domain, 'type':type})
        results = c.fetchall()
        conn.commit()
        conn.close()
        return results
    
    def compute_accuracy(self):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        TC_sql = 'SELECT COUNT(*) FROM clickables WHERE type == auto_type AND type <> "duplicate";'
        c.execute(TC_sql)
        TC = c.fetchall()[0][0]
        Total_sql = 'SELECT COUNT(*) FROM clickables WHERE type <> "duplicate";'
        c.execute(Total_sql)
        Total = c.fetchall()[0][0]
        conn.commit()
        conn.close()
        #results = [result[0] for result in results]
        return (TC, Total)

class Dark_patterns_table(Database_table):
    def __init__(self, _file_name=None, _name="dialogs"):
        super().__init__(_file_name, _name)

    def insert_into(self, domain, type, value, auto_value):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("INSERT INTO dark_patterns (domain, type, value, auto_value) values (?,?,?,?);", (domain, type, value, auto_value))
        conn.commit()
        conn.close()
    
    def update_value(self,domain,type,value):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("UPDATE dark_patterns SET value = :value WHERE domain = :domain AND type = :type;", {"domain":domain, "type":type, "value":value})
        conn.commit()
        conn.close()
        
    def compute_accuracy(self):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        TP_sql = 'SELECT COUNT(*) FROM dark_patterns WHERE auto_value <> "unconfirmed" AND value = "True" and auto_value = "True";'
        c.execute(TP_sql)
        TP = c.fetchall()[0][0]
        TN_sql = 'SELECT COUNT(*) FROM dark_patterns WHERE auto_value <> "unconfirmed" AND value = "False" and auto_value = "False";'
        c.execute(TN_sql)
        TN = c.fetchall()[0][0]
        Total_sql = 'SELECT COUNT(*) FROM dark_patterns WHERE auto_value = "True" OR auto_value = "False";'
        c.execute(Total_sql)
        Total = c.fetchall()[0][0]
        conn.commit()
        conn.close()
        #results = [result[0] for result in results]
        return (TP, TN, Total)
    
    def select_numClicks(self, domain):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("SELECT value FROM dark_patterns WHERE domain = :domain AND type = 'number of clicks to reject cookies';", {"domain":domain,})
        result = c.fetchall()[0][0]
        if result == None:
            result = 0
        return int(result)

class Cookie_collections_table(Database_table):
    def __init__(self, _file_name=None, _name="cookie_collections"):
        super().__init__(_file_name, _name)

    def insert_into(self, collection_num, domain, type, num_cookies):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("INSERT INTO cookie_collections (collection_num, domain, type, num_cookies, timestamp) values (?,?,?,?, datetime('now'));", (collection_num, domain, type, num_cookies))
        conn.commit()
        conn.close()

    def generate_collection_num(self):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("SELECT MAX(collection_num) FROM cookie_collections;")
        result = c.fetchall()
        conn.commit()
        conn.close()
        if result[0][0] == None:
            return 0
        return int(result[0][0]) + 1
    
    def select_numCookies(self, domain, type):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("SELECT num_cookies FROM cookie_collections WHERE domain = :domain AND type = :type",{'domain': domain, 'type':type})
        results = c.fetchall()
        conn.commit()
        conn.close()
        return results[0][0]


class Cookies_table(Database_table):
    def __init__(self, _file_name=None, _name="cookies"):
        super().__init__(_file_name, _name)
    
    def insert_into(self, collection_num, cookie_num, name, value, domain, path, expires, size, HttpOnly, secure, SameSite, raw_cookie):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("INSERT INTO cookies (collection_num, cookie_num, name, value, domain, path, expires, size, HttpOnly, secure, SameSite, raw_cookie) values (?,?,?,?,?,?,?,?,?,?,?,?);", (collection_num, cookie_num, name, value, domain, path, expires, size, HttpOnly, secure, SameSite, raw_cookie))
        conn.commit()
        conn.close()

    def generate_cookie_num(self, domain):
        conn = sqlite3.connect(self.file_name)
        c = conn.cursor()
        c.execute("SELECT MAX(cookie_num) FROM cookies WHERE domain = :domain;",{'domain' : domain})
        result = c.fetchall()
        conn.commit()
        conn.close()
        if result[0][0] == None:
            return 0
        return int(result[0][0]) + 1
