from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Create DB and table
def init_db():
    conn = sqlite3.connect('contacts.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            address TEXT,
            email TEXT UNIQUE NOT NULL,
            phone TEXT UNIQUE NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Home - Show contacts
@app.route('/')
def index():
    conn = sqlite3.connect('contacts.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contacts")
    contacts = cursor.fetchall()
    conn.close()
    return render_template('index.html', contacts=contacts)

# Add Contact
@app.route('/add', methods=['POST'])
def add_contact():
    first = request.form['first_name']
    last = request.form['last_name']
    address = request.form['address']
    email = request.form['email']
    phone = request.form['phone']

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        flash("Invalid email format!", "error")
        return redirect(url_for('index'))

    if not phone.isdigit() or len(phone) != 10:
        flash("Phone must be 10 digits!", "error")
        return redirect(url_for('index'))

    try:
        conn = sqlite3.connect('contacts.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO contacts (first_name, last_name, address, email, phone) VALUES (?, ?, ?, ?, ?)",
                       (first, last, address, email, phone))
        conn.commit()
    except sqlite3.IntegrityError:
        flash("Duplicate Email or Phone!", "error")
    finally:
        conn.close()

    return redirect(url_for('index'))

# Delete Contact
@app.route('/delete/<int:id>')
def delete_contact(id):
    conn = sqlite3.connect('contacts.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contacts WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Update Contact
@app.route('/edit/<int:id>')
def edit_contact(id):
    conn = sqlite3.connect('contacts.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contacts WHERE id=?", (id,))
    contact = cursor.fetchone()
    conn.close()
    return render_template('update.html', contact=contact)

@app.route('/update/<int:id>', methods=['POST'])
def update_contact(id):
    first = request.form['first_name']
    last = request.form['last_name']
    address = request.form['address']
    email = request.form['email']
    phone = request.form['phone']

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        flash("Invalid email format!", "error")
        return redirect(url_for('edit_contact', id=id))

    if not phone.isdigit() or len(phone) != 10:
        flash("Phone must be 10 digits!", "error")
        return redirect(url_for('edit_contact', id=id))

    try:
        conn = sqlite3.connect('contacts.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE contacts 
            SET first_name=?, last_name=?, address=?, email=?, phone=? 
            WHERE id=?
        ''', (first, last, address, email, phone, id))
        conn.commit()
    except sqlite3.IntegrityError:
        flash("Duplicate Email or Phone!", "error")
    finally:
        conn.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
