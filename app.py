from flask import Flask, redirect, render_template, request, session, flash, url_for
from os import getenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
#from dotenv import load_dotenv

#load_dotenv()
app = Flask(__name__)
app.secret_key = getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URL')



from flask import Flask, redirect, render_template, request, session, flash, get_flashed_messages, url_for

with app.app_context():
    db = SQLAlchemy(app)
    db.create_all()

@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html')
    else:
        return render_template('welcome.html') 

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        sql = 'SELECT * FROM "user" WHERE username = :username;'
        result = db.session.execute(text(sql), {'username': username})
        user = result.fetchone()
        
        if user and check_password_hash(user.password_hash, password):
            session['username'] = username
            session['user_id'] = user.id  # Siirrä tämä rivi tähän
            flash('Succesfully logged into ChargingTracker.', 'success')
            return redirect('/')
        else:
            flash('User id or password were incorrect.', 'error')

    return render_template('login.html', messages=get_flashed_messages())
   
@app.route('/logout')
def logout():
    if 'username' in session:
        del session['username']
        flash('Succesfully logged out from ChargingTracker.', 'success')
    return redirect('/login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords are not identical.', 'error')
        else:
            sql = 'SELECT id FROM "user" WHERE username = :username;'
            result = db.session.execute(text(sql), {'username': username})
            existing_user = result.fetchone()
            
            if existing_user:
                flash('User id exists already in the database.', 'error')
            else:
                password_hash = generate_password_hash(password)
                sql = 'INSERT INTO "user" (username, password_hash) VALUES (:username, :password_hash);'
                db.session.execute(text(sql), {'username': username, 'password_hash': password_hash})
                db.session.commit()
                flash('Succesfully registered to ChargingTracker.', 'success')
                flash('You can now login into system.', 'success')
                return redirect('/login')

    return render_template('register.html', messages=get_flashed_messages())    

@app.route('/vehicles')
def vehicles():
    if 'username' not in session:
        return redirect(url_for('login'))

    sql = 'SELECT id FROM "user" WHERE username = :username;'
    result = db.session.execute(text(sql), {'username': session['username']})
    user = result.fetchone()

    if user:
        sql = 'SELECT id, vehicle_name, battery_size, last_mileage FROM vehicle WHERE user_id = :user_id;'
        result = db.session.execute(text(sql), {'user_id': user.id})
        vehicles = result.fetchall()
        return render_template('vehicles.html', vehicles=vehicles)
    else:
        return redirect(url_for('login'))

@app.route('/add_vehicle', methods=['POST'])
def add_vehicle():
    if 'username' not in session:
        return redirect(url_for('login'))

    sql = 'SELECT id FROM "user" WHERE username = :username;'
    result = db.session.execute(text(sql), {'username': session['username']})
    user = result.fetchone()

    if user:
        vehicle_name = request.form['vehicle_name']
        battery_size = request.form['battery_size']

        sql = '''
        INSERT INTO vehicle (vehicle_name, battery_size, user_id) 
        VALUES (:vehicle_name, :battery_size, :user_id);
        '''
        db.session.execute(text(sql), {'vehicle_name': vehicle_name, 'battery_size': battery_size, 'user_id': user.id})
        db.session.commit()

        flash('Car was succesfully added to database.')
        return redirect(url_for('vehicles'))
    else:
        return redirect(url_for('login'))

