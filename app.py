from flask import Flask, redirect, render_template, request, session, flash, get_flashed_messages, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()  # Lataa ympäristömuuttujat .env-tiedostosta

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///chargingtrackerdb"
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
db = SQLAlchemy(app)


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
        
        sql = 'SELECT * FROM users WHERE username = :username;'
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
            return render_template('register.html')

        try:
            sql = 'SELECT id FROM users WHERE username = :username;'
            logger.info(f"Executing SQL query: {sql} with username = {username}")
            result = db.session.execute(text(sql), {'username': username})
            existing_user = result.fetchone()

            if existing_user:
                logger.warning(f"Attempt to register duplicate username: {username}")
                flash('User id exists already in the database.', 'error')
            else:
                password_hash = generate_password_hash(password)
                sql = 'INSERT INTO users (username, password_hash) VALUES (:username, :password_hash);'
                logger.info(f"Executing SQL query: {sql} for username = {username}")
                db.session.execute(text(sql), {'username': username, 'password_hash': password_hash})
                db.session.commit()
                logger.info(f"User {username} successfully registered.")
                flash('Successfully registered to ChargingTracker.', 'success')
                return redirect('/login')
        except Exception as e:
            logger.error(f"Error during registration for username {username}: {e}", exc_info=True)
            flash('An error occurred during registration.', 'error')

    return render_template('register.html')



@app.route('/vehicles')
def vehicles():
    print("Vehicles-reitti")
    if 'username' not in session:
        return redirect(url_for('login'))

    sql = 'SELECT id FROM users WHERE username = :username;'
    result = db.session.execute(text(sql), {'username': session['username']})
    user = result.fetchone()

    if user:
        sql = 'SELECT id, vehicle_name, battery_size, last_mileage FROM vehicle WHERE user_id = :user_id;'
        result = db.session.execute(text(sql), {'user_id': user.id})
        vehicles = result.fetchall()
        print(vehicles)  # Tulosta ajoneuvojen lista konsoliin debuggausta varten
        return render_template('vehicles.html', vehicles=vehicles)
    else:
        return redirect(url_for('login'))

@app.route('/add_vehicle', methods=['POST'])
def add_vehicle():
    if 'username' not in session:
        return redirect(url_for('login'))

    sql = 'SELECT id FROM users WHERE username = :username;'
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

    # Hae käyttäjän ajoneuvot
    vehicles_sql = 'SELECT id, vehicle_name FROM vehicle WHERE user_id = :user_id;'
    vehicles = db.session.execute(text(vehicles_sql), {'user_id': user_id}).fetchall()

    # Hae käyttäjän latausasemat
    stations_sql = 'SELECT id, station_name FROM charging_station WHERE user_id = :user_id;'
    charging_stations = db.session.execute(text(stations_sql), {'user_id': user_id}).fetchall()

    # Hae käyttäjän kohteet
    destinations_sql = 'SELECT id, destination_name FROM destinations WHERE user_id = :user_id;'
    destinations = db.session.execute(text(destinations_sql), {'user_id': user_id}).fetchall()

    # Hae käyttäjän lataustapahtumat ja liitä mukaan ajoneuvon nimi, latausaseman nimi ja kohde
    charging_sql = '''
    SELECT c.id, c.start_time, c.end_time, c.charged_energy, c.cost, c.mileage, v.vehicle_name, cs.station_name, d.destination_name
    FROM charging c
    JOIN vehicle v ON c.vehicle = v.id
    JOIN charging_station cs ON c.charging_station_id = cs.id
    LEFT JOIN destinations d ON c.destination_id = d.id
    WHERE c.user_id = :user_id;
    '''
    chargings = db.session.execute(text(charging_sql), {'user_id': user_id}).fetchall()

    return render_template('charging.html', vehicles=vehicles, charging_stations=charging_stations, destinations=destinations, chargings=chargings)


