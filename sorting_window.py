from guizero import Window, MenuBar, Text, CheckBox, PushButton
import scanner
import card_database
import arm
import time

#region Sorting Window Summary

# This module creates the main window used to sort cards.

# At the top of the window is a MenuBar which links to all other
# windows and provides program options.

# In the middle of the window are two columns of card type
# CheckBoxes used to select the card types to be sorted into trays
# 3 and 4.

# At the bottom of the window is a Button to begin sorting. When
# pressed, the device starts taking cards out of the first tray
# and placing them into trays 3 and 4 if they fit into the card
# types selected or into tray 2 if they don't or they can't be
# recognized.
#endregion

#region Constants and Variables

fullscreen = True
#endregion


class SortingWindow(Window):

    def __init__(self, app, text, cd, test_window, scanner_window):
        Window.__init__(self, app, title="MTG Sorter", layout="grid")
        self.tk.attributes("-fullscreen", True)

        # Top MenuBar
        def open_test():
            test_window.open_window()
        def open_scanner():
            scanner_window.show()

        def update_database():
            app.show()
            app.focus()
            cd.di = None
            cd.download(app_output=app, text_output=text)
        def toggle_fullscreen():
            global fullscreen
            fullscreen = not fullscreen
            self.tk.attributes("-fullscreen", fullscreen)
            test_window.tk.attributes("-fullscreen", fullscreen)
        def end_program():
            app.destroy()
        MenuBar(self,
                toplevel=["Windows", "Options"],
                options=[
                    [["Test", open_test], ["Scanner", open_scanner]],
                    [["Update Database", update_database], ["Toggle Fullscreen", toggle_fullscreen], ["End Program", end_program]]
                ])

        # Middle Card Type CheckBoxes
        Text(self, text="MTG Sorter", grid=[0, 0, 2, 1])
        Text(self, text="Slot 1 Types", grid=[0, 1])
        Text(self, text="Slot 2 Types", grid=[1, 1])
        types = ["Artifact", "Creature", "Enchantment", "Instant", "Land",
                 "Legendary", "Planeswalker", "Sorcery", "Tribal"]
        checkboxes1 = []
        for n in range(9):
            checkboxes1.append(CheckBox(self, text=types[n], grid=[0, n + 2]))
            checkboxes1[n].width = 22
            checkboxes1[n].text_size = 20
        checkboxes2 = []
        for n in range(9):
            checkboxes2.append(CheckBox(self, text=types[n], grid=[1, n + 2]))
            checkboxes2[n].width = 22
            checkboxes2[n].text_size = 20

        # Bottom Sort Cards Button
        def sort():

            # if nothing is selected in any column, do not sort
            nothing_selected1 = True
            for c in checkboxes1:
                if c.value:
                    nothing_selected1 = False
                    break
            nothing_selected2 = True
            for c in checkboxes2:
                if c.value:
                    nothing_selected2 = False
                    break
            if nothing_selected1 and nothing_selected2:
                print("nothing selected")
                return

            # reset arm to begin sorting
            arm.reset()
            print("Sorting cards...")

            # scan each card
            while True:
                img = scanner.scan_card()[3]
                if img is not None:
                    card = cd.get_card(img)
                    # if card isn't recognized, move it to bin 4
                    if card is None:
                        print("0")
                        arm.move_card(1, 4)
                    else:
                        card_type = card.type
                        print(card_type)
                        moved = False
                        # if card is any of the card types selected for the first bin, move it to bin 2
                        for c in checkboxes1:
                            if c.value:
                                if c.text in card_type:
                                    print("1")
                                    arm.move_card(1, 2)
                                    moved = True
                                    break
                        if moved:
                            continue
                        # if card is any of the card types selected for the second bin, move it to bin 3
                        for c in checkboxes2:
                            if c.value:
                                if c.text in card_type:
                                    print("2")
                                    arm.move_card(1, 3)
                                    break
                        if moved:
                            continue
                        # if card doesn't fit any of the selected types, move it to bin 4
                        print("0")
                        arm.move_card(1, 4)
                # if the tray is empty, end the sorting algorithm
                elif cd.is_empty():
                    print("tray is empty")
                    break
                # if the tray isn't empty but the card art can't be found, move the card to bin 4
                else:
                    print("0")
                    arm.move_card(1, 4)
            
            arm.set_servo(0)
        PushButton(self, command=sort, text="Sort Cards", grid=[0, 11, 2, 1])
