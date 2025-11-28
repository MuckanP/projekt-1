#LÄGG TILL MILTAL SENARE

import customtkinter as ctk
from tkinter import ttk, messagebox
import csv
import os

# === CONFIG ===
CSV_FILE = "cars.csv"  # CSV filename
FIELDNAMES = ["id", "make", "model", "year", "odometer", "hp", "torque", "price"]

def auto_suffix(field, value): # lägger till suffix/enheter automatiskt
    value = value.strip()

    # hp → append " hp"
    if field == "hp":
        # If already has "hp", keep it
        if not value.lower().endswith("hp"):
            return f"{value} hp"
        return value

    # torque → append " Nm"
    if field == "torque":
        if not value.lower().endswith("nm"):
            return f"{value} Nm"
        return value

    # price → append " $"
    if field == "price":
        if not value.endswith("$"):
            return f"{value} $"
        return value
    
    if field == "odometer":
        if not value.lower().endswith("km"):
            return f"{value} km"
        return value

    # All other fields unchanged
    return value


# === CSV HELPERS ===
def load_csv(filename):
    if not os.path.exists(filename):
        return []

    with open(filename, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)

        rows = list(reader)
        if not rows:
            return []

        # Normalize header names (strip spaces + BOM)
        headers = [h.strip().lower() for h in rows[0]]

        data = []
        for row in rows[1:]:
            # Skip blank lines
            if not any(row):
                continue

            entry = {}
            for idx, header in enumerate(headers):
                if idx < len(row):
                    entry[header] = row[idx].strip()
                else:
                    entry[header] = ""      # missing value
            data.append(entry)

        return data


def save_csv(filename, data, fieldnames):
    with open(filename, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

# === MAIN APPLICATION ===
class CarDealerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Car Dealership Inventory")
        self.geometry("1000x600")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.data = load_csv(CSV_FILE)
        self.sort_column = None
        self.sort_reverse = False

        # --- STYLE THE TABLE (dealership dashboard look) ---
        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Treeview",
            background="#1a1a1a",
            fieldbackground="#1a1a1a",
            foreground="white",
            rowheight=30,
            font=("Segoe UI", 12)
        )
        style.configure(
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

        # --- MAIN FRAME ---
        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        # --- TITLE ---
        title = ctk.CTkLabel(frame, text="Car Inventory", font=("Segoe UI Black", 28))
        title.pack(pady=10)

        # --- TREEVIEW ---
        self.tree = ttk.Treeview(frame, columns=FIELDNAMES, show="headings")

        for col in FIELDNAMES:
            self.tree.heading(col, text=col.upper(), command=lambda c=col: self.sort_by(c))
            self.tree.column(col, width=130)

        self.tree.pack(fill="both", expand=True)

        yscroll = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        yscroll.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=yscroll.set)

        # --- BUTTON BAR ---
        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(fill="x", pady=10)

        ctk.CTkButton(btn_frame, text="Add Car", command=self.add_window).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Edit Selected", command=self.edit_window).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Delete Selected", command=self.delete_car).pack(side="left", padx=5)

        self.populate_tree()

    # === TABLE POPULATION ===
    def populate_tree(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for i, car in enumerate(self.data):
            tag = "odd" if i % 2 else "even"
            self.tree.insert("", "end", values=[car[k] for k in FIELDNAMES], tags=(tag,))

        self.tree.tag_configure("even", background="#1a1a1a")
        self.tree.tag_configure("odd", background="#212121")

    # === SORTING ===
    def sort_by(self, column):
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False

        self.data.sort(key=lambda x: x[column].lower(), reverse=self.sort_reverse)
        self.populate_tree()

    # === ADD / EDIT / DELETE ===
    def add_window(self):
        CarEditor(self, "Add Car", None)

    def edit_window(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Select a car to edit.")
            return
        values = self.tree.item(sel[0])["values"]
        car = dict(zip(FIELDNAMES, values))
        CarEditor(self, "Edit Car", car)

    def delete_car(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Select a car to delete.")
            return
        
        # Get the ID of the selected car
        values = self.tree.item(sel[0])["values"]
        car_id = values[0]  # ID is the first value
        
        # Confirm deletion
        result = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete car with ID: {car_id}?")
        if result:
            # Remove the car from data
            self.data = [car for car in self.data if car["id"] != car_id]
            
            # Save to CSV and refresh the table
            save_csv(CSV_FILE, self.data, FIELDNAMES)
            self.populate_tree()
            messagebox.showinfo("Success", "Car deleted successfully.")

# === EDITOR WINDOW ===
class CarEditor(ctk.CTkToplevel):
    def __init__(self, master, title, car):
        super().__init__(master)
        self.title(title)
        self.geometry("400x500")
        self.master = master
        self.car = car or {}

        self.inputs = {}

        ctk.CTkLabel(self, text=title, font=("Segoe UI Black", 22)).pack(pady=10)

        for field in FIELDNAMES:
            frame = ctk.CTkFrame(self)
            frame.pack(fill="x", pady=5, padx=15)

            ctk.CTkLabel(frame, text=field.upper(), width=90).pack(side="left")
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
            new_data[field] = auto_suffix(field, raw)

        if not all(new_data.values()):
            messagebox.showwarning("Missing Data", "All fields must be filled.")
            return

        if self.car:  # Update
            for i, c in enumerate(self.master.data):
                if c["id"] == self.car["id"]:
                    self.master.data[i] = new_data
                    break
        else:  # Add
            if any(c["id"] == new_data["id"] for c in self.master.data):
                messagebox.showerror("Duplicate ID", "ID already exists.")
                return
            self.master.data.append(new_data)

        save_csv(CSV_FILE, self.master.data, FIELDNAMES)
        self.master.populate_tree()
        self.destroy()


# === MAIN ===
if __name__ == "__main__":
    app = CarDealerApp()
    app.mainloop()