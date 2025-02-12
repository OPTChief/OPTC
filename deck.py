import tkinter as tk
from tkinter import ttk, messagebox
import aiohttp
import asyncio
from PIL import Image, ImageTk
import logging
import config
import requests
from tqdm.asyncio import tqdm as tqdm_async
from io import BytesIO
from tqdm import tqdm

class CharacterSelector:
    def __init__(self, character_data=[]):
        
        self.root = None
        self.confirm_button = None
        self.image_labels = []
        self.selected_dicts = []
        self.character_data = character_data
        self.frame = None

    def select_character(self, event, dictionary):
        if len(self.selected_dicts) < 5:
            if dictionary not in self.selected_dicts:
                self.selected_dicts.append(dictionary)
                label = event.widget
                label.config(borderwidth=3, relief="solid", bg="blue", fg="white")
            else:
                self.selected_dicts.remove(dictionary)
                label = event.widget
                label.config(borderwidth=1, relief="solid", bg="white", fg="black")
        else:
            if dictionary in self.selected_dicts:
                self.selected_dicts.remove(dictionary)
                label = event.widget
                label.config(borderwidth=1, relief="solid", bg="white", fg="black")
            else:
                messagebox.showinfo("Error", "Maximum character selection reached.")

    def confirm_selection(self):
        if self.selected_dicts:
            config.team = [card['UniqueID'] for card in self.selected_dicts]
            self.root.destroy()
        else:
            messagebox.showinfo("Error", "Please select at least one character.")
            
    def get_bg_color(self, character_type):
        # Define the background colors for different character types
        bg_colors = {
            0: 'cyan',    # AGL
            1: 'green',   # TEQ
            2: 'purple',  # INT
            3: 'red',     # STR
            4: 'orange',  # PHY
            10: 'cyan',   # S_AGL
            11: 'green',  # S_TEQ
            12: 'purple', # S_INT
            13: 'red',    # S_STR
            14: 'orange', # S_PHY
            20: 'cyan',   # E_AGL
            21: 'green',  # E_TEQ
            22: 'purple', # E_INT
            23: 'red',    # E_STR
            24: 'orange', # E_PHY
        }
        
        return bg_colors.get(character_type, 'white') 

    def search_characters(self, event):
        # Cancel any previously scheduled search
        if hasattr(self, "search_delay"):
            self.root.after_cancel(self.search_delay)
        
        # Schedule the search to execute after 5 seconds
        self.search_delay = self.root.after(3000, self.perform_search)
        
    def perform_search(self):
        query = self.search_entry.get()
        filtered_data = self.filter_characters(query)
        self.update_character_labels(filtered_data)       
    
    def filter_characters(self, query):
        filtered_data = []
        for character in self.character_data:
            name_match = query.lower() in character.get('Name', '').lower()
            types_match = any(query.lower() in category.lower() for category in character.get('Types', []))
            classes_match = any(query.lower() in category.lower() for category in character.get('Classes', []))
            if name_match or types_match or classes_match:
                filtered_data.append(character)  
        return filtered_data
                
    def update_character_labels(self, data):
        data = [character for character in data if character['Rarity'] not in ['1★','1★+','2★','2★+','3★','3★+','4★']]
        for label in self.image_labels:
            try:
                label.destroy()
            except Exception as e:
                pass

        for i, character in enumerate(tqdm(data, desc="Downloading Images")):
            try:
                response = requests.get(character['image_url'], stream=True)
                response.raise_for_status()  # Check for any request errors

                image = Image.open(BytesIO(response.content))
                max_height = 70
                desired_width = int(image.width * max_height / image.height)
                desired_height = max_height
                
                image = image.convert("RGBA")
                image = image.resize((desired_width, desired_height), Image.LANCZOS)
                photo = ImageTk.PhotoImage(image)

                row = i // 10
                col = i % 10

                label = tk.Label(self.frame, image=photo, text=character['ID'], borderwidth=1, relief="solid")
                label.character = character
                label.bind("<Button-1>", lambda event, arg=character: self.select_character(event, arg))
                label.photo = photo

                # Set the background color based on the 'type' attribute
                bg_color = self.get_bg_color(character['Type1'])
                label.configure(bg=bg_color)

                label.grid(row=row, column=col, padx=2, pady=2)
                self.image_labels.append(label)
            except Exception as e:
                logging.error(f"Failed to load image for character {character['ID']}: {e}")
                pass
    
    async def create_gui(self, data):
        data = [character for character in data if character['Rarity'] not in ['1★','1★+','2★','2★+','3★','3★+','4★']] 
        self.selected_dicts = []
        self.character_data = data
        self.root = tk.Tk()
        self.root.title("Team update")
        self.root.geometry("1100x900")
        
        num_characters = len(data)
        num_columns = 10
        num_rows = (num_characters + num_columns - 1) // num_columns

        # Create a canvas with scrollbar
        canvas = tk.Canvas(self.root)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(self.root, command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        # Configure the canvas to work with the scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Create a frame inside the canvas to hold the image labels
        self.frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=self.frame, anchor="nw")

        # Create an aiohttp session
        async with aiohttp.ClientSession() as session:
            # Create tasks for downloading images
            tasks = [self.download_image(session, character) for character in data]

            # Gather all tasks to download images simultaneously
            images = await asyncio.gather(*tasks)

        for i, (character, image) in enumerate(zip(data, images)):
            if image is not None:
                row = i // num_columns
                col = i % num_columns

                label = tk.Label(self.frame, image=image, text=character['ID'], borderwidth=1, relief="solid")
                label.character = character
                label.bind("<Button-1>", lambda event, arg=character: self.select_character(event, arg))
                label.photo = image

                # Set the background color based on the 'type' attribute
                bg_color = self.get_bg_color(character['Type1'])
                label.configure(bg=bg_color)

                label.grid(row=row, column=col, padx=2, pady=2)
                self.image_labels.append(label)

        confirm_button = ttk.Button(self.root, text="Confirm", command=self.confirm_selection)
        confirm_button.pack(pady=10)

        # Create a search bar
        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=10)

        search_label = tk.Label(search_frame, text="Search:")
        search_label.pack(side="left")

        self.search_entry = tk.Entry(search_frame)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_characters)

        self.root.mainloop()
    

    async def download_image(self, session, character):
        try:
            async with session.get(character['image_url']) as response:
                response.raise_for_status()  # Check for any request errors

                image_data = await response.read()

            image = Image.open(BytesIO(image_data))
            max_height = 70
            desired_width = int(image.width * max_height / image.height)
            desired_height = max_height

            # Convert the image to RGBA mode to handle transparency
            image = image.convert("RGBA")

            image = image.resize((desired_width, desired_height), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            return photo

        except Exception as e:
            # logging.error(f"Failed to load image for character {character['id']}: {e}")
            return None
            
# data = [{
#             'Type1': 'STR',
#             'Type2': 'QCK',
#             'Types': ['QCK','STR'],
#             'class1': 'Class1',
#             'class2': 'Class2',
#             'Classes': ['Class1', 'Class2'],
#             'ID': 10084,
#             'image_url': utils.get_card_url(10092),
#             'Rarity': 'SSR',
#             'Name': 'Luffy',
#             'UniqueID': 1
#         },
#         {
#             'Type1': 'STR',
#             'Type2': 'QCK',
#             'Types': ['QCK','STR'],
#             'class1': 'Class1',
#             'class2': 'Class2',
#             'Classes': ['Class1', 'Class2'],
#             'ID': 10084,
#             'image_url': utils.get_card_url(10103),
#             'Rarity': 'SSR',
#             'Name': 'Luffy',
#             'UniqueID': 2
#         },
#         {
#             'Type1': 'STR',
#             'Type2': 'QCK',
#             'Types': ['QCK','STR'],
#             'class1': 'Class1',
#             'class2': 'Class2',
#             'Classes': ['Class1', 'Class2'],
#             'ID': 10084,
#             'image_url': utils.get_card_url(10181),
#             'Rarity': 'SSR',
#             'Name': 'Luffy',
#             'UniqueID': 3
#         },
#         {
#             'Type1': 'STR',
#             'Type2': 'QCK',
#             'Types': ['QCK','STR'],
#             'class1': 'Class1',
#             'class2': 'Class2',
#             'Classes': ['Class1', 'Class2'],
#             'ID': 10084,
#             'image_url': utils.get_card_url(10182),
#             'Rarity': 'SSR',
#             'Name': 'Luffy',
#             'UniqueID': 4
#         },
#         {
#             'Type1': 'STR',
#             'Type2': 'QCK',
#             'Types': ['QCK','STR'],
#             'class1': 'Class1',
#             'class2': 'Class2',
#             'Classes': ['Class1', 'Class2'],
#             'ID': 10084,
#             'image_url': utils.get_card_url(11705),
#             'Rarity': 'SSR',
#             'Name': 'Luffy',
#             'UniqueID': 5
#         },
#         {
#             'Type1': 'STR',
#             'Type2': 'QCK',
#             'Types': ['QCK','STR'],
#             'class1': 'Class1',
#             'class2': 'Class2',
#             'Classes': ['Class1', 'Class2'],
#             'ID': 10084,
#             'image_url': utils.get_card_url(11409),
#             'Rarity': 'SSR',
#             'Name': 'Luffy',
#             'UniqueID': 6
#         }
#         ]
# gui = CharacterSelector()
# loop = asyncio.new_event_loop()
# asyncio.set_event_loop(loop)

