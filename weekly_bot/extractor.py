import re
import os
import sys
import tarfile
import requests
from typing import List, Tuple


PET_NAME_FILE = "./data/pet_names.csv"
FOOD_NAME_FILE = "./data/food_names.csv"
OUTPUT_FOLDER = "./output"
OUTPUT_FOOD_FOLDER = os.path.join(OUTPUT_FOLDER, "foods")
OUTPUT_PET_FOLDER = os.path.join(OUTPUT_FOLDER, "pets")
BASE_FANDOM_FILE_URL = "https://superautopets.fandom.com/wiki/File:"
BASE_FANDOM_IMG_URL = ""


# Naming exceptions.
NAME_EXCEPTIONS = {"Popcorns": "Popcorn", "Hammershark": "Hammerhead_Shark"}


def read_item_names() -> Tuple[List[str], List[str]]:
    """
    Read item names from a text csv. Hard-coded.

    :returns: Food and pet names as tuple.
    """
    with open(FOOD_NAME_FILE, "r") as food_file, open(
        PET_NAME_FILE, "r"
    ) as pet_file:
        foods = [food.strip() for food in food_file.readlines()]
        pets = [name.strip() for name in pet_file.readlines()]
        return (foods, pets)


def save_imgs(item_names: List[str], output_dir: str) -> None:
    """
    Save images from a given list of Super Auto Pets item names.
    Then outputs files to the specified directory.

    :param item_names: List of SAP item names
        * Foods or pets
    :param output_dir: Output directory.

    :returns: None
    """
    for item in item_names:
        if item in NAME_EXCEPTIONS:
            item = NAME_EXCEPTIONS[item]

        # Remove any spaces.
        item = item.replace(" ", "_")
        # Currently, new icons are suffixed with '_Icon'.
        fd_item_filename = f"{item}_Icon.png"
        output_file = os.path.join(output_dir, fd_item_filename)
        # Continue if file exists.
        if os.path.exists(output_file):
            continue

        mdata_url = f"{BASE_FANDOM_FILE_URL}{fd_item_filename}"
        res_mdata_page = requests.get(mdata_url)

        # Match on the url.
        rgx_img_url = (
            r"https://static.wikia.nocookie.net/superautopets/images/\w{1}/\w{2}/"
            + fd_item_filename
            + r"/revision/latest"
        )
        match = re.search(rgx_img_url, res_mdata_page.text)
        # print(food, match.group(0))

        # If whole match, get file at the image url.
        if match is not None and (res_img_file := match.group(0)):
            res = requests.get(res_img_file, stream=True)
            # https://stackoverflow.com/questions/13137817/how-to-download-image-using-requests
            if res.status_code == 200:
                with open(output_file, "wb") as img_file:
                    for chunk in res:
                        img_file.write(chunk)
            else:
                print(f"No result on {res_img_file}", file=sys.stderr)
        else:
            print(f"Cannot find url with {rgx_img_url}", file=sys.stderr)


def extract_imgs() -> int:
    """
    Extract images from the SAP Fandom wiki.

    :returns: 0 on success
    """
    foods, pets = read_item_names()

    os.makedirs(OUTPUT_FOOD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_PET_FOLDER, exist_ok=True)

    save_imgs(foods, OUTPUT_FOOD_FOLDER)
    save_imgs(pets, OUTPUT_PET_FOLDER)

    # Create tarball.
    with tarfile.open(f"{OUTPUT_FOLDER}.tar.gz", "w:gz") as tar:
        tar.add(OUTPUT_FOLDER, arcname=os.path.basename(OUTPUT_FOLDER))

    return 0
