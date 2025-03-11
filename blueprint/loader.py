from typing import List, Tuple
import os
import random
import csv


BLUEPRINT_PATH = "blueprints"
FILE_EXTENSION = ".csv"

def load_blueprint(name: str) -> List[Tuple[int, int, int, int, str]]:
    with open(os.path.join(BLUEPRINT_PATH, name + FILE_EXTENSION), 'r', newline='') as file:
        return [(int(row[0]), int(row[1]), int(row[2]), int(row[3]), row[4]) for row in csv.reader(file)]

def list_blueprints() -> List[str]:
    return [file.strip(FILE_EXTENSION) for file in os.listdir(BLUEPRINT_PATH) if file.endswith(FILE_EXTENSION)]

def select_random_blueprint() -> str:
    return random.choice(list_blueprints())
