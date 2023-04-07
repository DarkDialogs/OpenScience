# Import the required Interfaces from the User Input Interface module.
from dark_cookies.uii import Confirm_Box
# Import the mouse class from pynput - used to record mouse clicks.
from pynput import mouse
import timeit
import logging
# From the sfl module import the required functions.
from dark_cookies.sfl import save_cookies

class Cookie_Rejector():
    def __init__(self, conf):
        # The WebDriver instance
        self.driver = conf.driver
        # The domain of the website
        self.domain = conf.domain
        # The number of clicks needed to reject cookies.
        self.num_clicks = 0
        self.resultsDB = conf.resultsDB


    def on_click(self, x, y, button, pressed):
        """Function which is used to increment the number of clicks.

        Args:
            x (int): x value of the mouse.
            y (int): y value of the mouse.
            button (n/a): n/a
            pressed (boolean): boolean value which indicates if the mouse has been clicked.
        """
        # If the button was pressed then increment the number of clicks.
        if pressed:
            self.num_clicks += 1


    def reject_cookies(self):
        """  Function to allow the user to reject cookies, record the number of clicks and then determine if there is a dark pattern.
        """
        logging.info("Rejecting Cookies for '"+str(self.domain)+"'...")
        start = timeit.default_timer()
        # Set the number of clicks to zero.
        self.num_clicks = 0
        # Start a listener for mouse clicks.
        listener = mouse.Listener(on_click=self.on_click)
        listener.start()
        # Prompt the user to confirm when they have rejected all cookies.
        app = Confirm_Box( description="Reject Cookies and then click confirm.", window_name="Cookie Rejector")
        app.mainloop()
        # Remove the extra click used to click the confirm button.
        total_clicks = self.num_clicks - 1 
        logging.debug("Num clicks = "+str(total_clicks))
        # Stop the listener.
        listener.stop()
        stop = timeit.default_timer()
        total_time = stop - start
        logging.debug('Time to reject cookies: '+ str(total_time) + "s")
        # Save the time to reject cookies to the database.
        self.resultsDB.dark_patterns.insert_into(self.domain,"time to reject cookies manually", total_time, total_time)
        # Save the number of clicks to the database.
        self.resultsDB.dark_patterns.insert_into(self.domain,"number of clicks to reject cookies", total_clicks, total_clicks)
        
        # Save the cookies present on the website after rejecting cookies.
        save_cookies(self.driver, self.domain, self.resultsDB, 'opt-out option')
