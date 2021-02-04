from guizero import App, Text
import card_database
import arm
import sorting_window
import test_window
import scanner_window

#region Card Sorter Main Summary

# This module is the main file used to initialize all the
# other modules in this project and create the main app
# that all other windows belong to.

# If the card database does not exist or isn't completed,
# then this app window displays the text output from this
# process as the necessary data is downloaded. When the
# database is completed or simply loaded from memory, then
# the sorting window is opened and ready for the user to
# operate it.
#endregion

#region Initialization

app = App(title="Card Sorter Updater", height=50)
text = Text(app, text="Downloading...")
cd = None
def start_program():
    cd = card_database.CardDatabase(app, text)
    tw = test_window.TestWindow(app)
    scw = scanner_window.ScannerWindow(app, cd)
    sow = sorting_window.SortingWindow(app, text, cd, tw, scw)
app.after(1000, start_program)
app.display()
#endregion
