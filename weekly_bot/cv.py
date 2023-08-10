from collections import defaultdict
import cv2
import os
import math
import numpy as np
from typing import DefaultDict, NamedTuple


class ItemImageCoord(NamedTuple):
    x: int
    y: int
    w: int
    h: int
    calc_tier: int


class NamedItemImage(NamedTuple):
    name: str
    image: np.ndarray


# https://stackoverflow.com/a/44659589
def image_resize(image, width=None, height=None, inter=cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation=inter)

    # return the resized image
    return resized


def load_images(
    directory: str, height: int
) -> DefaultDict[int, list[NamedItemImage]]:
    named_images = defaultdict(list)
    for file in os.listdir(directory):
        fname, _ = os.path.splitext(file)
        # Extract name_tier
        name, tier = fname.split("_")
        img = cv2.imread(os.path.join(directory, file), cv2.IMREAD_GRAYSCALE)
        resized_img = image_resize(img, height=height)

        # Adjust for 0-index
        named_images[int(tier) - 1].append(
            NamedItemImage(name=name, image=resized_img)
        )

    return named_images


def get_white_contours(img):
    imghsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # Set upper and lower bounds of HSV.
    lower_white = np.array([0, 0, 168])
    upper_white = np.array([172, 111, 255])
    # Create mask and only take pixels where white.
    mask = cv2.inRange(imghsv, lower_white, upper_white)
    output = cv2.bitwise_and(img, img, mask=mask)
    # Convert to grayscale and threshold to get binary image.
    imgray = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(imgray, 127, 255, 0)
    # Extract all external contours.
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    return contours


def get_valid_contours(contours, exp_tier_height: int):
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        # Ignore smaller contours
        if h < 35 or w < 35:
            continue
        # Ignore contours on left side. i.e. dice.
        if x < 30:
            continue
        yield ItemImageCoord(x, y, w, h, math.floor(y / exp_tier_height))


def main():
    base_img = cv2.imread("./data/weekly.jpg")
    contours = get_white_contours(base_img)
    exp_tier_height = base_img.shape[0] / 6
    valid_item_coords: list[ItemImageCoord] = list(
        get_valid_contours(contours, exp_tier_height)
    )

    pets = load_images("./output/pets", height=120)
    max_h = 0
    max_w = 0
    for icon in (item for _, items in pets.items() for item in items):
        if icon.image.shape[0] > max_h:
            max_h = icon.image.shape[0]
        if icon.image.shape[1] > max_w:
            max_w = icon.image.shape[1]

    found_pets = set()

    # O(num_slices) ~ 74
    gray_img = cv2.cvtColor(base_img, cv2.COLOR_BGR2GRAY)
    for coord in valid_item_coords:
        # Ensure image slice always greater than template
        img_slice = gray_img[
            coord.y : coord.y + coord.h, coord.x : coord.x + coord.w
        ]
        img_slice = image_resize(img_slice, height=120)

        # O(num_images at tier)
        best_num_matches = ("", 0)
        for template in pets[coord.calc_tier]:
            # https://www.analyticsvidhya.com/blog/2019/10/detailed-guide-powerful-sift-technique-image-matching-python/
            sift = cv2.SIFT_create()
            _, descriptors_1 = sift.detectAndCompute(img_slice, None)
            _, descriptors_2 = sift.detectAndCompute(template.image, None)
            bf = cv2.BFMatcher(cv2.NORM_L1, crossCheck=True)

            matches = bf.match(descriptors_1, descriptors_2)
            # Use number of matches as predictor of
            num_matches = len(matches)
            if num_matches >= best_num_matches[1]:
                best_num_matches = (template.name, num_matches)

        print(best_num_matches)
        cv2.imshow("", img_slice)
        cv2.waitKey(0)

    print(len(found_pets))
    print(found_pets)


if __name__ == "__main__":
    raise SystemExit(main())