@app.route('/edit_vehicle/<int:id>', methods=['GET', 'POST'])
def edit_vehicle(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    sql = 'SELECT * FROM vehicle WHERE id = :id;'
    result = db.session.execute(text(sql), {'id': id})
    vehicle = result.fetchone()

    if vehicle and request.method == 'POST':
        vehicle_name = request.form['vehicle_name']
        battery_size = request.form['battery_size']

        sql = '''
        UPDATE vehicle
        SET vehicle_name = :vehicle_name, battery_size = :battery_size
        WHERE id = :id;
        '''
        db.session.execute(text(sql), {'vehicle_name': vehicle_name, 'battery_size': battery_size, 'id': id})
        db.session.commit()

        flash('Car data succesfully updated.')
        return redirect(url_for('vehicles'))

    return render_template('edit_vehicle.html', vehicle=vehicle)

@app.route('/delete_vehicle/<int:id>')
def delete_vehicle(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    # First, check if this vehicle is referenced in the charging table
    sql = 'SELECT COUNT(*) FROM charging WHERE vehicle = :vehicle_id;'
    result = db.session.execute(text(sql), {'vehicle_id': id})
    count = result.fetchone()[0]

    if count > 0:
        # If the vehicle is referenced in charging, flash a message and redirect
        flash('Cannot delete vehicle as it is referenced in charging records.', 'error')
        return redirect(url_for('vehicles'))

    # If the vehicle is not referenced, proceed to delete
    sql = 'DELETE FROM vehicle WHERE id = :id;'
    db.session.execute(text(sql), {'id': id})
    db.session.commit()

    flash('Car successfully deleted from the database.')
    return redirect(url_for('vehicles'))

@app.route('/stations', methods=['GET', 'POST'])
def stations():
    if 'username' not in session:
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    sql = 'SELECT id, operator_name FROM operators WHERE user_id = :user_id;'
    result = db.session.execute(text(sql), {'user_id': user_id})
    user_operators = result.fetchall()

    if request.method == 'POST':
        station_data = {
            'station_name': request.form['station_name'],
            'streetname1': request.form['streetname1'],
            'streetname2': request.form['streetname2'],
            'zip': request.form['zip'],
            'city': request.form['city'],
            'country': request.form['country'],
            'operator_id': request.form['operator']
        }

        if not station_data['operator_id']:
            flash('Please select an operator.', 'error')
            return render_template('station.html', operators=user_operators, station_data=station_data)

        sql_insert = '''
        INSERT INTO charging_station (station_name, streetname1, streetname2, zip, city, country, operator, user_id) 
        VALUES (:station_name, :streetname1, :streetname2, :zip, :city, :country, :operator_id, :user_id);
        '''
        db.session.execute(text(sql_insert), {**station_data, 'user_id': user_id})
        db.session.commit()
        flash('Charging station added successfully!')
        return redirect(url_for('stations'))

    sql_select = 'SELECT * FROM charging_station WHERE user_id = :user_id;'
    all_stations = db.session.execute(text(sql_select), {'user_id': user_id}).fetchall()
    return render_template('station.html', stations=all_stations, operators=user_operators, station_data={})

@app.route('/edit_station/<int:id>', methods=['GET', 'POST'])
def edit_station(id):
    if request.method == 'POST':
        sql = '''
        UPDATE charging_station 
        SET station_name = :station_name, streetname1 = :streetname1, streetname2 = :streetname2, zip = :zip, city = :city, country = :country, operator = :operator 
        WHERE id = :id;
        '''
        db.session.execute(text(sql), {
            'station_name': request.form['station_name'],
            'streetname1': request.form['streetname1'],
            'streetname2': request.form['streetname2'],
            'zip': request.form['zip'],
            'city': request.form['city'],
            'country': request.form['country'],
            'operator': request.form['operator'],
            'id': id
        })
        db.session.commit()
        flash('Charging station updated successfully!')
        return redirect(url_for('stations'))

    sql = 'SELECT * FROM charging_station WHERE id = :id;'
    station = db.session.execute(text(sql), {'id': id}).fetchone()

    sql = 'SELECT * FROM operators;'
    operators = db.session.execute(text(sql)).fetchall()
    return render_template('edit_station.html', station=station, operators=operators)

@app.route('/delete_station/<int:id>', methods=['GET', 'POST'])
def delete_station(id):
    # First, retrieve the station name for the flash message
    station_sql = 'SELECT station_name FROM charging_station WHERE id = :id;'
    station_result = db.session.execute(text(station_sql), {'id': id})
    station_row = station_result.fetchone()

    if station_row is None:
        flash('Charging station not found.', 'error')
        return redirect(url_for('stations'))

    station_name = station_row[0]

    # Check if this charging station is referenced in the charging table
    sql = 'SELECT COUNT(*) FROM charging WHERE charging_station_id = :station_id;'
    result = db.session.execute(text(sql), {'station_id': id})
    count = result.fetchone()[0]

    if count > 0:
        # If the charging station is referenced in charging, flash a message and redirect
        flash(f'Cannot delete charging station {station_name} as it is referenced in charging records.', 'error')
        return redirect(url_for('stations'))

    # If the charging station is not referenced, proceed to delete
    sql = 'DELETE FROM charging_station WHERE id = :id;'
    db.session.execute(text(sql), {'id': id})
    db.session.commit()

    flash(f'Charging station {station_name} successfully deleted.')
    return redirect(url_for('stations'))

@app.route('/operators')
def operators():
    if 'username' not in session:
        return redirect(url_for('login'))

    sql = 'SELECT id, operator_name FROM operators WHERE user_id = :user_id;'
    result = db.session.execute(text(sql), {'user_id': session['user_id']})
    operators = result.fetchall()
    return render_template('operator.html', operators=operators)

@app.route('/add_operator', methods=['GET', 'POST'])
def add_operator():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Tarkista, että käyttäjä on kirjautunut sisään
    if 'user_id' in session:
        user_id = session['user_id']
    else:
        flash('You are not logged in.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        operator_name = request.form['operator_name']

        # Lisää operaattori tietokantaan
        sql = 'INSERT INTO operators (operator_name, user_id) VALUES (:operator_name, :user_id);'
        db.session.execute(text(sql), {'operator_name': operator_name, 'user_id': user_id})
        db.session.commit()
        flash('Operator added successfully!')
        return redirect(url_for('operators'))

    return render_template('add_operator.html')


@app.route('/edit_operator/<int:id>', methods=['GET', 'POST'])
def edit_operator(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    sql = 'SELECT * FROM operators WHERE id = :id;'
    result = db.session.execute(text(sql), {'id': id})
    operator = result.fetchone()

    if operator and request.method == 'POST':
        operator_name = request.form['operator_name']

        sql = '''
        UPDATE operators
        SET operator_name = :operator_name
        WHERE id = :id;
        '''
        db.session.execute(text(sql), {'operator_name': operator_name, 'id': id})
        db.session.commit()

        flash('Operator succesfully updated.')
        return redirect(url_for('operators'))

    return render_template('edit_operator.html', operator=operator)

@app.route('/delete_operator/<int:id>', methods=['GET', 'POST'])
def delete_operator(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    # Tarkista, että operaattori on olemassa ja kuuluuko se kirjautuneelle käyttäjälle
    user_id = session.get('user_id')
    sql = 'SELECT id FROM operators WHERE id = :id AND user_id = :user_id;'
    result = db.session.execute(text(sql), {'id': id, 'user_id': user_id})
    operator = result.fetchone()

    if not operator:
        flash('Operator not found or you are not authorized to delete this operator', 'error')
        return redirect(url_for('operators'))

    # Tarkista, onko operaattoriin viitattu muissa tauluissa (esimerkiksi charging_station-taulussa)
    check_sql = 'SELECT COUNT(*) FROM charging_station WHERE operator = :operator_id;'
    check_result = db.session.execute(text(check_sql), {'operator_id': id})
    count = check_result.fetchone()[0]

    if count > 0:
        flash('Cannot delete operator as it is referenced in other records.', 'error')
        return redirect(url_for('operators'))

    # Suoritetaan operaattorin poisto
    delete_sql = 'DELETE FROM operators WHERE id = :id;'
    db.session.execute(text(delete_sql), {'id': id})
    db.session.commit()

    flash('Operator successfully deleted!')
    return redirect(url_for('operators'))


@app.route('/chargings')
def chargings():
    if 'username' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    # Fetch user's vehicles
    vehicle_sql = 'SELECT id, vehicle_name FROM vehicle WHERE user_id = :user_id;'
    vehicle_result = db.session.execute(text(vehicle_sql), {'user_id': user_id})
    user_vehicles = [{'id': row[0], 'vehicle_name': row[1]} for row in vehicle_result]

    # Fetch user's charging stations
    station_sql = 'SELECT id, station_name FROM charging_station WHERE user_id = :user_id;'
    station_result = db.session.execute(text(station_sql), {'user_id': user_id})
    user_charging_stations = [{'id': row[0], 'station_name': row[1]} for row in station_result]

    # Fetch user's charging data with join to include vehicle and charging station names
    charging_sql = '''
    SELECT c.charging_id, c.start_time, c.end_time, c.charged_energy, c.cost, c.mileage,
           v.vehicle_name, cs.station_name
    FROM charging c
    LEFT JOIN vehicle v ON c.vehicle = v.id
    LEFT JOIN charging_station cs ON c.charging_station_id = cs.id
    WHERE c.user_id = :user_id;
    '''
    charging_result = db.session.execute(text(charging_sql), {'user_id': user_id})
    
    # Convert each row to a dictionary using _asdict()
    user_chargings = [row._asdict() for row in charging_result]

    return render_template('charging.html', chargings=user_chargings, vehicles=user_vehicles, charging_stations=user_charging_stations)


@app.route('/add_charging', methods=['POST'])
def add_charging():
    if 'username' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    # Retrieve the form data
    charging_station_id = request.form.get('charging_station')
    vehicle_id = request.form.get('vehicle')
    start_time = request.form['start_time']
    end_time = request.form['end_time']
    charged_energy = request.form['charged_energy']
    cost = request.form['cost']
    mileage = request.form['mileage']

    # Convert empty strings to None for integer fields
    charging_station_id = int(charging_station_id) if charging_station_id and charging_station_id.isdigit() else None
    vehicle_id = int(vehicle_id) if vehicle_id and vehicle_id.isdigit() else None

    # Prepare the SQL query for inserting the new charging data
    sql = '''
    INSERT INTO charging (user_id, charging_station_id, vehicle, start_time, end_time, charged_energy, cost, mileage) 
    VALUES (:user_id, :charging_station_id, :vehicle_id, :start_time, :end_time, :charged_energy, :cost, :mileage);
    '''
    db.session.execute(text(sql), {
        'user_id': user_id,
        'charging_station_id': charging_station_id,
        'vehicle_id': vehicle_id,
        'start_time': start_time,
        'end_time': end_time,
        'charged_energy': charged_energy,
        'cost': cost,
        'mileage': mileage
    })
    db.session.commit()

    flash('Charging data added successfully!')
    return redirect(url_for('chargings'))



@app.route('/edit_charging/<int:charging_id>', methods=['GET', 'POST'])
def edit_charging(charging_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    # Fetch the specific charging data
    charging_sql = 'SELECT * FROM charging WHERE charging_id = :charging_id AND user_id = :user_id;'
    charging_result = db.session.execute(text(charging_sql), {'charging_id': charging_id, 'user_id': user_id})
    charging_row = charging_result.fetchone()

    if charging_row is None:
        flash('Charging event not found.', 'error')
        return redirect(url_for('chargings'))

    charging = charging_row._asdict()
    charging['start_time_str'] = charging['start_time'].strftime('%Y-%m-%dT%H:%M')
    charging['end_time_str'] = charging['end_time'].strftime('%Y-%m-%dT%H:%M')

    # Fetch vehicles and charging stations for dropdowns
    vehicle_sql = 'SELECT id, vehicle_name FROM vehicle WHERE user_id = :user_id;'
    vehicle_result = db.session.execute(text(vehicle_sql), {'user_id': user_id})
    user_vehicles = [{'id': row[0], 'vehicle_name': row[1]} for row in vehicle_result]

    station_sql = 'SELECT id, station_name FROM charging_station WHERE user_id = :user_id;'
    station_result = db.session.execute(text(station_sql), {'user_id': user_id})
    user_charging_stations = [{'id': row[0], 'station_name': row[1]} for row in station_result]

    if request.method == 'POST':
        print("Form data received:", request.form)  # Printtaa lomaketiedot

        updated_data = {
            'charging_station_id': int(request.form['charging_station_id']),
            'start_time': datetime.strptime(request.form['start_time'], '%Y-%m-%dT%H:%M'),
            'end_time': datetime.strptime(request.form['end_time'], '%Y-%m-%dT%H:%M'),
            'charged_energy': int(request.form['charged_energy']),
            'cost': int(request.form['cost']),
            'vehicle': int(request.form['vehicle_id']),  # Tässä korjattu avain
            'mileage': int(request.form['mileage'])
        }

        print(f"Attempting to update with data: {updated_data}")  # Printtaa päivitetyt tiedot

        try:
            update_sql = '''
            UPDATE charging
            SET charging_station_id = :charging_station_id, start_time = :start_time, end_time = :end_time, 
                charged_energy = :charged_energy, cost = :cost, vehicle = :vehicle, mileage = :mileage
            WHERE charging_id = :charging_id AND user_id = :user_id;
            '''
            db.session.execute(text(update_sql), {**updated_data, 'charging_id': charging_id, 'user_id': user_id})
            db.session.commit()
            flash('Charging data updated successfully!')
        except Exception as e:
            print(f'Error updating charging data: {e}')  # Printtaa mahdolliset virheet
            flash(f'Error updating charging data: {e}', 'error')

        return redirect(url_for('chargings'))
    
    return render_template('edit_charging.html', charging=charging, vehicles=user_vehicles, charging_stations=user_charging_stations)



@app.route('/delete_charging/<int:charging_id>', methods=['POST'])
def delete_charging(charging_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    # Tarkista ensin, onko kyseinen lataustapahtuma olemassa
    sql = 'SELECT * FROM charging WHERE charging_id = :charging_id;'
    result = db.session.execute(text(sql), {'charging_id': charging_id})
    charging = result.fetchone()

    if not charging:
        flash('Charging data not found.', 'error')
        return redirect(url_for('chargings'))

    # Jos lataustapahtuma on olemassa, poista se
    delete_sql = 'DELETE FROM charging WHERE charging_id = :charging_id;'
    db.session.execute(text(delete_sql), {'charging_id': charging_id})
    db.session.commit()

    flash('Charging data deleted successfully!')
    return redirect(url_for('chargings'))


if __name__ == '__main__':
    app.run(debug=True)
