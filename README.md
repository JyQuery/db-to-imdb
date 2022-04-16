# db

retrieve your rating details from db.

forked from https://github.com/fisheepx/douban-to-imdb


Changes:
- save csv for each page, instead of saving after retrieving all the data.
- add more contents to the csv file. 
- add exception handling if ip is banned by the service provider.
- add mark in reserved order on imdb
- default imdb star is 2 times of the db star. If there is no star on db, mark it 1 star on imdb.