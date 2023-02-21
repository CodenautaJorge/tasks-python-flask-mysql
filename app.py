from flask import Flask, render_template, request, session, redirect, url_for
import config
from flask_mysqldb import MySQL
from datetime import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = config.HEX_SEC_KEY
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB

mysql = MySQL(app)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
    user = cur.fetchone()
    cur.close()

    if user is not None:
        session['email'] = email
        session['name'] = user[1]
        session['surnames'] = user[2]

        return redirect(url_for('tasks'))
    else:
        return render_template('index.html', message="Las credenciales no son correctas")

@app.route('/tasks', methods=['GET'])
def tasks():
    email = session['email']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tasks WHERE email = %s", [email])
    tasks = cur.fetchall()

    insertObject = []
    columnNames = [column[0] for column in cur.description]
    for record in tasks:
        insertObject.append(dict(zip(columnNames, record)))
    cur.close()

    return render_template('tasks.html', tasks = insertObject)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/new-task', methods=['POST'])
def newTask():
    title = request.form['title']
    description = request.form['description']
    email = session['email']
    d = datetime.now()
    dateTask = d.strftime("%Y-%m-%d $H:%M:%S")

    if title and description and email:
        cur = mysql.connection.cursor()
        sql = "INSERT INTO tasks (email, title, description, date_task) VALUES (%s, %s, %s, %s)"
        data = (email, title, description, dateTask)
        cur.execute(sql, data)
        mysql.connection.commit()
    return redirect(url_for('tasks'))

@app.route('/new-user', methods=['POST'])
def newUser():
    name = request.form['name']
    surnames = request.form['surnames']
    email = request.form['email']
    password = request.form['password']

    if name and surnames and email and password:
        cur = mysql.connection.cursor()
        sql = "INSERT INTO users (name, surnames, email, password) VALUES (%s, %s, %s, %s)"
        data = (name, surnames, email, password)
        cur.execute(sql, data)
        mysql.connection.commit()
    return redirect(url_for('tasks'))

@app.route("/delete-task", methods=["POST"])
def deleteTask():
    cur = mysql.connection.cursor()
    id = request.form['id']
    sql = "DELETE FROM tasks WHERE id = %s"
    data = (id,)
    cur.execute(sql, data)
    mysql.connection.commit()
    return redirect(url_for('tasks'))




if __name__ == '__main__':
    app.run(debug=True)