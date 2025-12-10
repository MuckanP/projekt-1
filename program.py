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
def load_csv(filename): #laddar in csv filen
    if not os.path.exists(filename):
        return []

    with open(filename, "r", encoding="utf-8-sig", newline='') as f:
        reader = csv.reader(f)

        rows = list(reader)
        if not rows:
            return []

        # Normalize header names (strip spaces + BOM)
        headers = [h.strip().lower() for h in rows[0]]

        data = []
        for row in rows[1:]:
            # Skip blank lines
            if not any(cell.strip() for cell in row):
                continue

            entry = {}
            for idx, header in enumerate(headers):
                if idx < len(row):
                    entry[header] = row[idx].strip()
                else:
                    entry[header] = ""      # missing value

            # Ensure all expected FIELDNAMES exist (use empty string if missing)
            for k in FIELDNAMES:
                entry.setdefault(k, "")

            data.append(entry)

        return data


def save_csv(filename, data, fieldnames): #sparar till csv filen
    # Make sure directory exists (if path contains dirs)
    os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
    with open(filename, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def remove_car_by_id(cars, car_id):
    """Safe removal by id. Returns True if removed, False if not found."""
    for i, car in enumerate(cars):
        if str(car.get("id", "")) == str(car_id):
            del cars[i]
            return True
    return False


class CarDealerApp(ctk.CTk): #huvud programmet
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
        self.tree = ttk.Treeview(frame, columns=FIELDNAMES, show="headings", selectmode="browse")

        for col in FIELDNAMES:
            # Use closure default to bind correct column name
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

    def sort_by(self, column): #TODO sorterar tabellen, fungerar ej för nummer just nu 
        
        def parse_value(val):
            if val is None:
                return 0

            s = str(val).lower().strip()

            # Remove common units and symbols
            for unit in ["hp", "nm", "$", "km"]:
                s = s.replace(unit, "").strip()

            # Remove commas or extra spaces
            s = s.replace(",", "").strip()

            # If it's numeric, return number
            if s.replace(".", "", 1).isdigit():
                try:
                    return float(s)
                except:
                    return s
        
            # Fallback: sort as text
            return s

        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False

        # Sort using parsed numeric-aware value
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
        
        # Get the ID of the selected car
        values = self.tree.item(sel[0])["values"]
        if not values:
            messagebox.showerror("Error", "Selected row is empty.")
            return
        car_id = str(values[0])  # ID is the first value
        
        # Confirm deletion
        result = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete car with ID: {car_id}?")
        if result:
            # Remove the car from data safely
            removed = remove_car_by_id(self.data, car_id)
            if removed:
                # Save to CSV and refresh the table
                save_csv(CSV_FILE, self.data, FIELDNAMES)
                self.populate_tree()
                messagebox.showinfo("Success", "Car deleted successfully.")
            else:
                messagebox.showerror("Not Found", f"Could not find car with ID: {car_id}.")


# editor
class CarEditor(ctk.CTkToplevel):
    def __init__(self, master, title, car):
        super().__init__(master)
        self.title(title)
        self.geometry("420x520")
        self.master = master
        # store a reference to the original car dict if editing; if adding, car is None
        self.car = car or {}
        self.original_id = str(self.car.get("id", "")) if car else None

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


# === MAIN ===
if __name__ == "__main__":
    app = CarDealerApp()
    app.mainloop()
