import tkinter as tk
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk


### COMMON FUNCTIONS
#Function to centre the tk window
def center_window(master):
    # Need to update the master so that the window dimensions are current.
    master.update()
    # Get the width and height of the user's display
    screen_width = int(master.winfo_screenwidth())
    screen_height = int(master.winfo_screenheight())
    # Get the width and height of the master window.
    window_width =  master.winfo_reqwidth()
    window_height =  master.winfo_reqheight()
    # Check that the height of the window is not larger than the user display size
    if window_height > screen_height:
        window_height = screen_height
    # Calcualte the x and y coordinates need to center the master window.
    x_coordinate = int((screen_width/2) - (window_width/2))
    y_coordinate = int((screen_height/2) - (window_height/2))
    # Reposition the master window using the x and y coordinates calculated above..
    master.geometry("{}x{}+{}+{}".format(window_width, window_height, x_coordinate, y_coordinate))


# Function to set the theme of the Interface.
def set_theme(object, theme='dark'):
    # RGB Color Picker: https://www.rapidtables.com/web/color/RGB_Color.html
    if theme == 'dark':
        object.bg_color = '#1E1E1E'
        object.btn_text_color = "#6A9949"
        # Red
        #object.text_color = "#CE9178"
        # Blue
        object.text_color = "#569CD6"
        # Green
        #object.text_color = "#6A9949"
        #Turquoise
        #object.text_color = "#4EC9B0"
        object.dialog_highlight_color = "#FF3333"
    else:
        object.bg_color = '#E0E0E0'
        object.configure(background='#E0E0E0')
        object.btn_text_color = "green"
        object.text_color = "black"
        object.dialog_highlight_color = "red2"
    #object.master.wm_iconbitmap(dirname(__file__)+'/tk_icon.ico')
    object.font = ("Trebuchet MS", 12, 'bold')

