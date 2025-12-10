#=== programmets huvudfil ===#

from gui import CarDealerApp

CSV_FILE = "cars.csv"  # CSV filens namn
FIELDNAMES = ["id", "make", "model", "year", "odometer", "hp", "torque", "price"]

if __name__ == "__main__":
    app = CarDealerApp()
    app.mainloop()