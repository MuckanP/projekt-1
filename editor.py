#=== editor för redan existerande bilar ===#
# (denna är en egen fil då editor är inbakat i gui koden och därför svårt att flytta till file_edit)

import customtkinter as ctk
from tkinter import messagebox
from main import CSV_FILE, FIELDNAMES
from suffix import auto_suffix # importera auto_suffix funktionen
from file_edit import save_csv

class CarEditor(ctk.CTkToplevel):
    def __init__(self, master, title, car):
        super().__init__(master)
        self.title(title)
        self.geometry("420x520")
        self.master = master
        self.car = car or {}
        self.original_id = str(self.car.get("id", "")) if car else None #spara en kopia av bilen som redigeras

        self.inputs = {}

        ctk.CTkLabel(self, text=title, font=("Segoe UI Black", 22)).pack(pady=10)

        for field in FIELDNAMES:
            frame = ctk.CTkFrame(self)
            frame.pack(fill="x", pady=5, padx=15)

            ctk.CTkLabel(frame, text=field.upper(), width=110).pack(side="left")
            entry = ctk.CTkEntry(frame)
            entry.pack(side="right", fill="x", expand=True)

            entry.insert(0, self.car.get(field, ""))
            self.inputs[field] = entry

        btn_text = "Save" if car else "Add"
        ctk.CTkButton(self, text=btn_text, command=self.save).pack(pady=15)

    def save(self):
        new_data = {}

        for field in FIELDNAMES:
            raw = self.inputs[field].get().strip()
            # For id and year we keep as-is (string), for numeric fields we add suffixes if needed
            new_data[field] = auto_suffix(field, raw) if field in ("hp", "torque", "price", "odometer") else raw

        if not all(str(v).strip() for v in new_data.values()):
            messagebox.showwarning("Missing Data", "All fields must be filled.")
            return

        # If editing: replace the correct item by matching original_id (so changing ID still works)
        if self.car:
            # find index by original_id (fallback to current id)
            lookup_id = self.original_id if self.original_id is not None else new_data.get("id", "")
            updated = False
            for i, c in enumerate(self.master.data):
                if str(c.get("id", "")) == str(lookup_id):
                    self.master.data[i] = new_data
                    updated = True
                    break
            if not updated:
                messagebox.showerror("Error", "Could not find original car to update.")
                return
        else:  # lägg till 
            # förhindrar duplicering av ID vid tillägg
            if any(str(c.get("id", "")) == str(new_data.get("id", "")) for c in self.master.data):
                messagebox.showerror("Duplicate ID", "ID already exists.")
                return
            self.master.data.append(new_data)

        save_csv(CSV_FILE, self.master.data, FIELDNAMES)
        self.master.populate_tree()
        self.destroy()