
#=== själva gui programmet ===#

import customtkinter as ctk
from tkinter import ttk, messagebox
from file_edit import FIELDNAMES, CSV_FILE
from file_edit import load_csv, save_csv, remove_car_by_id
from editor import CarEditor




class CarDealerApp(ctk.CTk): # kod för graphical user interface
    def __init__(self):
        super().__init__()
        self.title("Car Dealership Inventory")
        self.geometry("1000x600")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.data = load_csv(CSV_FILE)
        self.sort_column = None
        self.sort_reverse = False

        style = ttk.Style() # utseende för tabellen (1)
        style.theme_use("default")

        style.configure( # fortfarande utseende för tabellen, bakgrund och sånt (2)
            "Treeview",
            background="#1a1a1a",
            fieldbackground="#1a1a1a",
            foreground="white",
            rowheight=30,
            font=("Segoe UI", 12)
        )
        style.configure( # rubrikerna i tabellen, stil (3)
            "Treeview.Heading",
            background="#2b2b2b",
            foreground="#00aaff",
            font=("Segoe UI Semibold", 13)
        )
        style.map(
            "Treeview",
            background=[("selected", "#005f87")],
            foreground=[("selected", "white")]
        )

        # frame
        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        # appens titel
        title = ctk.CTkLabel(frame, text="Car Inventory", font=("Segoe UI Black", 28))
        title.pack(pady=10)

        # treeview (tabell)
        self.tree = ttk.Treeview(frame, columns=FIELDNAMES, show="headings", selectmode="browse")

        for col in FIELDNAMES:
            # Use closure default to bind correct column name
            self.tree.heading(col, text=col.upper(), command=lambda c=col: self.sort_by(c))
            self.tree.column(col, width=130)

        self.tree.pack(fill="both", expand=True)

        yscroll = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        yscroll.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=yscroll.set)

        # bar för knappar
        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(fill="x", pady=10)
        # knappar
        ctk.CTkButton(btn_frame, text="Add Car", command=self.add_window).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Edit Selected", command=self.edit_window).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Delete Selected", command=self.delete_car).pack(side="left", padx=5)

        self.populate_tree()

    def populate_tree(self): #fyller tabellen med data
        for row in self.tree.get_children():
            self.tree.delete(row)

        for i, car in enumerate(self.data):
            tag = "odd" if i % 2 else "even"
            # Use get to avoid KeyError if a key is missing
            values = [car.get(k, "") for k in FIELDNAMES]
            self.tree.insert("", "end", values=values, tags=(tag,))

        self.tree.tag_configure("even", background="#1a1a1a")
        self.tree.tag_configure("odd", background="#212121")

    #sorteringsfunktion för tabellen (vid klick på kolumnernas rubriker)
    def sort_by(self, column):
        
        def parse_value(val):
            if val is None:
                return 0

            s = str(val).lower().strip()

            # ta bort enheter
            for unit in ["hp", "nm", "$", "km"]:
                s = s.replace(unit, "").strip()

            # ta bort kommatecken och extra mellanslag
            s = s.replace(",", "").strip()

            # ifall det är ett nummer, returnera som float
            if s.replace(".", "", 1).isdigit():
                try:    # annars sorterar den efter siffror, inte tal
                    return float(s)
                except:
                    return s
        
            # annars returnera som sträng
            return s

        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False

        # sortera mha parse_value funktionen
        self.data.sort(key=lambda x: parse_value(x.get(column, "")), 
                   reverse=self.sort_reverse)

        self.populate_tree()

    def add_window(self): #lägger till en bil
        CarEditor(self, "Add Car", None)

    def edit_window(self): #ska redigera bil, fungerar ej just nu
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Select a car to edit.")
            return

        # Get ID from selected row values
        values = self.tree.item(sel[0])["values"]
        if not values:
            messagebox.showerror("Error", "Selected row is empty.")
            return
        selected_id = str(values[0])

        # Find the car in self.data by id (use string comparison for safety)
        for car in self.data:
            if str(car.get("id", "")) == selected_id:
                # Pass the actual car dict (not a shallow zip copy), so editor can reference original id
                CarEditor(self, "Edit Car", car)
                return

        messagebox.showerror("Not Found", f"Car with ID {selected_id} not found in data.")

    def delete_car(self): #ska ta bort bil, fungerar ej just nu
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Select a car to delete.")
            return
        
        # fetch id för rad
        values = self.tree.item(sel[0])["values"]
        if not values:
            messagebox.showerror("Error", "Selected row is empty.")
            return
        car_id = str(values[0])  # ID is the first value
        
        #bekräfta ta bort
        result = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete car with ID: {car_id}?")
        if result:
            # ta bort säkert
            removed = remove_car_by_id(self.data, car_id)
            if removed:
                # spara automatiskt till csv fil, uppdatera tabell
                save_csv(CSV_FILE, self.data, FIELDNAMES)
                self.populate_tree()
                messagebox.showinfo("Success", "Car deleted successfully.")
            else:
                messagebox.showerror("Not Found", f"Could not find car with ID: {car_id}.")