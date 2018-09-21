from guizero import Window, MenuBar, Text, CheckBox, PushButton
import scanner
import database

fullscreen = True

class SortingWindow(Window):

    def __init__(self, app, text, cd, test_window, scanner_window):
        Window.__init__(self, app, title="MTG Sorter", layout="grid")
        self.tk.attributes("-fullscreen", True)

        # Components
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
                toplevel=["Windows", "Program"],
                options=[
                    [["Test", open_test], ["Scanner", open_scanner]],
                    [["Update Database", update_database], ["Toggle Fullscreen", toggle_fullscreen], ["End Program", end_program]]
                ])
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
        def sort():
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
            arm.reset()
            print("Sorting cards...")
            while True:
                img = scanner.scan_card()[3]
                if img is not None:
                    card = cd.get_card(img)
                    if card is None:
                        print("0")
                        arm.move_card(1, 2)
                    else:
                        card_type = card.type
                        print(card_type)
                        moved = False
                        for c in checkboxes1:
                            if c.value:
                                if c.text in card_type:
                                    print("1")
                                    arm.move_card(1, 3)
                                    moved = True
                                    break
                        if moved:
                            continue
                        for c in checkboxes2:
                            if c.value:
                                if c.text in card_type:
                                    print("2")
                                    arm.move_card(1, 4)
                                    break
                        if moved:
                            continue
                        print("0")
                        arm.move_card(1, 2)
                elif cd.is_empty():
                    print("tray is empty")
                    break
                else:
                    print("0")
                    arm.move_card(1, 2)
            arm.set_servo(0)
        PushButton(self, command=sort, text="Sort Cards", grid=[0, 11, 2, 1])