@app.route('/add_charging', methods=['POST'])
def add_charging():
    if 'username' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    charging_station_id = request.form.get('charging_station')
    vehicle_id = request.form.get('vehicle')
    start_time = request.form['start_time']
    end_time = request.form['end_time']
    charged_energy = request.form['charged_energy']
    cost = request.form['cost']
    mileage = request.form['mileage']
    destination_id = request.form.get('destination')  # Lisätty

    sql = '''
    INSERT INTO charging (user_id, charging_station_id, vehicle, start_time, end_time, charged_energy, cost, mileage, destination_id) 
    VALUES (:user_id, :charging_station_id, :vehicle_id, :start_time, :end_time, :charged_energy, :cost, :mileage, :destination_id);
    '''
    db.session.execute(text(sql), {
        'user_id': user_id,
        'charging_station_id': charging_station_id,
        'vehicle_id': vehicle_id,
        'start_time': start_time,
        'end_time': end_time,
        'charged_energy': charged_energy,
        'cost': cost,
        'mileage': mileage,
        'destination_id': destination_id
    })
    db.session.commit()

    flash('Charging event added successfully!')
    return redirect(url_for('chargings'))

@app.route('/edit_charging/<int:id>', methods=['GET', 'POST'])
def edit_charging(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    if request.method == 'POST':
        charging_station_id = request.form['charging_station_id']
        vehicle_id = request.form['vehicle_id']
        start_time = datetime.strptime(request.form['start_time'], '%Y-%m-%dT%H:%M')
        end_time = datetime.strptime(request.form['end_time'], '%Y-%m-%dT%H:%M')
        charged_energy = request.form['charged_energy']
        cost = request.form['cost']
        mileage = request.form['mileage']
        destination_id = request.form['destination_id']

        sql = '''
        UPDATE charging
        SET charging_station_id = :charging_station_id, vehicle = :vehicle_id, start_time = :start_time, 
            end_time = :end_time, charged_energy = :charged_energy, cost = :cost, mileage = :mileage, 
            destination_id = :destination_id
        WHERE id = :id AND user_id = :user_id;
        '''
        db.session.execute(text(sql), {
            'id': id,
            'user_id': user_id,
            'charging_station_id': charging_station_id,
            'vehicle_id': vehicle_id,
            'start_time': start_time,
            'end_time': end_time,
            'charged_energy': charged_energy,
            'cost': cost,
            'mileage': mileage,
            'destination_id': destination_id
        })
        db.session.commit()

        flash('Charging event updated successfully!')
        return redirect(url_for('chargings'))
    else:
        # Haetaan muokattavan lataustapahtuman tiedot
        charging_info_sql = 'SELECT * FROM charging WHERE id = :id AND user_id = :user_id;'
        charging_info_result = db.session.execute(text(charging_info_sql), {'id': id, 'user_id': user_id}).fetchone()

        if not charging_info_result:
            flash('Charging event not found.', 'error')
            return redirect(url_for('chargings'))

        charging_info = charging_info_result._asdict()

        # Haetaan latausasemat, ajoneuvot ja kohteet
        charging_stations_sql = 'SELECT id, station_name FROM charging_station WHERE user_id = :user_id;'
        charging_stations = db.session.execute(text(charging_stations_sql), {'user_id': user_id}).fetchall()

        vehicles_sql = 'SELECT id, vehicle_name FROM vehicle WHERE user_id = :user_id;'
        vehicles = db.session.execute(text(vehicles_sql), {'user_id': user_id}).fetchall()

        destinations_sql = 'SELECT id, destination_name FROM destinations WHERE user_id = :user_id;'
        destinations = db.session.execute(text(destinations_sql), {'user_id': user_id}).fetchall()

        # Valmistele tiedot lomakkeelle
        charging_info['start_time_str'] = charging_info['start_time'].strftime('%Y-%m-%dT%H:%M')
        charging_info['end_time_str'] = charging_info['end_time'].strftime('%Y-%m-%dT%H:%M')

        return render_template('edit_charging.html', charging=charging_info, vehicles=vehicles, charging_stations=charging_stations, destinations=destinations)
    
@app.route('/delete_charging/<int:id>', methods=['POST'])
def delete_charging(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    # Tarkista ensin, onko kyseinen lataustapahtuma olemassa
    sql = 'SELECT * FROM charging WHERE id = :id AND user_id = :user_id;'
    result = db.session.execute(text(sql), {'id': id, 'user_id': user_id})
    charging = result.fetchone()

    if not charging:
        flash('Charging event not found.', 'error')
        return redirect(url_for('chargings'))

    # Jos lataustapahtuma on olemassa, poista se
    delete_sql = 'DELETE FROM charging WHERE id = :id;'
    db.session.execute(text(delete_sql), {'id': id})
    db.session.commit()

    flash('Charging event deleted successfully!')
    return redirect(url_for('chargings'))


@app.route('/destinations', methods=['GET', 'POST'])
def destinations():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        destination_name = request.form['name']  # Ota huomioon lomakkeen kentän nimi
        user_id = session['user_id']
        sql = text('INSERT INTO destinations (destination_name, user_id) VALUES (:destination_name, :user_id)')
        db.session.execute(sql, {'destination_name': destination_name, 'user_id': user_id})
        db.session.commit()
        flash('Destination added successfully!')

    sql = text('SELECT * FROM destinations WHERE user_id = :user_id')
    destinations = db.session.execute(sql, {'user_id': session['user_id']}).fetchall()
    return render_template('destinations.html', destinations=destinations)

@app.route('/add_destination', methods=['POST'])
def add_destination():
    if 'username' not in session:
        return redirect(url_for('login'))

    destination_name = request.form['name']
    user_id = session['user_id']
    sql = text('INSERT INTO destinations (destination_name, user_id) VALUES (:destination_name, :user_id)')
    db.session.execute(sql, {'destination_name': destination_name, 'user_id': user_id})
    db.session.commit()
    flash('Destination added successfully!')
    return redirect('/destinations')


@app.route('/edit_destination/<int:id>', methods=['GET', 'POST'])
def edit_destination(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        destination_name = request.form['name']
        sql = text('UPDATE destinations SET destination_name = :destination_name WHERE id = :id')
        db.session.execute(sql, {'destination_name': destination_name, 'id': id})
        db.session.commit()
        flash('Destination updated successfully!')
        return redirect('/destinations')

    # Haetaan muokattava kohde tietokannasta
    sql = text('SELECT * FROM destinations WHERE id = :id')
    result = db.session.execute(sql, {'id': id})
    destination = result.fetchone()

    if destination:
        return render_template('edit_destination.html', destination=destination)
    else:

        flash('Destination not found.', 'error')
        return redirect('/destinations')


@app.route('/delete_destination/<int:id>', methods=['GET', 'POST'])
def delete_destination(id):

    if 'username' not in session:
        return redirect(url_for('login'))

    # Esimerkki: Tarkista, onko kohdetta viitattu muissa tauluissa, esimerkiksi 'charging'
    # Tämä vaihe riippuu sovelluksesi rakenteesta ja siitä, miten kohteita käytetään.
    # Jos esimerkiksi kohteisiin viitataan toisesta taulusta, sinun tulee suorittaa vastaava tarkistus.
    # sql = 'SELECT COUNT(*) FROM charging WHERE destination_id = :destination_id;'
    # result = db.session.execute(text(sql), {'destination_id': id})
    # count = result.fetchone()[0]
    # if count > 0:
    #     flash('Cannot delete destination as it is referenced in other records.', 'error')
    #     return redirect(url_for('destinations'))

    # Jos kohteeseen ei viitata tai viittausten käsittelyn jälkeen, poista kohde
    sql = 'DELETE FROM destinations WHERE id = :id;'
    db.session.execute(text(sql), {'id': id})
    db.session.commit()

    flash('Destination successfully deleted from the database.')
    return redirect(url_for('destinations'))


import logging
from logging.handlers import RotatingFileHandler

# Määritä logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
logger.addHandler(handler)


if __name__ == '__main__':
    app.run(debug=True)
