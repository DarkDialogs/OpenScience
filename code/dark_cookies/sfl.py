# Function to save the current cookies to the database.
def save_cookies(driver, domain, resultsDB, type):
    '''
    param driver: WebDriver
        an instance of a selenium webdriver used to interact with the webpage.
    param domain: String
        a string specifiying the base domain of the webpage that we are analysing.
    param type: String
        the type of cookie collection we are creating.
    '''
    # https://chromedevtools.github.io/devtools-protocol/tot/Network/#method-getAllCookies
    # https://stackoverflow.com/questions/64211215/selenium-3-python-add-listener-for-chrome-devtools-network-event
    
    # Execute a command to get all the cookies from the Chrome browser for the current webpage
    response = driver.execute_cdp_cmd('Network.getAllCookies', {})
    # Get the cookies from the response
    if 'cookies' in response:    
        cookies = response['cookies']
    else:
        cookies = {}
    # Get the next collection number to store the cookies under.
    collection_num = resultsDB.cookie_collections.generate_collection_num()
    # Create a new collection for the cookies.
    resultsDB.cookie_collections.insert_into(collection_num, domain, type, len(cookies))
    # Get the next cookie number to index the cookies in the database
    cookie_num = resultsDB.cookies.generate_cookie_num(domain)
    # For each cookie in the dict of cookies
    for cookie in cookies:
        # Retreieve the required attributes from the cookie if they are present.
        if 'name' in cookie:
            name = cookie['name']
        else:
            name = None
        if 'value' in cookie:
            value = cookie['value']
        else:
            value = None
        if 'domain' in cookie:
            cookie_domain = cookie['domain']
        else:
            cookie_domain = None
        if 'path' in cookie:
            path = cookie['path']
        else:
            path = None
        if 'expires' in cookie:
            expires = cookie['expires']
        else:
            expires = None
        if 'size' in cookie:
            size = cookie['size']
        else:
            size = None
        if 'httpOnly' in cookie:
            httpOnly = cookie['httpOnly']
        else:
            httpOnly = None
        if 'secure' in cookie:
            secure = cookie['secure']
        else:
            secure = None
        if 'sameSite' in cookie:
            sameSite = cookie['sameSite']
        else:
            sameSite = None
        # Save the cookie to the database.
        resultsDB.cookies.insert_into(collection_num, cookie_num, name, value, cookie_domain, path, expires, size, httpOnly, secure, sameSite, str(cookie))
        # Increment the cookie number by 1
        cookie_num += 1


# Function to shortern the url given by the user and only retain the domain section of the url.
def url_to_domain(base_url):
    '''
    param url: String
        the url to convert
    return: String
        the domain
    '''
    # Remove the protocol and www.
    url = base_url.split('://www.')
    # Only keep the first section
    if len(url) > 1:
        url = url[1].split('/')[0]
    else:
        url = base_url.split('www.')
        if len(url) > 1:
            url = url[1].split('/')[0]
        else:
            url = url[0].split('/')[0]
    return url


# Function to convert a domain to a url.
def domain_to_url(base_domain):
    '''
    param domain: String
        the domain to convert.
    param url: String
        the url 
    '''
    return "https://www." + base_domain