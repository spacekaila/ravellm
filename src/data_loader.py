import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv
import json

# loads .env file with rav credentials
load_dotenv()


def find_all_key_instances(key_to_find, data_struct, val_remove=""):
    """Find all occurances of a specific key in nested dict/list.

    Parameters
    ----------
    key_to_find : any
        key to search for
    data_struct : dict/list
        dict or list to search
    val_remove : any, optional
        Val to remove from the list, by default None
    """
    if isinstance(data_struct, dict):
        for k, v in data_struct.items():
            if k == key_to_find and v != val_remove:
                yield v
            # Recursively search in nested dictionaries or lists
            if isinstance(v, (dict, list)):
                yield from find_all_key_instances(key_to_find, v, val_remove)
    elif isinstance(data_struct, list):
        for item in data_struct:
            # Recursively search in items within the list
            if isinstance(item, (dict, list)):
                yield from find_all_key_instances(key_to_find, item, val_remove)


class RavelryAPI:
    def __init__(self):
        self.username = os.getenv("RAVELRY_USERNAME")
        self.password = os.getenv("RAVELRY_PASSWORD")
        self.base_url = "https://api.ravelry.com"
        self.auth = HTTPBasicAuth(self.username, self.password)

    def search_patterns(self, query=None, filters={}, page=1, page_size=100):
        """Search for patterns

        Parameters
        ----------
        query : str
            query to send
        page : int, optional
            result page to retrieve, by default 1
        page_size : int, optional
            items per page, maximum accepted is 100, by default 100
        """

        endpoint = f"{self.base_url}/patterns/search.json"
        params = {
            "query": query,
            "page": page,
            "page_size": page_size,
            "craft": "knitting"
        }

        # send a request to the ravelry API
        response = requests.get(endpoint, auth=self.auth, params=(params | filters))
        # raises HTTPError if status code indicates one, otherwise does nothing
        response.raise_for_status()
        # returns json response body
        return response.json()

    def get_pattern_details(self, pattern_id: int):
        """Get detailed info for a specific pattern

        Parameters
        ----------
        pattern_id : int
            pattern ID number
        """

        endpoint = f"{self.base_url}/patterns/{pattern_id}.json"
        response = requests.get(endpoint, auth=self.auth)
        response.raise_for_status()
        return response.json()

    def get_pattern_details_multi(self, pattern_id_str):
        """Get detailed info for multiple patterns

        Parameters
        ----------
        pattern_id_str : str
            formatted as id1+id2+id3+idn
        """
        endpoint = f"{self.base_url}/patterns.json?ids={pattern_id_str}"
        response = requests.get(endpoint, auth=self.auth)
        response.raise_for_status()
        return response.json()

    def collect_patterns_by_category(self, categories, filters={}, query=None, max_per_category=50):
        """Collect patterns across multiple categories

        Parameters
        ----------
        categories : list
            List of categories to search
        max_per_category : int, optional
            Max number of patterns per category, by default 50
        """

        all_patterns = []
        ids = []

        for category in categories:
            print(f"Browsing patterns for: {category}")
            filters["pc"] = category
            pattern_search = self.search_patterns(query=query, filters=filters, page_size=max_per_category)
            pattern_list = pattern_search.get("patterns", [])
            cat_ids = [p["id"] for p in pattern_list]
            ids.extend(cat_ids)
        # we don't want to fetch the same pattern more than once
        ids = list(set(ids))
        pattern_id_str = "+".join([str(x) for x in ids])
        print("Fetching pattern information")
        pattern_details = self.get_pattern_details_multi(pattern_id_str=pattern_id_str)
        patterns = pattern_details.get("patterns", {})

        for id, pattern in patterns.items():
            cat_list = list(set(find_all_key_instances("permalink", pattern["pattern_categories"], "categories")))
            pattern_data = {
                "id": pattern["id"],
                "name": pattern["name"],
                "designer": pattern.get("pattern_author", {}).get("name", "Unknown"),
                "difficulty": pattern.get("difficulty_average", 0),
                "yarn_weight": pattern.get("yarn_weight", {}).get("name", "Unknown"),
                "notes": pattern.get("notes", ""),
                "url": f"https://www.ravelry.com/patterns/library/{pattern.get("permalink", "")}",
                "category": " ".join(cat_list),
                "downloadable": pattern["downloadable"],
                "free": pattern["free"],
            }
            all_patterns.append(pattern_data)

        return all_patterns


def main():
    api = RavelryAPI()

    # Categories to search
    categories = [
        "sweater", "socks", "hat", "shawl-wrap", "tops",
        "blanket", "scarf", "mittens", "cowl", "slippers"
    ]

    patterns = api.collect_patterns_by_category(categories=categories, max_per_category=100)

    with open("data/raw/patterns.json", "w") as f:
        json.dump(patterns, f, indent=2)

    print(f"Collected {len(patterns)} patterns")


# Example usage
if __name__ == "__main__":
    main()