### INTERFACES
# Interface to allow the user to check and select a valid cookie dialog.
# The result variable stores an integer value which is the i-th dialog (in alphabetical order A-Z) 
# of the valid dialog in the screenshots/dialogs or -1 if no dialog was selected.
class Dialog_Checker(tk.Frame):
    def __init__(self, master=None, dialog_nums=[], data_folder_name=".cda"):
        # If not master (basically a tk window instance) was given then create one.
        if master == None:
            master = tk.Tk()
        super().__init__(master)
        self.data_folder_name = data_folder_name
        # Set the dialog number attribute
        self.dialog_nums = dialog_nums
        # Define a scalar which specifies how the size of the dialogs
        # Example: window_scale = 4 will mean dialogs will be 1/4th the size of the user's display screen width.
        self.window_scale = 1.5
        # Setup the master window
        self.master = master
        # Define the colors for the backgrounds and fonts.
        set_theme(self)  
        # Give the tk window a title and background color.
        self.master.title("Cookie Dialog Collector")   
        # Setup an tk IntVar() to store the result of the user selection.
        self.result = IntVar()
        self.result.set(-1)
        # Call the method to draw the widgets on the tk window.
        self.create_widgets()

    def create_widgets(self):
        # See https://stackoverflow.com/questions/43731784/tkinter-canvas-scrollbar-with-grid
        frame_main = tk.Frame(self.master, bg = self.bg_color)
        frame_main.grid(sticky='news')

        # Create a frame for the canvas with non-zero row&column weights
        frame_canvas = tk.Frame(frame_main, bg = self.bg_color)
        frame_canvas.grid(row=2, column=0, pady=(0, 0), sticky='nw')
        frame_canvas.grid_rowconfigure(0, weight=1)
        frame_canvas.grid_columnconfigure(0, weight=1)
        # Set grid_propagate to False to allow 5-by-5 buttons resizing later
        frame_canvas.grid_propagate(False)

        # Add a canvas in that frame
        canvas = tk.Canvas(frame_canvas, bg = self.bg_color)
        canvas.grid(row=0, column=0, sticky="news")

        # Link a vertical scrollbar to the canvas
        vsb = tk.Scrollbar(frame_canvas,bg = self.bg_color, orient="vertical", command=canvas.yview)
        vsb.grid(row=0, column=2, sticky='ns')
        canvas.configure(yscrollcommand=vsb.set)

        # Create a frame to contain the buttons
        frame_buttons = tk.Frame(canvas, bg = self.bg_color)
        canvas.create_window((0, 0), window=frame_buttons, anchor='w')

        # Define the dialogs directory
        mydir = self.data_folder_name+"/screenshots/dialogs"
        # Define a variable n to count the number of files successfully opened as images.
        n = 0
        for i in self.dialog_nums:
            try:
                # Open the image using the Pillow image module.
                load = Image.open(mydir + "/" + str(i)+".png")
                # Determine the width of the dialogs using the window_scale scalar.
                dialog_width = (self.master.winfo_screenwidth()-400)/self.window_scale
                # Calculate the scalar needed to resize the dialog image so that it is the correct size
                scalar = dialog_width / load.size[0]
                # Resize the image using a scalar so it is resized consistently.
                load = load.resize((round(load.size[0]*scalar), round(load.size[1]*scalar)))
                # Render the image using the Pillow ImageTkImage
                render = ImageTk.PhotoImage(load)
                # Draw the image on the tk window and highlight the image.
                panel = Label(frame_buttons, image=render, bg =self.dialog_highlight_color)
                panel.image = render
                # Add the image to the window grid.
                panel.grid(row=n, column=0, padx=10, pady=20)
                # Create a Radio button to the right of the dialog to allow the user to select the correct dialog.
                # NOTE: the text of the button is the file name minus it last 4 letters (removes the image extension)
                c1 = Radiobutton(frame_buttons, bg = self.bg_color, fg=self.text_color ,text='Dialog '+str(i), font = self.font, variable=self.result, value=i)
                # Add the radio button to the window grid.
                c1.grid(row=n, column=1, padx=10)
                # Increment the n variable to indicate the dialog has been succesfully displayed.
                n += 1
            # Catch any exceptions that may occur during execution.
            except Exception as e:
                print("Error could not open '"+str(i)+".png"+"'.")
                #print(e)
            
        # Link a horizontal scrollbar to the canvas
        vsb = tk.Scrollbar(frame_canvas, bg = self.bg_color, orient='horizontal', command=canvas.xview)
        vsb.grid(row=n, column=0, sticky='ew')
        canvas.configure(xscrollcommand=vsb.set)

        # Update buttons frames idle tasks to let tkinter calculate buttons sizes
        frame_buttons.update_idletasks()

        # If there are any elements in the grid then resize it
        if n > 0:
            # Draw the info text at the bottom left of the window.
            text = Label(frame_main, fg=self.text_color, text='Select a valid cookie dialog (or none if there are no valid cookie dialogs present) and then click confirm.', font = self.font, bg = self.bg_color,  padx=10, pady=10)
            frame_canvas.config(width=self.master.winfo_screenwidth()-400,
                height=self.master.winfo_screenheight()-200)
        # Else set the hight of the grid to 0
        else:
            text = Label(frame_main, fg=self.text_color, text='No cookie dialogs were found, click confirm to continue.', font = self.font, bg = self.bg_color,  padx=10, pady=10)
            frame_canvas.config(width=self.master.winfo_screenwidth()-400,
                height=0)

        # Add the info text to the window grid.
        text.grid(row=3, column=0, pady=5, sticky='w')
        # Set the canvas scrolling region
        canvas.config(scrollregion=canvas.bbox("all"))
        # Draw quit (confirm) button in the bottom right of the window.
        self.quit = Button(frame_main, text="Confirm", font = self.font, bg = self.bg_color, fg=self.btn_text_color,command=self.master.destroy)
        # Add the quit button to the window grid.
        self.quit.grid(row=3, column=0, pady=5, sticky='e')
        # Center the window so that it appears in the middle of the user's display.
        center_window(self.master)
        canvas.yview_moveto('0.0')
