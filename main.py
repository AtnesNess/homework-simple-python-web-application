import random
import string
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments import highlight
from flask import Flask, request,g, redirect, url_for, render_template
import sqlite3
import os
from contextlib import closing

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
DATABASE = os.path.join(BASE_DIR, "paster.db")
DEBUG = True
SECRET_KEY = '12345678'
USERNAME = 'admin'
PASSWORD = 'qweqweqwe'

app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.route('/', methods=["GET", "POST"])
def create():
    if request.method == "POST":
        paste_sec = None
        while True:
            paste_sec = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(7))
            cur = g.db.execute("SELECT * FROM paste_table where id_sec='{}'".format(paste_sec))
            if len(cur.fetchall()) == 0:
                break
        paste = request.form["paste"]
        paste = paste.replace("'", "&#39;")
        lexer = request.form["lexer"]
        if "seen_delete" in request.form:
            seen_delete = 1
        else:
            seen_delete = 0

        ip = request.remote_addr

        g.db.execute("INSERT INTO paste_table (code, user_ip, lexer, seen_delete, id_sec) VALUES "
                     "('{}', '{}', '{}', {}, '{}' )".format(
            paste, ip, lexer, seen_delete, paste_sec
        ))
        g.db.commit()

        return redirect(url_for('show_paste', paste_sec=paste_sec))
    return render_template("create.html")


@app.route('/<paste_sec>')
def show_paste(paste_sec):
    cur = g.db.execute('select code, lexer, seen_delete, user_ip from paste_table where id_sec="{}"'.format(paste_sec))
    entries = [dict(code=row[0], lexer=row[1], seen_delete=row[2], user_ip=row[3]) for row in cur.fetchall()]
    if len(entries) == 0:
        return "Paste Not Found =("
    code = entries[0]['code'].replace("&#39;", "'")
    raw = code
    code = highlight(code, get_lexer_by_name(entries[0]['lexer']), HtmlFormatter())
    entries[0]['code'] = code
    if entries[0]['seen_delete'] == 1 and \
                    entries[0]['user_ip'] != str(request.remote_addr):

        g.db.execute('delete from paste_table where id_sec="{}"'.format(paste_sec))
        g.db.commit()
    return render_template("show.html", **entries[0], raw=raw)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
