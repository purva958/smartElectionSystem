from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
import random
import subprocess
from twilio.rest import Client
import hashlib

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For session management

import mysql.connector

db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',  # or 'Harshita-Parmar' or your IP address
    'database': 'vote'
}

try:
    conn = mysql.connector.connect(**db_config)
    print("Connected to MySQL")
except mysql.connector.Error as err:
    print(f"Error: {err}")


# Twilio configuration
account_sid = 'AC398781fc1258fb9856fcec452a5ef520'
auth_token = '07d26bb893a5d5311c832534a9eff788'
twilio_phone_number = '+15305085793'

@app.route('/fetch_phone', methods=['GET'])
def fetch_phone():
    aadhaar_number = request.args.get('aadhaar')

    if not aadhaar_number:
        return jsonify({'error': 'Aadhaar number is required'}), 400

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        query = "SELECT phone_number FROM add_data WHERE aadhaar_number = %s"
        cursor.execute(query, (aadhaar_number,))
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            return jsonify({'phone_number': result[0]})  # This returns the phone number if found
        else:
            return jsonify({'phone_number': ''})  # No phone number found

    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500


def generate_voter_id():
    return str(random.randint(100000, 999999))

def send_otp(mobile_number, unique_voter_id):
    client = Client(account_sid, auth_token)
    message = f"Your VoterID is {unique_voter_id}. It is valid for 10 minutes."
    
    try:
        message_response = client.messages.create(
            body=message,
            from_=twilio_phone_number,
            to=mobile_number
        )
        print(f"VoterID sent successfully to {mobile_number}, Message SID: {message_response.sid}")
    except Exception as e:
        print(f"Failed to send OTP: {e}")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        aadhaar = request.form.get('aadhaar')
        voter_id = request.form.get('voterId')
        password = request.form.get('password')

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Retrieve the hashed password from the login table
        cursor.execute('''
            SELECT password FROM login 
            WHERE aadhaar_number = %s AND voter_id = %s
        ''', (aadhaar, voter_id))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result and result[0] == hash_password(password):
            session['aadhaar'] = aadhaar  # Store Aadhaar in session
            return redirect(url_for('options'))
        else:
            return "Invalid login credentials, please try again."

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    cursor = None  # Initialize cursor to None
    conn = None  # Initialize conn to None
    if request.method == 'POST':
        name = request.form['name']
        fathers_name = request.form['fatherName']
        dob = request.form['dob']
        aadhaar = request.form['aadhaar']
        phone = request.form['phone']
        address = request.form['address']
        city = request.form['city']
        pincode = request.form['pincode']
        password = request.form['password']

        try:
            
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
           
        #    #cursor.execute('SELECT phone_number FROM add_data WHERE aadhaar_number = %s', (aadhaar,))
        #     result = cursor.fetchone()

        #     if not result:
        #         return render_template('register.html', error_message="Aadhaar number not found in add_data.")

            phone_number = phone

            # Ensure phone number starts with '+91'
            if not phone_number.startswith('+91'):
                phone_number = '+91' + phone_number

            # Check if the Aadhaar number already exists in the register table
            cursor.execute('SELECT aadhaar_number FROM register WHERE aadhaar_number = %s', (aadhaar,))
            existing_user = cursor.fetchone()

            if not existing_user:
                cursor.execute(''' 
                    INSERT INTO register (name, fathers_name, dob, aadhaar_number, phone_number, address, city, pin_code, password) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (name, fathers_name, dob, aadhaar, phone_number, address, city, pincode, hash_password(password)))

                # Generate a unique voter ID
                unique_voter_id = generate_voter_id()

                # Send the generated voter ID to the phone number using Twilio
                send_otp(phone_number, unique_voter_id)

                # Insert Aadhaar number, voter ID, and hashed password into the login table
                cursor.execute(''' 
                    INSERT INTO login (aadhaar_number, voter_id, password) 
                    VALUES (%s, %s, %s)
                ''', (aadhaar, unique_voter_id, hash_password(password)))

                # Commit the transaction and close the connection
                conn.commit()

                return redirect(url_for('login'))  # Redirect to the login page

            else:
                return render_template('register.html', error_message="User with this Aadhaar number already exists.")

        except mysql.connector.Error as err:
            return f"Error: {err}", 500
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template('register.html')


@app.route('/mysql_login', methods=['GET', 'POST'])
def mysql_login():
    error = None
    
    if request.method == 'POST':
        hostname = request.form['hostname'] or 'localhost'
        password = request.form['password']
        
        try:
            db_config['host'] = hostname
            db_config['password'] = password
            
            # Attempt to connect to MySQL
            conn = mysql.connector.connect(**db_config)
            conn.close()
            
            session['db_config'] = db_config
            return redirect(url_for('access'))  # Redirect to access page

        except mysql.connector.Error as err:
            error = f"Could not connect to MySQL: {err}"

    return render_template('mysql_login.html', error=error)

@app.route('/access')
def access():
    return render_template('access.html')


@app.route('/admin')
def admin_page():
    """Admin page."""
    if 'db_config' not in session:
        return redirect(url_for('mysql_login'))  # Redirect to MySQL login page if not logged in
    
    return render_template('admin.html')  # Load admin page if logged in

@app.route('/vote')
def options():
    return render_template('', faces_added=session.get('faces_added', False), 
                           data_trained=session.get('data_trained', False))

@app.route('/add_faces', methods=['POST'])
def add_faces():
    aadhaar_number = request.form.get('aadhar')
    voter_id = request.form.get('voterId')
    password = request.form.get('password')
    action = request.form.get('action')

    if not aadhaar_number or not voter_id or not password:
        return "Please provide all required fields.", 400

    try:
        if action == "add_faces":
            subprocess.run(["python", "add_faces.py", aadhaar_number], check=True)
            session['faces_added'] = True
            return redirect(url_for('login'))
        elif action == "give_vote":
            return redirect(url_for('give_vote'))
    except Exception as e:
        return f"Error occurred: {e}", 500

@app.route('/give_vote')
def give_vote():
    subprocess.run(["python", "give_vote.py"])
    return render_template('home.html')
    

@app.route('/add_data')
def add_data_page():
    return render_template('add_data.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
