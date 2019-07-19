from flask import Flask, render_template, request, redirect, url_for, g, jsonify
import os
import base64

import sqlite3

DATABASE = '.data/shortcuts.db'
app = Flask(__name__)

##############################################################################
#                BOILERPLATE CODE (you can essentially ignore this)          #
##############################################################################

def get_db():
    """Boilerplate code to open a database
    connection with SQLite3 and Flask.
    Note that `g` is imported from the
    `flask` module."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = make_dicts
    return db

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

@app.teardown_appcontext
def close_connection(exception):
    """Boilerplate code: function called each time 
    the request is over."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
        
##############################################################################
#                APPLICATION CODE (read from this point!)                    #
##############################################################################
        
def shortcut_to_dict(key, url):
  return {
    "key": key,
    "url": url,
    "shortcut": url_for('redir', key=key, _external=True)
  }
        
@app.route("/")
def hello():
  return render_template('index.html')
 
def insert_url(url):
  find = False
  
  db = get_db()
  cur = db.cursor()
  
  while not find:
    try: 
      key = base64.urlsafe_b64encode(os.urandom(3)).decode()
      cur.execute("INSERT INTO shortcuts VALUES (?, ?)", (key, url))
      find = True
    except sqlite3.IntegrityError:
      # The insertion failed because an integrity error, that means
      # the `key` is already used in th DB (recall that `key` has 
      # `PRIMARY KEY` as constraint).
      #
      # So we do not set `find` to True and repeat until we found a 
      # non-used key
      pass
    
  db.commit()
  
  return key

@app.route("/new-shortcut/", methods=["POST"])
def new_shortcut():
  try:
    url = request.json['url']
  except KeyError:
    return jsonify({ "error": 'Missing "url" parameter!'}), 400

  if not url.startswith('http'):
    url = "http://" + url

  key = insert_url(url)
  return jsonify(shortcut_to_dict(key, url)), 201 # 201 is the HTTP code for "created"
  

@app.route("/view-shortcut/<key>")
def view_shortcut(key):
  db = get_db()
  cur = db.cursor()
  
  cur.execute("SELECT url FROM shortcuts WHERE key=?", (key,))
  res = cur.fetchone()
  if res is None:
    return jsonify({ "error": 'No url associated with the key ' + key + '.'}), 404
    
  return jsonify(shortcut_to_dict(key, res['url']))
  
@app.route("/search/")
def search():
  query = request.args.get('q', "")
  db = get_db()
  cur = db.cursor()
  
  # see this StackOverflow answer for explanations:
  # https://stackoverflow.com/questions/3105249
  cur.execute("SELECT key, url FROM shortcuts WHERE url LIKE ?", ('%' + query + '%',))
  matches = cur.fetchall()
  return render_template('search.html', matches=matches, query=query)
  
  
@app.route("/r/<key>")
def redir(key):
  db = get_db()
  cur = db.cursor()
  
  cur.execute("SELECT url FROM shortcuts WHERE key=?", (key,))
  res = cur.fetchone()
  if res is None:
    return render_template('error.html', message='No url associated with the key ' + key + '.'), 404
  return redirect(res['url'])


  


if __name__ == '__main__':
    app.run(debug=True)
