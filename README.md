# Super Auto Pets Fandom Weekly Bot
Update weekly page so consistent record of pets each week.
* WIP

Relies on [`SuperAutoTest`](https://github.com/koisland/SuperAutoTest), a database for Super Auto Pets.

### Pipeline
1. Invoke pipeline on weekly basis.
    * Best to do serverless with Lambda?
    * Runtime: ~2 min
    * Total space: ~3 MB
2. Extract images from Fandom wiki.
    * This requires knowning the names of each item. Hence, the need to use `saptest`.
        * May cause issue as cannot use both Rust and Python as cv libraries in Rust are not well-documented and easy to use.
        * Stick with a static list of names in `data/` retrieved with `saptest` for now.
3. Extract weekly image of most recently posted on [r/superautopets](https://www.reddit.com/r/superautopets/).
4. Determine date range from weekly post.
5. Downscale extracted images.
6. Find best match on pets in image with OpenCV.
    * Find dice first and use as starting position.
    * For each dice...
        * Move across scanning with ? x ? kernel.
        * Update if matching pet found?
        * Once empty blue space of ? length of pixels found set state of extractor for items.
        * Update if matching foods found?.
        * On end of image, continue to next dice.
7. Use created Fandom credentials to login into bot account.
8. Navigate to weekly page if exists, otherwise create.
9. Fill in wiki page with information.
10. Comment changes and general summary of pets.
