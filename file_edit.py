
#=== (nästan) allting att göra med att läsa, skriva och spara till csv ===#
# (edit och add var svårt att flytta utan att gui medför, då dessa är inbakade i gui koden)

import csv 
import os
from main import FIELDNAMES


def load_csv(filename): #laddar in csv filen
    if not os.path.exists(filename):
        return []

    with open(filename, "r", encoding="utf-8-sig", newline='') as f:
        reader = csv.reader(f)

        rows = list(reader)
        if not rows:
            return []

        #normaliserar rubriker, ser till att de inte ser annourlund ut
        headers = [h.strip().lower() for h in rows[0]]

        data = []
        for row in rows[1:]:
            # hoppa över tomma rader
            if not any(cell.strip() for cell in row):
                continue

            entry = {}
            for idx, header in enumerate(headers):
                if idx < len(row):
                    entry[header] = row[idx].strip()
                else:
                    entry[header] = ""      # missing value

            # ser till att alla FIELDNAMES finns med 
            for k in FIELDNAMES:
                entry.setdefault(k, "")

            data.append(entry)

        return data


def save_csv(filename, data, fieldnames): #sparar till csv filen
    #ser till att directory existerar
    os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
    with open(filename, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def remove_car_by_id(cars, car_id):
    # tar bort produkt via id
    for i, car in enumerate(cars):
        if str(car.get("id", "")) == str(car_id):
            del cars[i]
            return True
    return False