# Example Usage
"""
app = Dialog_Checker(dialog_nums=[0,1])
app.mainloop()
print(app.result.get())
"""


# Interface to allow the user to input a string.
# The result variable stores an string value which is the value the user entered.
class UII_Inputbox(tk.Frame):
    def __init__(self, master=None, description='Enter a value:', title="Input box"):
        # If not master (basically a tk window instance) was given then create one.
        if master == None:
            master = tk.Tk()
        super().__init__(master)
        # Setup the master window
        self.master = master
        # Set the description attribute
        self.description = description
        # Set the title of the window
        self.title = title
        self.master.title(self.title) 
        # Define the colors for the backgrounds and fonts.
        set_theme(self)  
        # Setup an tk IntVar() to store the result of the user selection.
        self.result = StringVar()
        # Call the method to draw the widgets on the tk window.
        self.create_widgets()

    def create_widgets(self):
        # Create a main frame for the window
        frame_main = tk.Frame(self.master, bg = self.bg_color)
        frame_main.grid(sticky='news')
        # Draw the info text at the top left of the window.
        text = Label(frame_main, text=self.description, font = self.font,fg=self.text_color, bg=self.bg_color)
        # Add the info text to the window grid.
        text.grid(row=0,column=0) 
        # Draw the quit button in the bottom right of the window.
        quit = Button(frame_main, text="Confirm", font = self.font, fg=self.btn_text_color, command=self.master.destroy, bg=self.bg_color)
        # Add the info text to the window grid.
        quit.grid(row=1,column=1,padx=10, pady=10)
        # Draw the css selector input box in the bottom left of the window.
        selector_input = Entry(frame_main, textvariable=self.result, show=None, font=self.font, bg=self.bg_color, fg=self.dialog_highlight_color)
        # Add the css selector to the window grid.  
        selector_input.grid(row = 1, column=0)
        # Center the window so that it appears in the middle of the user's display.
        center_window(self.master)
# Example Usage
"""
app = UII_Inputbox(description='Enter the css selector for the cookie dialog:', title="Cookie Dialog CSS Selector Input")
app.mainloop()
print(app.result.get())
"""


