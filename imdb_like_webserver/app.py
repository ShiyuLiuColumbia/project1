#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python app.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
from __future__ import print_function
import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
import sys
# from forms import RegistrationForm, LoginForm

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

# XXX: The Database URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# For your convenience, we already set it to the class database

# Use the DB credentials you received by e-mail
DB_USER = "ho2271"
DB_PASSWORD = "d1d6s4ad"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"

# This line creates a database engine that knows how to connect to the URI above
engine = create_engine(DATABASEURI)

# Here we create a test table and insert some values in it
engine.execute("""DROP TABLE IF EXISTS users;""")

engine.execute("""CREATE TABLE users (
  id SERIAL PRIMARY KEY ,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);""")

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass

# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def home():
	"""
	request is a special object that Flask provides to access web request information:

	request.method:   "GET" or "POST"
	request.form:     if the browser submitted a form, this contains the data in the form
	request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

	See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
	"""

	# DEBUG: this is debugging code to see what request looks like
 	print(request.args)

  # return render_template("index.html", **context)
	return render_template("home.html")


#This is the movie-index page
@app.route('/movies')
def movie_index():
  cmd = 'SELECT * FROM movie limit 10'
  movies = g.conn.execute(text(cmd))
  print(type(movies), file=sys.stderr)
  return render_template("./movies/index.html", movies = movies)


#This is the movie-show page
@app.route('/movies/<int:id>')
def movie_show(id):
  cmd = 'SELECT movie.mov_id, movie.name AS mov_name, movie.language, movie.runtime, movie.release_date, genre.name AS genre_name,  act.cast_id, act.role, mov_cast.name AS cast_name, mov_cast.gender  FROM movie, belong_to, mov_cast, act, genre WHERE movie.mov_id = :name  AND movie.mov_id = act.mov_id AND belong_to.mov_id = movie.mov_id AND act.cast_id = mov_cast.cast_id AND genre.genre_id = belong_to.genre_id'
  selected_movie = g.conn.execute(text(cmd), name=id).fetchone()
  print(type(selected_movie), file=sys.stderr)

  return render_template("./movies/show.html", selected_movie = selected_movie)

# This is the search path
@app.route('/search',methods=['POST'])
def search():
	return redirect('/')

# add ratings or movies into database
@app.route('/add', methods=['GET','POST'])
def add():
	if request.method == 'GET':
		pass

	if request.method == 'POST':
		if "new_rate" in request.form:
			mov_id = request.form.get('mov_id')
			user_id = request.form.get('user_id')
			grade = request.form.get('grade')
			review = request.form.get('review')
			
			print(mov_id, user_id, grade, review)

			cmd = 'INSERT INTO rate(mov_id, user_id, grade, review) VALUES (:name1), (:name2), (:name3), (:name4);'
			#g.conn.execute(text(cmd), name1 = mov_id, name2 = user_id, name3=grade, name4=review)
		
		elif "new_movie" in request.form:
			name = request.form.get('name')
			mov_id = request.form.get('mov_id')
			language = request.form.get('language')
			runtime = request.form.get('runtime')
			release_date = request.form.get('release_date')
			revenue = request.form.get('revenue')

			print(name, mov_id, language, runtime, release_date, revenue)

			cmd = 'INSERT INTO movie(name, mov_id, language, runtime, release_date, revenue) VALUES (:name1), (:name2), (:name3), (:name4), (:name5), (:name6);'
			#g.conn.execute(text(cmd), name1 = name, name2 = mov_id, name3=language, name4=runtime, name5=release_date, name6=revenue)
		else:
			print("DID NOT GET THE FORM VALUE")
	return render_template("/add.html")

#This is the login and register using flask-wtf 
# @app.route("/register", methods=['GET', 'POST'])
# def register():
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         flash('Account created for {}!'.format(form.username.data), 'success')
#         return redirect(url_for('movie_index'))
#     return render_template('register.html', title='Register', form=form)


# @app.route("/login", methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         if form.email.data == 'admin@blog.com' and form.password.data == 'password':
#             flash('You have been logged in!', 'success')
#             return redirect(url_for('movie_index'))
#         else:
#             flash('Login Unsuccessful. Please check username and password', 'danger')
#     return render_template('login.html', title='Login', form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
      username = request.form['username']
      password = request.form['password']
      error = None

      if not username:
          error = 'Username is required.'
      elif not password:
          error = 'Password is required.'

      elif g.conn.execute(
          text('SELECT id FROM users WHERE username = :name'), name = username
      ).fetchone() is not None:
          error = 'User {} is already registered.'.format(username)

      if error is None:
          g.conn.execute(
              text('INSERT INTO users (username, password) VALUES (:name1, :name2)'),
              name1=username, name2=generate_password_hash(password)
          )
          flash('User {} successfully registered.'.format(username),'success')
          return redirect(url_for('login'))

      flash(error,'danger')

  return render_template('register.html', title='Login')


@app.route("/login", methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = g.conn.execute(
            text('SELECT * FROM users WHERE username = :name'), name=username
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('movie_index'))

        flash(error,'danger')

    return render_template('login.html',title='Login')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('movie_index'))


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8112, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=True, threaded=threaded)


  run()
