# db movie to imdb & db book to goodreads

Retrieve your rating details from db, and mark them on imdb or goodreads.

Forked from https://github.com/fisheepx/douban-to-imdb

## dbmovie_to_csv.py
Changes:
- save csv for each page, instead of saving after retrieving all the data.
- add more contents to the csv file.
- use config file instead of program params
- collect 想看/正在看 list.

## csv_to_imdb.py
Changes:
- add mark in reserved order.

## dbbook_to_csv.py
Use webdriver to retrieve rated book details.