# Interface to allow the user to tag the types of clickable.
class Clickable_Checker(tk.Frame):
    def __init__(self, master=None, input_values={}, choices={}, default_choice="none", description="Select the type of each clickable and then click confirm.",data_folder_name=".cda"):
        # If not master (basically a tk window instance) was given then create one.
        if master == None:
            master = tk.Tk()
        super().__init__(master)
        # Set the atttributes from the inputs
        self.data_folder_name=data_folder_name
        self.input_values = input_values
        self.choices = choices
        self.default_choice = default_choice
        self.description = description
        # Define the colors for the backgrounds and fonts.
        # Define a scalar which specifies how the size of the dialogs
        # Example: window_scale = 4 will mean dialogs will be 1/4th the size of the user's display screen width.
        self.window_scale = 6
        # Setup the master window
        self.master = master
        set_theme(self)
        # Give the tk window a title and background color.
        self.master.title("Clickable Locator")   
        # Setup an dictionary of IntVar() to store the result of the user selection.
        self.result = dict()
        for i in self.input_values:
            self.result[i] = StringVar()
            self.result[i].set(self.input_values[i])
        # Call the method to draw the widgets on the tk window.
        self.create_widgets()

    def create_widgets(self):
        # See https://stackoverflow.com/questions/43731784/tkinter-canvas-scrollbar-with-grid
        # Create a main frame for the window
        frame_main = tk.Frame(self.master, bg = self.bg_color)
        frame_main.grid(sticky='news')

        # Create a frame for the canvas with non-zero row&column weights
        frame_canvas = tk.Frame(frame_main, bg = self.bg_color)
        frame_canvas.grid(row=2, column=0, pady=(0, 0), sticky='nw')
        frame_canvas.grid_rowconfigure(0, weight=1)
        frame_canvas.grid_columnconfigure(0, weight=1)
        # Set grid_propagate to False to allow 5-by-5 buttons resizing later
        frame_canvas.grid_propagate(False)

        # Add a canvas in that frame
        canvas = tk.Canvas(frame_canvas, bg = self.bg_color)
        canvas.grid(row=0, column=0, sticky="news")

        # Link a vertical scrollbar to the canvas
        vsb = tk.Scrollbar(frame_canvas,bg = self.bg_color, orient="vertical", command=canvas.yview)
        vsb.grid(row=0, column=2, sticky='ns')
        canvas.configure(yscrollcommand=vsb.set)

        # Create a frame to contain the buttons
        frame_buttons = tk.Frame(canvas, bg = self.bg_color)
        canvas.create_window((0, 0), window=frame_buttons, anchor='w')

        # Define the dialogs directory
        mydir = self.data_folder_name + "/screenshots/clickables"
        # Define a variable n to count the number of files successfully opened as images.
        n = 0
        for i in self.input_values:
            try:
                # Open the image using the Pillow image module.
                load = Image.open(mydir + "/" + str(i)+".png")
                # Determine the width of the dialogs using the window_scale scalar.
                dialog_width = self.master.winfo_screenwidth()/self.window_scale
                # Calculate the scalar needed to resize the dialog image so that it is the correct size
                scalar = dialog_width / load.size[0]
                # Resize the image using a scalar so it is resized consistently.
                load = load.resize((round(load.size[0]*scalar), round(load.size[1]*scalar)))
                # Render the image using the Pillow ImageTkImage
                render = ImageTk.PhotoImage(load)
                # Draw the image on the tk window and highlight the image.
                panel = Label(frame_buttons, image=render, bg =self.dialog_highlight_color)
                panel.image = render
                # Add the image to the window grid.
                panel.grid(row=n, column=0, padx=10, pady=20)
                # Create a Radio button to the right of the dialog to allow the user to select the correct dialog.
                # NOTE: the text of the button is the file name minus it last 4 letters (removes the image extension)
                l1 = Label(frame_buttons, fg=self.text_color, text='Clickable ' + str(i) + ":", font = self.font, bg = self.bg_color)
                l1.grid(row=n, column=2, sticky="w")
                
                c1 = ttk.OptionMenu(frame_buttons, self.result[i], self.result[i].get(), *self.choices)
                # Add the radio button to the window grid.
                c1.grid(row=n, column=3, padx=0, pady=0, sticky="w")
                # Increment the n variable to indicate the dialog has been succesfully displayed.
                n += 1
            # Catch any exceptions that may occur during execution.
            except Exception as e:
                print("Error could not open '"+str(i)+".png"+"'.")
                print(e)
            
        # Link a horizontal scrollbar to the canvas
        vsb = tk.Scrollbar(frame_canvas, bg = self.bg_color, orient='horizontal', command=canvas.xview)
        vsb.grid(row=n, column=0, sticky='ew')
        canvas.configure(xscrollcommand=vsb.set)

        # Update buttons frames idle tasks to let tkinter calculate buttons sizes
        frame_buttons.update_idletasks()

         # If there are any elements in the grid then resize it
        if n > 0:
            # Draw the info text at the bottom left of the window.
            text = Label(frame_main, fg=self.text_color, text=self.description, font = self.font, bg = self.bg_color,  padx=10, pady=10)
            frame_canvas.config(width=self.master.winfo_screenwidth()-400,
                            height=self.master.winfo_screenheight()-400)
         # Else set the hight of the grid to 0
        else:
            text = Label(frame_main, fg=self.text_color, text='No values were found, click confirm to continue.', font = self.font, bg = self.bg_color,  padx=10, pady=10)
            frame_canvas.config(width=1000,
                            height=0)

        # Add the info text to the window grid.
        text.grid(row=3, column=0, pady=0, sticky='w')
        # Set the canvas scrolling region
        canvas.config(scrollregion=canvas.bbox("all"))
        # Draw quit (confirm) button in the bottom right of the window.
        self.quit = Button(frame_main, text="Confirm", font = self.font, bg = self.bg_color, fg=self.btn_text_color,command=self.master.destroy)
        # Add the quit button to the window grid.
        self.quit.grid(row=3, column=0, pady=5, sticky='e')
        # Center the window so that it appears in the middle of the user's display.
        center_window(self.master)
        canvas.yview_moveto('0.0')
