import sqlite3
from flask import Flask, request, render_template, jsonify
from datetime import datetime
from flask_cors import CORS
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import matplotlib.dates
from flask import redirect, url_for

app = Flask(__name__, static_url_path="/static", static_folder="static")
CORS(app)

@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/graph')
def graph():
    con = sqlite3.connect('mydatabase.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM dezemer")
    rows = cur.fetchall()

    x = [datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S') for row in rows]
    y = [row[0] for row in rows]

    dates = matplotlib.dates.date2num(x)

    # plt.xticks([0, 1],[x[0],x[-1]])
    plt.plot_date(x, y)
    plt.xlabel('String Value')
    plt.ylabel('Double Value')
    plt.title('Dezemer')

    # Create a BytesIO object
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue()).decode('ascii')
    return render_template('graph.html', figdata_png=figdata_png)

@app.route('/')
def index():

    return render_template('index.html')

@app.route('/display')
def display():
    con = sqlite3.connect('mydatabase.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM dezemer")
    rows = cur.fetchall()
    return render_template('display.html', rows=rows)

@app.route('/data/<data>', methods=['POST', 'GET'])
def handle_post_request(data):

    # save current time
    current_time = datetime.now()
    time_string = current_time.strftime("%Y-%m-%d %H:%M:%S")

    # post request
    #data = request.form['double_value']

    # connect sqlite3 database
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS dezemer (meritev REAL, cas VARCHAR(255))")
    c.execute("INSERT INTO dezemer (meritev, cas) VALUES (?, ?)", (data, time_string))
    conn.commit()
    conn.close()
    return time_string

@app.route('/eksperimenti', methods=['GET', 'POST'])
def eksperimenti():

    conn = sqlite3.connect('database.db')

    conn.execute('CREATE TABLE IF NOT EXISTS eksperimenti (name TEXT, lokacija TEXT, datum TEXT, izvajalec TEXT)')
    conn.close()

    if request.method == 'POST':
        try:
            name = request.form['name']
            print(name)
            lokacija = request.form['lokacija']
            print(lokacija)
            datum = request.form['datum']
            print(datum)
            izvajalec = request.form['izvajalec']
            print(izvajalec)

            with sqlite3.connect('database.db') as conn:
                cur = conn.cursor()
                cur.execute("INSERT INTO eksperimenti (name, lokacija, datum, izvajalec) VALUES (?,?,?,?)", (name, lokacija, datum, izvajalec))

                conn.commit()

        except:
            conn.rollback()

        finally:
            conn.close()
    
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM eksperimenti")
    # print(cur.fetchall())
    rows = cur.fetchall()

    for row in rows:
        print(row[0])

    return render_template("eksperimenti.html",experiments = rows)

@app.route('/vaja')
def vaja():
    return render_template('vaja.html')

@app.route("/eksperiment_podrobnosti/<ime_eksperimenta>")
def eksperiment_podrobnosti(ime_eksperimenta):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT * FROM eksperimenti WHERE name=?", (ime_eksperimenta,))
    rows = c.fetchall()

    for row in rows:
        table_name = row[0].replace(" ", "_")
        c.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (meritev REAL, cas VARCHAR(255))")
        print('tabela je ustvarjena')

    conn.commit()
    c.close()

    return render_template("eksperiment_podrobnosti.html", experiments=rows)




if __name__ == '__main__':
    app.run(debug=True, host = '0.0.0.0')

