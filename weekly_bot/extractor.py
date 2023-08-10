import os
import sys
import json
import logging
import requests
from typing import NamedTuple

logging.basicConfig(format="%(asctime)s - %(message)s", stream=sys.stderr)

OUTPUT_FOLDER = "./output"
OUTPUT_FOOD_FOLDER = os.path.join(OUTPUT_FOLDER, "foods")
OUTPUT_PET_FOLDER = os.path.join(OUTPUT_FOLDER, "pets")
ENDPT = "https://saptest.fly.dev/db"


class ImageRequest(NamedTuple):
    base_endpt: str
    output_dir: str


def download_image(img_url: str, output_file: str):
    resp = requests.get(img_url, stream=True)
    # https://stackoverflow.com/questions/13137817/how-to-download-image-using-requests
    if resp.ok:
        with open(output_file, "wb") as img_file:
            for chunk in resp:
                img_file.write(chunk)


def extract_imgs() -> int:
    """
    Extract images from the SAP Fandom wiki.

    :returns: 0 on success
    """
    os.makedirs(OUTPUT_FOOD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_PET_FOLDER, exist_ok=True)

    item_img_requests = [
        ImageRequest(base_endpt=f"{ENDPT}/pets", output_dir=OUTPUT_PET_FOLDER),
        ImageRequest(
            base_endpt=f"{ENDPT}/foods", output_dir=OUTPUT_FOOD_FOLDER
        ),
    ]

    for req in item_img_requests:
        resp = requests.get(req.base_endpt)

        if resp.ok:
            items = json.loads(resp.text)
            for item in items:
                name = item["name"]
                tier = item["tier"]
                if isinstance(name, dict):
                    name = name["Custom"]

                output_img_file = os.path.join(
                    req.output_dir, f"{name}_{tier}.png"
                )
                if os.path.exists(output_img_file):
                    continue

                try:
                    download_image(item["img_url"], output_img_file)
                except Exception:
                    logging.error(f"Missing image url for {name}")
                    continue

    return 0
