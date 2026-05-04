import json
import sys
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parent_dir))
from config import DATASET_DIR

dataset_path = Path(".")
objects = []

for subcategory_dir in dataset_path.iterdir():
    if not subcategory_dir.is_dir():
        continue
    
    subcategory = subcategory_dir.name  # indoor and outdoor
    
    for category_dir in subcategory_dir.iterdir():
        if not category_dir.is_dir():
            continue
        
        category = category_dir.name  # armchair, chair, ...
        
        for i in range(1, 11):  # from 1 to 10 since there are only 10 variations for each object
            obj = {
                "id": f"{category}_{subcategory}_{i}",
                "category": category,
                "subcategory": subcategory,
                "description_file": str(DATASET_DIR / subcategory / category / f"txt{i}.txt"),
                "code_file": str(DATASET_DIR / subcategory / category / f"code{i}.py"),
                "image_file": str(DATASET_DIR / subcategory / category / f"image{i}.png")
            }
            objects.append(obj)

output = {"dataset_version": "1.0", "objects": objects}

with open("dataset.json", "w") as f:
    json.dump(output, f, indent=2)

    