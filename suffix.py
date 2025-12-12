
#=== allting att göra med suffix ===#

from file_edit import FIELDNAMES

def auto_suffix(field, value): # lägger till suffix/enheter automatiskt
    value = value.strip()

    # hp > append "hp" med mellanrum
    if field == "hp":
        #ifall suffix redan finns lägger inte till igen
        if not value.lower().endswith("hp"):
            return f"{value} hp"
        return value

    # torque > append "Nm" med mellanrum
    if field == "torque":
        #ifall suffix redan finns lägger inte till igen
        if not value.lower().endswith("nm"):
            return f"{value} Nm"
        return value

    # price > append "$" med mellanrum
    if field == "price":
        #ifall suffix redan finns lägger inte till igen
        if not value.endswith("$"):
            return f"{value} $"
        return value
    
    # odometer > append "km" med mellanrum
    if field == "odometer":
        #ifall suffix redan finns lägger inte till igen
        if not value.lower().endswith("km"):
            return f"{value} km"
        return value

    # om inget fält matchar ska returnera värdet oförändrat
    return value
