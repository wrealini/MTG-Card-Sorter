from guizero import App, Text
import database
import arm
import sorting_window
import test_window
import scanner_window

app = App(title="MTG Sorter Updater", height=50)
text = Text(app, text="Downloading...")
cd = None
def start_program():
    cd = database.CardDatabase(app_output=app, text_output=text)
    tw = test_window.TestWindow(app)
    scw = scanner_window.ScannerWindow(app)
    sow = sorting_window.SortingWindow(app, text, cd, tw, scw)
app.after(1000, start_program)
app.display()