from src.data_loader import RavelryAPI
import os
import json


def get_next_fname(base_fname="patterns", directory="./data/raw", ext="json"):
    if not os.path.exists(directory):
        os.makedirs(directory)

    i = 0
    while True:
        # format fname with incrementing number
        new_fname = f"{base_fname}_{i}.{ext}"
        full_path = os.path.join(directory, new_fname)

        if not os.path.exists(full_path):
            return full_path

        i += 1


def main():
    api = RavelryAPI()

    # categories to search
    categories = [
        "sweater", "socks", "hat", "shawl-wrap", "tops",
        "blanket", "scarf", "mittens", "cowl", "slippers"
    ]

    patterns = api.collect_patterns_by_category(categories=categories, max_per_category=100)

    fname = get_next_fname()

    with open(fname, "w") as f:
        json.dump(patterns, f, indent=2)

    print(f"Collected {len(patterns)} patterns")


if __name__ == "__main__":
    main()
