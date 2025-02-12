from tkinter import *
import farm,user

def show2(lst):
    # Create an instance of tkinter frame
    points = user.get_user_point()['points']
    win=Tk()
    win.title('Colloseum Groups')

    # Set the geometry
    win.geometry("1000x900")

    # list of stages
    listbox = Listbox(win, width=40, height=60)
    listbox.pack(side=LEFT, fill=BOTH, expand=True)

    # Iterate over each stage in the list and add it to the listbox
    for item in lst:
        if type(item) == str:
            listbox.insert(END, item)
        else:
            listbox.insert(END, item[0] + " - " + item[1])

    # label widget to display the user's points
    points_label = Label(win, text="CURRENT POINTS : {}/200 ".format(points))
    points_label.pack(side=TOP, padx=30, pady=30, anchor=SE)

    # Function to select the stage and close the window
    def select_stage():
        selected_index = listbox.curselection()
        if len(selected_index) == 0:
            # No stage selected
            return
        stage_id = lst[selected_index[0]][0]
        print("Selected stage ID: " +  str(stage_id))
        win.destroy()
        farm.unlock_colosseum(stage_id)
    # button to select the stage
    select_button = Button(win, text="Confirm", width=15, height=5, command=select_stage)
    select_button.pack(side=TOP, padx=20, pady=20)

    win.mainloop()


    
class QuestListGUI:
    def __init__(self, quests):
        self.quests = quests

    def search(self, search_query):
        self.quests_text.delete('1.0', END)
        for q in self.quests:
            if search_query.lower() in q.lower():
                self.quests_text.insert(END, q + '\n')

    def display(self):
        win = Tk()
        win.geometry("920x480")
        win.title('Quest List')

        # Create the frame for the list of quests
        quests_frame = Frame(win)
        quests_frame.pack(side=LEFT, fill=BOTH, expand=True)

        # Create the text widget for the list of quests
        self.quests_text = Text(quests_frame, width=80, height=60)
        self.quests_text.pack(side=LEFT, fill=BOTH, expand=True)

        # Populate the text widget with the quests
        for q in self.quests:
            self.quests_text.insert(END, q + '\n')

        # Create the frame for the search bar
        search_frame = Frame(win)
        search_frame.pack(fill=X)

        # Create the label for the search bar
        search_label = Label(search_frame, text='Search:')
        search_label.pack(side=LEFT)

        # Create the entry widget for the search bar
        self.search_entry = Entry(search_frame)
        self.search_entry.pack(side=LEFT, fill=X, expand=True)

        # Create the button for the search bar
        search_button = Button(search_frame, text='Search', command=lambda: self.search(self.search_entry.get()))
        search_button.pack(side=LEFT)

        win.mainloop()
