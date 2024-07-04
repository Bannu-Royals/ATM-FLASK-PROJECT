from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATA_FILE = "accounts.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    else:
        return {
            "1234": {"pin": "1111", "balance": 0, "transactions": []},
            "5678": {"pin": "2222", "balance": 0, "transactions": []},
            "9012": {"pin": "3333", "balance": 0, "transactions": []}
        }

def save_data(accounts):
    with open(DATA_FILE, "w") as file:
        json.dump(accounts, file, indent=4)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        card_number = request.form['card_number']
        pin = request.form['pin']
        accounts = load_data()
        if card_number in accounts and accounts[card_number]['pin'] == pin:
            session['card_number'] = card_number
            return redirect(url_for('main_menu'))
        else:
            flash("Invalid card number or PIN")
    return render_template('login.html')

@app.route('/main_menu')
def main_menu():
    if 'card_number' not in session:
        return redirect(url_for('login'))
    return render_template('main_menu.html')

@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if 'card_number' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        amount = float(request.form['amount'])
        accounts = load_data()
        card_number = session['card_number']
        accounts[card_number]['balance'] += amount
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        accounts[card_number]['transactions'].append(f"{timestamp} - Deposited ${amount:.2f}")
        save_data(accounts)
        flash(f"Deposited ${amount:.2f}. New balance: ${accounts[card_number]['balance']:.2f}")
        return redirect(url_for('main_menu'))
    return render_template('deposit.html')

@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if 'card_number' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        amount = float(request.form['amount'])
        accounts = load_data()
        card_number = session['card_number']
        if amount <= 0:
            flash("Please enter a positive amount")
        elif amount > accounts[card_number]['balance']:
            flash("Insufficient funds")
        else:
            accounts[card_number]['balance'] -= amount
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            accounts[card_number]['transactions'].append(f"{timestamp} - Withdrew ${amount:.2f}")
            save_data(accounts)
            flash(f"Withdrew ${amount:.2f}. New balance: ${accounts[card_number]['balance']:.2f}")
        return redirect(url_for('main_menu'))
    return render_template('withdraw.html')

@app.route('/balance')
def balance():
    if 'card_number' not in session:
        return redirect(url_for('login'))
    accounts = load_data()
    balance = accounts[session['card_number']]['balance']
    return render_template('balance.html', balance=balance)

@app.route('/transactions')
def transactions():
    if 'card_number' not in session:
        return redirect(url_for('login'))
    accounts = load_data()
    transactions = accounts[session['card_number']]['transactions']
    return render_template('transactions.html', transactions=transactions)

@app.route('/logout')
def logout():
    session.pop('card_number', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
