import os
import requests

from flask import Flask, session, render_template, request, redirect, url_for, jsonify, abort
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import datetime

# app = Flask(__name__, static_url_path="")
app = Flask(__name__)

# NEED TO DO FOR USING THE DATABASE ON A LOCALHOST
#export DATABASE_URL=postgres://fcmowaitpbarwh:ba1dfca6b5497a0d9cd86f042a6ccc884b293ae7396056e6ac405305f1c777b1@ec2-174-129-41-127.compute-1.amazonaws.com:5432/d2n8h31dn021tr
#export FLASK_APP=application.py
#export FLASK_DEBUG=1
#export KEY= VfgPRTWa6Pl64HlBB8S68w

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
#session["user_id"]= "yay"

# db.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username VARCHAR NOT NULL, password VARCHAR NOT NULL)")

@app.route('/api/<string:isbn>')
def search_api_isbn(isbn):
    book = db.execute("SELECT isbn, title, author, year FROM books WHERE isbn=:isbn", {"isbn": isbn}).fetchone()
    if book is None:
        #return 404 response
        abort(404)
    isbn, title, author, year = book
    return jsonify(
        isbn= isbn,
        title= title,
        author= author,
        year= year,
    )



@app.route('/general_search/<string:text>/<string:search_type>')
def general_search(text, search_type):
    if search_type == "isbn":
        return redirect(url_for('search_isbn', isbn= text))
    elif search_type == "author":
        return redirect(url_for('search_author', author= text))
    elif search_type == "title":
        return redirect(url_for('search_title', title= text))
    elif search_type == "year":
        return redirect(url_for('search_year', year= text))
    else:
        return render_template('error.html', message= f"You didn't provide a valid search_type: {search_type}")

#for search from the text input
@app.route('/search/<string:search_type>', methods=["POST", "GET"])
def search(search_type):
    now = datetime.now()
    date = now.strftime("%B %d, %Y")+ " at "+ now.strftime("%H:%M:%S") 
    if search_type == "isbn":
        isbn = request.form.get("isbn")

        print('bool:', isbn =="style.css")
        if isbn != "":
            sql_command = "INSERT INTO history_search (username, text_searched, type, date) VALUES (:username, :text_searched, :type, :date);"
            new_values = {"username": session["username"], "text_searched": isbn, "type": "isbn", "date": date}
            db.execute(sql_command, new_values)
            db.commit()
            return redirect(url_for('search_isbn', isbn= isbn))
    if search_type == "author":
        author = request.form.get("author")
        print(author)
        if author != "":
            sql_command = "INSERT INTO history_search (username, text_searched, type, date) VALUES (:username, :text_searched, :type, :date);"
            new_values = {"username": session["username"], "text_searched": author, "type": "author", "date": date}
            db.execute(sql_command, new_values)
            db.commit()
            return redirect(url_for('search_author', author= author))
    if search_type == "title":
        title = request.form.get("title")
        if title != "":
            sql_command = "INSERT INTO history_search (username, text_searched, type, date) VALUES (:username, :text_searched, :type, :date);"
            new_values = {"username": session["username"], "text_searched": title, "type": "title", "date": date}
            db.execute(sql_command, new_values)
            db.commit()
            return redirect(url_for('search_title', title= title))
    if search_type == "year":
        year = request.form.get("year")
        if year != "":
            sql_command = "INSERT INTO history_search (username, text_searched, type, date) VALUES (:username, :text_searched, :type, :date);"
            new_values = {"username": session["username"], "text_searched": year, "type": "year", "date": date}
            db.execute(sql_command, new_values)
            db.commit()
            return redirect(url_for('search_year', year=year))
    else:
        return render_template("error.html", message = "Nothing provided")

    # isbn = request.form.get("isbn")
    # author= request.form.get("author")
    # title= request.form.get("title")
    # year = request.form.get("year")
    # if isbn is not None and isbn != "":
    #     return redirect(url_for('search_isbn', isbn= isbn))
    # elif author is not None and author!= "":
    #     return redirect(url_for('search_author', author= author))
    # elif title is not None and title != "":
    #     return redirect(url_for('search_title', title= title))
    # elif year is not None and year != "":
    #     return redirect(url_for('search_year', year=year))
    # else:
    #     return render_template("error.html", message = "Nothing provided")

@app.route('/book/<string:isbn>')
def book(isbn):
    print('isbn=', isbn)
    isbn, title, author, year = db.execute("SELECT isbn, title, author, year FROM books WHERE isbn=:isbn", {"isbn": isbn}).fetchone()
    KEY= "VfgPRTWa6Pl64HlBB8S68w"
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": KEY, "isbns": isbn})
    work_ratings_count = res.json()["books"][0]["work_ratings_count"]
    average_rating = res.json()["books"][0]["average_rating"]
    return render_template("book.html", author=author, title= title, isbn=isbn, year=year, work_ratings_count= work_ratings_count, average_rating= average_rating)

# @app.route('/books')
# def books():



