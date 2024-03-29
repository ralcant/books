import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f) #good format
    next(reader) #skips the first line (is not actual data)
    for isbn, title, author, year in reader:
        #print(type(isbn), type(title), type(author), type(year))
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)", {"isbn":isbn, "title": title, "author": author, "year": year})
    db.commit()
    print(reader)
if __name__ == "__main__":
    main()