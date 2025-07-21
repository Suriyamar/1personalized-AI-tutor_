import csv
import os

def verify_user(username, password):
    users_file = os.path.join(os.path.dirname(__file__), "users.csv")
    if not os.path.exists(users_file):
        return None
    with open(users_file, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["username"] == username and row["password"] == password:
                return row
    return None