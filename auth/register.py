import csv
import os

def register_user(full_name, username, password, age, school_level):
    users_file = os.path.join(os.path.dirname(__file__), "users.csv")
    user_exists = False
    if os.path.exists(users_file):
        with open(users_file, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["username"] == username:
                    user_exists = True
                    break
    else:
        with open(users_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["full_name", "username", "password", "age", "school_level"])
            writer.writeheader()
    if user_exists:
        return False, "Username already exists"
    with open(users_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["full_name", "username", "password", "age", "school_level"])
        writer.writerow({
            "full_name": full_name,
            "username": username,
            "password": password,
            "age": age,
            "school_level": school_level
        })
    user_dir = os.path.join("users", username)
    os.makedirs(os.path.join(user_dir, "courses"), exist_ok=True)
    os.makedirs(os.path.join(user_dir, "scores"), exist_ok=True)
    return True, "User registered successfully"