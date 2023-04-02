from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import pickle
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB, GaussianNB
from sklearn.model_selection import train_test_split

import Model.py

app = Flask(__name__, template_folder = 'templates')
app.secret_key = 'vk'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'sa'
app.config['MYSQL_PASSWORD'] = 'hellonewworld'
app.config['MYSQL_DB'] = 'MLT_CIA_Temp'

with open('model.pkl', 'rb') as f:
    model = pickle.load(f)


@app.route('/')
def home():
    return render_template('login.html')


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = mysql.connector.connect(**app.config)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session['username'] = user[1]
            return redirect(url_for('success'))
        else:
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')


# Success
@app.route('/success', methods=['GET', 'POST'])
def success():
    cv = CountVectorizer()

    if 'username' in session:
        if request.method == 'POST':
            message = request.form['message']
            data = [message]
            vect = cv.transform(data).toarray()

            result = model.predict([vect])[0]

            return redirect(url_for('result', result=result))

        return render_template('input.html')

    return redirect(url_for('home'))


# Results
@app.route('/result/<result>')
def result(result):
    if 'username' in session:
        return render_template('result.html', result=result)

    return redirect(url_for('home'))


# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
