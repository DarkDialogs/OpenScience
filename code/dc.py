import sys
from dark_cookies import CDA
from dark_cookies.CDA_Options import Options

# Function to explore a single website.
def explore_website(domain):
    '''
    param domain: string
        specifies the base domain of the webpage that we are analysing.
    '''
    options = Options()
    CDA(domain, options=options)

def from_file(file_name):
    print(file_name)
    lines = open(file_name, 'r')
    for website in lines:
        explore_website(website.rstrip())

# Function used to parse arguments when the script is run.
def main(args):
    '''
    param args: List[String]
        the arguments for the script.
    '''
    # Parse the name of the command
    if (len(args) > 1):
        arg1 = str(args[1]).lower()
    else:
        raise Exception("Error: Not enough arguments given.")
    if(arg1 == "from"):
        if len(args) > 2:
            arg2 = str(args[2])
            from_file(arg2)
    else:
        # Command to explore the tool on the a single website
        # Syntax: python src/scrape_manager.py <website_domain>
        explore_website(arg1)
    
    
if __name__ == "__main__":
    main(sys.argv)