import tkinter as tk
import config

selected_list = []


def add_Character():
    selected = listbox.curselection()
    if not selected:
        return
    selected_Character = listbox.get(selected[0])
    if selected_Character in selected_list.get(0, tk.END):
        return
    if selected_list.size() >= 5:
        return
    selected_list.insert(tk.END, selected_Character)


def delete_Character():
    selected = selected_list.curselection()
    if not selected:
        return
    selected_list.delete(selected[0])


def confirm_deck():
    deck = list(selected_list.get(0, tk.END))
    if not deck:
        print("You must select at least one character.")
        return 0
    root.destroy()
    print(deck)
    config.team = deck
    return 0

def confirm_ship():
    deck = list(selected_list.get(0, tk.END))
    if not deck or len(deck) > 1:
        print("You must select one ship.")
        return 0
    root.destroy()
    print(deck)
    config.ship = deck
    return 0

def show(chars_list):
    global listbox, root, selected_list
    root = tk.Tk()
    root.title('Change your deck')
    root.geometry("1250x1080")

    frame = tk.Frame(root)
    frame.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')

    # Create a search bar
    search_label = tk.Label(frame, text="Search:")
    search_label.pack(side=tk.TOP)

    search_entry = tk.Entry(frame, width=50)
    search_entry.pack(side=tk.TOP)

    listbox_frame = tk.Frame(frame)
    listbox_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    listbox_scrollbar = tk.Scrollbar(listbox_frame)
    listbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    listbox = tk.Listbox(listbox_frame, width=100, yscrollcommand=listbox_scrollbar.set)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    listbox_scrollbar.config(command=listbox.yview)

    selected_frame = tk.Frame(root)
    selected_frame.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

    selected_list = tk.Listbox(selected_frame, width=75)
    selected_list.pack(side=tk.LEFT, fill=tk.Y)

    add_button = tk.Button(selected_frame, text='Add Character', command=add_Character)
    add_button.pack(side=tk.TOP)

    delete_button = tk.Button(selected_frame, text='Delete Character', command=delete_Character)
    delete_button.pack(side=tk.TOP)

    confirm_button = tk.Button(selected_frame, text='Confirm Deck', command=confirm_deck)
    confirm_button.pack(side=tk.TOP)

    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)
    root.rowconfigure(0, weight=1)

    for character in chars_list:
        listbox.insert(tk.END, character)

    def search_characters(event=None):
        query = search_entry.get()
        listbox.delete(0, tk.END)
        for character in chars_list:
            if query.lower() in character.lower():
                listbox.insert(tk.END, character)

    search_entry.bind("<KeyRelease>", search_characters)

    root.mainloop()

def show_ship(chars_list):
    global listbox, root, selected_list
    root = tk.Tk()
    root.title('Change your ship')
    root.geometry("1250x720")

    frame = tk.Frame(root)
    frame.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')

    # Create a search bar
    search_label = tk.Label(frame, text="Search:")
    search_label.pack(side=tk.TOP)

    search_entry = tk.Entry(frame, width=75)
    search_entry.pack(side=tk.TOP)

    listbox_frame = tk.Frame(frame)
    listbox_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    listbox_scrollbar = tk.Scrollbar(listbox_frame)
    listbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    listbox = tk.Listbox(listbox_frame, width=100, yscrollcommand=listbox_scrollbar.set)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    listbox_scrollbar.config(command=listbox.yview)

    selected_frame = tk.Frame(root)
    selected_frame.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

    selected_list = tk.Listbox(selected_frame, width=50)
    selected_list.pack(side=tk.LEFT, fill=tk.Y)

    add_button = tk.Button(selected_frame, text='Select Ship', command=add_Character)
    add_button.pack(side=tk.TOP)

    delete_button = tk.Button(selected_frame, text='Remove Ship', command=delete_Character)
    delete_button.pack(side=tk.TOP)

    confirm_button = tk.Button(selected_frame, text='Confirm Ship', command=confirm_ship)
    confirm_button.pack(side=tk.TOP)

    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)
    root.rowconfigure(0, weight=1)

    for character in chars_list:
        listbox.insert(tk.END, character)

    def search_characters(event=None):
        query = search_entry.get()
        listbox.delete(0, tk.END)
        for character in chars_list:
            if query.lower() in character.lower():
                listbox.insert(tk.END, character)

    search_entry.bind("<KeyRelease>", search_characters)

    root.mainloop()  