@app.route('/isbn/<string:isbn>')
def search_isbn(isbn):
    #print(request.form.get("isbn"), request.form.get("author"), request.form.get("title"))
    #isbn = request.form.get("isbn")
    '''
    Updating search database
    '''
    print('isbn=', isbn)
    rule = f"%{isbn}%"
    books = db.execute("SELECT title, author, year, isbn FROM books WHERE isbn LIKE :rule", {"rule": rule}).fetchall()
    if books is None:
        return render_template("error.html", message= "There are no such books with a similar isbn!")
    #isbn, title, author, year = book
    print('books in search_isbn=',books)
    return render_template("books.html", books= books)
    # return redirect(url_for('books'))
    #return render_template("book.html", books= books)#author=author, title= title, isbn=isbn, year=year)

@app.route('/author/<string:author>')
def search_author(author):
    #print(request.form.get("isbn"), request.form.get("author"), request.form.get("title"))
    #isbn = request.form.get("isbn")

    print('author=', author)
    rule = f"%{author}%"
    books = db.execute("SELECT title, author, year, isbn FROM books WHERE author LIKE :rule", {"rule": rule}).fetchall()
    if books is None:
        return render_template("error.html", message= "There are no such books with a similar author!")
    #isbn, title, author, year = book
    print('books in search_author=',books)
    return render_template("books.html", books= books)
    #return redirect(url_for('index', books= books))    
    #return render_template("book.html", books= books) #author=author, title= title, isbn=isbn, year=year)

@app.route('/title/<string:title>')
def search_title(title):
    #print(request.form.get("isbn"), request.form.get("author"), request.form.get("title"))
    #isbn = request.form.get("isbn")

    print('title=', title)
    rule= f"%{title}%"
    books = db.execute("SELECT title, author, year, isbn FROM books WHERE title LIKE :rule", {"rule": rule}).fetchall()
    if books is None:
        return render_template("error.html", message= "There are no such books with a similar title!")
    #isbn, title, author, year = book
    print('books in search_title=',books)
    return render_template("books.html", books= books)

    #return redirect(url_for('index', books= books))        
    #return render_template("book.html", author=author, title= title, isbn=isbn, year=year  )

@app.route('/year/<string:year>')
def search_year(year):
    #print(request.form.get("isbn"), request.form.get("author"), request.form.get("title"))
    #isbn = request.form.get("isbn")

    rule= f"%{year}%"
    books = db.execute("SELECT title, author, year, isbn FROM books WHERE year LIKE :rule", {"rule": rule}).fetchall()
    if books is None:
        return render_template("error.html", message= "There are no such books with a similar year of publication!")
    #isbn, title, author, year = book
    print('books in search_title=',books)
    return render_template("books.html", books= books)



#@app.route("")
@app.route("/dashrd")
def first():
    return render_template("dashboard.html")
@app.route('/history')
def history():
    searchs = db.execute("SELECT text_searched, type, date FROM history_search WHERE username=:username ORDER BY id DESC",{"username": session["username"]})
    return render_template("search.html", searchs=searchs)


#log in a user
@app.route('/login', methods=["POST", "GET"]) 
def login():
    #if "user_id" 
    #session["user_id"] = 1
    if request.method== "POST":
        username= request.form.get("username")
        password= request.form.get("password")
        if db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username": username, "password": password}).rowcount ==0:
            #not valid user
            return render_template("error.html", message="Wrong username and/or password!") #TODO: RENDER A PAGE THAT SHOWS AN OPTION FOR SIGNING UP (OR GOING BACK)
        #valid user
        print(f"Signing in user with username {username} and with password {password}")
        db.commit() #useless?
        session["username"] = username
        # books = db.execute("SELECT title FROM books").fetchall()
        # session["books"] = books
        return redirect(url_for('index'))
        #return render_template("user.html", username= username, password=password)
    else:
        print (db.execute("SELECT * FROM users WHERE username= :username", {"username": session["username"]}))
        return 

@app.route('/logout')
def logout():
    #remove the username from the session if it is there
    session.pop('username', None)
    return redirect(url_for('index'))

#TRY TO SIGN UP A USER
@app.route('/signup', methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        #print(session["user_id"])
        print(request.form.get("username"),request.form.get("password"))
        username = request.form.get("username")
        password = request.form.get("password")
        print(f"trying to insert user with username {username} and password {password}")
        if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount >=1:
            print("same username :(")
            return render_template("error.html", message="Sorry, but this username was taken!")
        if len(username) == 0:
            return render_template("error.html", message="No username provided :/")
        if len(password) <=7:
            #too short
            return render_template("error.html", message="Sorry, password to short. Each password should be at least 8 characters long")
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", {"username": username, "password": password})
        print("success!")
        db.commit()
        return render_template("success.html")
    else:
        return 
@app.route("/", methods=["GET", "POST"])
def index(): #IMPORTANT!: This is where the application usually lives 
    if "username" not in session: 
        return render_template("login.html")
        #return send_from_directory('./static','login.html')
        #return app.send_static_file('login.html')
        #return url_for('static', filename="login.html") 
    else:
        #if already logged in
        username= session["username"]

        password = db.execute("SELECT password FROM users where username=:username", {"username": username}).fetchone()[0] #fectchone returns it as a tuple
        # books = session["books"]
        #user is of the form (id, username, password)
        return render_template("user.html", username=username, password=password) #need to also pass the password