# Example Usage
"""
choices = ["other", "accept","reject"]
input_values = {0:"accept", 1:"reject", 2:"other"}
app = Clickable_Checker(input_values=input_values, choices=choices, default_choice="other")
app.mainloop()
#print(app.result)
[print(str(a)+ ","+str(app.result[a].get())) for a in app.result]
"""


# Interface to allow the user to select all values that apply using a checkboxes.
class Checkbox_Input(tk.Frame):
    def __init__(self, master=None, input_values=dict(), input_descriptions=dict(), description="Check all that apply and then click confirm.",window_name="Checkbox Input"):
        # If not master (basically a tk window instance) was given then create one.
        if master == None:
            master = tk.Tk()
        super().__init__(master)
        # Set the atttributes from the inputs
        self.input_values = input_values
        self.input_descriptions = input_descriptions
        self.description = description
        self.window_name = window_name
        # Define a scalar which specifies how the size of the dialogs
        # Example: window_scale = 4 will mean dialogs will be 1/4th the size of the user's display screen width.
        self.window_scale = 16
        # Setup the master window
        self.master = master
        # Define the colors for the backgrounds and fonts.
        set_theme(self)
        # Give the tk window a title and background color.
        self.master.title(window_name)   
        # Setup an dictionary of BooleanVar() to store the result of the user selection.
        self.result = dict()
        for i in self.input_values:
            self.result[i] = BooleanVar()
            self.result[i].set(self.input_values[i])
        # Call the method to draw the widgets on the tk window.
        self.create_widgets()

    def create_widgets(self):
        # See https://stackoverflow.com/questions/43731784/tkinter-canvas-scrollbar-with-grid
        # Create a main frame for the window
        frame_main = tk.Frame(self.master, bg = self.bg_color)
        frame_main.grid(sticky='news')

        # Create a frame for the canvas with non-zero row&column weights
        frame_canvas = tk.Frame(frame_main, bg = self.bg_color)
        frame_canvas.grid(row=2, column=0, pady=(0, 0), sticky='nw')
        frame_canvas.grid_rowconfigure(0, weight=1)
        frame_canvas.grid_columnconfigure(0, weight=1)
        # Set grid_propagate to False to allow 5-by-5 buttons resizing later
        frame_canvas.grid_propagate(False)

        # Add a canvas in that frame
        canvas = tk.Canvas(frame_canvas, bg = self.bg_color)
        canvas.grid(row=0, column=0, sticky="news")

        # Link a vertical scrollbar to the canvas
        vsb = tk.Scrollbar(frame_canvas,bg = self.bg_color, orient="vertical", command=canvas.yview)
        vsb.grid(row=0, column=2, sticky='ns')
        canvas.configure(yscrollcommand=vsb.set)

        # Create a frame to contain the buttons
        frame_buttons = tk.Frame(canvas, bg = self.bg_color)
        canvas.create_window((0, 0), window=frame_buttons, anchor='nw')

        n = 0
        for i in self.input_values:
            c1 = Checkbutton(frame_buttons, bg = self.bg_color, fg=self.text_color, font = self.font, variable=self.result[i])
            # Add the radio button to the window grid.
            c1.grid(row=n, column=0)

            l1 = Label(frame_buttons, fg=self.text_color, text=str(i) + ": "+ self.input_descriptions[i], font = self.font, bg = self.bg_color)
            l1.grid(row=n, column=1, sticky="w")
            # Increment the n variable to indicate the dialog has been succesfully displayed.
            n += 1
            
        # Link a horizontal scrollbar to the canvas
        vsb = tk.Scrollbar(frame_canvas, bg = self.bg_color, orient='horizontal', command=canvas.xview)
        vsb.grid(row=n, column=0, sticky='ew')
        canvas.configure(xscrollcommand=vsb.set)

        # Update buttons frames idle tasks to let tkinter calculate buttons sizes
        frame_buttons.update_idletasks()

        if n > 0:
            # Draw the info text at the bottom left of the window.
            text = Label(frame_main, fg=self.text_color, text=self.description, font = self.font, bg = self.bg_color,  padx=10, pady=10)
            frame_canvas.config(width=self.master.winfo_screenwidth()-400,
                            height=self.master.winfo_screenheight()-400)
        else:
            text = Label(frame_main, fg=self.text_color, text='No values were found, click confirm to continue.', font = self.font, bg = self.bg_color,  padx=10, pady=10)
            frame_canvas.config(width=1000,
                            height=0)
        # Add the info text to the window grid.
        text.grid(row=3, column=0, pady=5, sticky='w')

        # Set the canvas scrolling region
        canvas.config(scrollregion=canvas.bbox("all"))
        # Draw quit (confirm) button in the bottom right of the window.
        self.quit = Button(frame_main, text="Confirm",bg = self.bg_color, font = self.font, fg=self.btn_text_color,command=self.master.destroy)
        # Add the quit button to the window grid.
        self.quit.grid(row=3, column=0, pady=0, sticky='e')
        # Center the window so that it appears in the middle of the user's display.
        center_window(self.master)
# Example Usage
"""
input_values = {"Dark Pattern 1":False, "No input box reeeeeeeeeeeee":True}
app = Checkbox_Input(input_values=input_values, description="Check all the Dark Patterns and then click confirm.", window_name="ADP")
app.mainloop()
#print(app.result)
[print(str(a)+ ","+str(app.result[a].get())) for a in app.result]
"""


# Interface that prompts the user to confirm they wish to continue.
class Confirm_Box(tk.Frame):
    def __init__(self, master=None, description="Check all that apply and then click confirm.",window_name="Checkbox Input"):
        # If not master (basically a tk window instance) was given then create one.
        if master == None:
            master = tk.Tk()
        super().__init__(master)
        # Set the atttributes from the inputs
        self.description = description
        # Set the name of the window
        self.window_name = window_name
        self.master.title(window_name)  
        # Setup the master window
        self.master = master
        # Define the colors for the backgrounds and fonts.
        set_theme(self)
        # Setup an tk IntVar() to store the result of the user selection.
        self.create_widgets()
    
    def create_widgets(self):
        # Create a main frame for the window
        frame_main = tk.Frame(self.master, bg = self.bg_color)
        frame_main.grid(sticky='news')
        # Draw the info text at the top left of the window.
        text = Label(frame_main, text=self.description, font = self.font,fg=self.text_color, bg=self.bg_color)
        # Add the info text to the window grid.
        text.grid(row=0,column=0) 
        # Draw the quit button in the bottom right of the window.
        quit = Button(frame_main, text="Confirm", font = self.font, fg=self.btn_text_color, command=self.master.destroy, bg=self.bg_color)
        # Add the info text to the window grid.
        quit.grid(row=0,column=1,padx=10, pady=10)
        # Center the window so that it appears in the middle of the user's display.
        center_window(self.master)
# Example Usage
"""
app = Confirm_Box( description="Reject Cookies and then click confirm.", window_name="Cookie Rejector")
app.mainloop()
"""


# Display all fonts
"""
import tkinter.font
Tk()
for name in sorted(tkinter.font.families()):
    print(name)
"""