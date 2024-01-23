from flask import Flask, redirect, render_template, request, session, flash, url_for
from os import getenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URL')

from flask import Flask, redirect, render_template, request, session, flash, get_flashed_messages, url_for

with app.app_context():
    db = SQLAlchemy(app)
    db.create_all()

class Vehicle(db.Model):
    __tablename__ = 'vehicle'
    id = db.Column(db.Integer, primary_key=True)
    vehicle_name = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    battery_size = db.Column(db.Integer)
    last_mileage = db.Column(db.Integer)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

class ChargingStation(db.Model):
    __tablename__ = 'charging_station'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    station_name = db.Column(db.String(50))
    streetname1 = db.Column(db.String(50))
    streetname2 = db.Column(db.String(50))
    zip = db.Column(db.String(20))
    city = db.Column(db.String(30))
    country = db.Column(db.String(30))
    operator = db.Column(db.Integer, db.ForeignKey('operators.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) 

class Operator(db.Model):
    __tablename__ = 'operators'
    id = db.Column(db.Integer, primary_key=True)
    operator_name = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Charging(db.Model):
    __tablename__ = 'charging'
    charging_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    charging_station_id = db.Column(db.Integer, db.ForeignKey('charging_station.id'))  # Päivitetty nimi
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    charged_energy = db.Column(db.Integer)
    cost = db.Column(db.Integer)
    vehicle = db.Column(db.Integer, db.ForeignKey('vehicle.id'))
    mileage = db.Column(db.Integer)

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
            existing_user = User.query.filter_by(username=username).first()
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

    sql = 'DELETE FROM vehicle WHERE id = :id;'
    db.session.execute(text(sql), {'id': id})
    db.session.commit()

    flash('Car successfully deleted from the database.')
    return redirect(url_for('vehicles'))

@app.route('/stations', methods=['GET', 'POST'])
def stations():
    if 'username' not in session:
        return redirect(url_for('login'))

    user_id = User.query.filter_by(username=session['username']).first().id
    user_operators = Operator.query.filter_by(user_id=user_id).all()
    all_stations = ChargingStation.query.filter(ChargingStation.operator.in_([operator.id for operator in user_operators])).all()
    station_data = {}

    if request.method == 'POST':
        station_data = {
            'station_name': request.form['station_name'],
            'streetname1': request.form['streetname1'],
            'streetname2': request.form['streetname2'],
            'zip_code': request.form['zip'],
            'city': request.form['city'],
            'country': request.form['country'],
            'operator_id': request.form['operator']
        }

        if not station_data['operator_id']:
            flash('Please select an operator.', 'error')
            return render_template('station.html', stations=all_stations, operators=user_operators, station_data=station_data)

        new_station = ChargingStation(
            station_name=station_data['station_name'],
            streetname1=station_data['streetname1'],
            streetname2=station_data['streetname2'],
            zip=station_data['zip_code'],
            city=station_data['city'],
            country=station_data['country'],
            operator=station_data['operator_id']
        )
        db.session.add(new_station)
        db.session.commit()
        flash('Charging station added successfully!')
        return redirect(url_for('stations'))

    return render_template('station.html', stations=all_stations, operators=user_operators, station_data=station_data)


@app.route('/edit_station/<int:id>', methods=['GET', 'POST'])
def edit_station(id):
    station = ChargingStation.query.get(id)
    operators = Operator.query.all() 
    if request.method == 'POST':
        station.station_name = request.form['station_name']
        station.streetname1 = request.form['streetname1']
        station.streetname2 = request.form['streetname2']
        station.zip = request.form['zip']
        station.city = request.form['city']
        station.country = request.form['country']
        station.operator = request.form['operator']

        db.session.commit()
        flash('Charging station updated successfully!')
        return redirect(url_for('stations'))

    return render_template('edit_station.html', station=station, operators=operators)

@app.route('/delete_station/<int:id>', methods=['GET', 'POST'])
def delete_station(id):
    station_to_delete = ChargingStation.query.get_or_404(id)
    db.session.delete(station_to_delete)
    db.session.commit()
    flash('Charging station successfully deleted.')
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

    sql = 'SELECT id FROM "user" WHERE username = :username;'
    result = db.session.execute(text(sql), {'username': session['username']})
    user = result.fetchone()

    if user and request.method == 'POST':
        operator_name = request.form['operator_name']
        new_operator = Operator(operator_name=operator_name, user_id=user.id)
        db.session.add(new_operator)
        db.session.commit()
        flash('Operator added successfully!')
        return redirect(url_for('operators'))

    return render_template('add_operator.html')

@app.route('/edit_operator/<int:id>', methods=['GET', 'POST'])
def edit_operator(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    operator = Operator.query.get(id)
    if operator and operator.user_id != User.query.filter_by(username=session['username']).first().id:
        flash('You are not authorized to edit this operator', 'error')
        return redirect(url_for('operators'))

    if request.method == 'POST':
        operator.operator_name = request.form['operator_name']
        db.session.commit()
        flash('Operator updated successfully!')
        return redirect(url_for('operators'))

    return render_template('edit_operator.html', operator=operator)

@app.route('/delete_operator/<int:id>', methods=['GET', 'POST'])
def delete_operator(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    operator = Operator.query.get(id)
    if operator and operator.user_id != User.query.filter_by(username=session['username']).first().id:
        flash('You are not authorized to delete this operator', 'error')
        return redirect(url_for('operators'))

    db.session.delete(operator)
    db.session.commit()
    flash('Operator successfully deleted!')
    return redirect(url_for('operators')
                    
                    )

@app.route('/chargings')
def chargings():
    if 'username' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    vehicle_sql = 'SELECT id, vehicle_name FROM vehicle WHERE user_id = :user_id;'
    station_sql = 'SELECT id, station_name FROM charging_station WHERE user_id = :user_id;'

    vehicle_result = db.session.execute(text(vehicle_sql), {'user_id': user_id})
    station_result = db.session.execute(text(station_sql), {'user_id': user_id})

    user_vehicles = [{'id': row[0], 'vehicle_name': row[1]} for row in vehicle_result]
    user_charging_stations = [{'id': row[0], 'station_name': row[1]} for row in station_result]

    # Tulosta arvot palvelimen lokitiedostoon
    print("User Vehicles:", user_vehicles)
    print("User Charging Stations:", user_charging_stations)

    user_chargings = Charging.query.filter_by(user_id=user_id).all()



    # Lisätään jokaiselle charging-objektille station_name ja car_name
    for charging in user_chargings:
        # Hae latausaseman nimi
        station = ChargingStation.query.get(charging.charging_station_id)
        charging.station_name = station.station_name if station else 'Unknown'

        # Hae auton nimi
        car = Vehicle.query.get(charging.vehicle)
        charging.car_name = car.vehicle_name if car else 'Unknown'

    return render_template('charging.html', chargings=user_chargings, vehicles=user_vehicles, charging_stations=user_charging_stations)

@app.route('/add_charging', methods=['POST'])
def add_charging():
    if 'username' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    charging_station = request.form['charging_station']
    start_time = request.form['start_time']
    end_time = request.form['end_time']
    charged_energy = request.form['charged_energy']
    cost = request.form['cost']
    vehicle = request.form['vehicle']
    mileage = request.form['mileage']

    new_charging = Charging(user_id=user_id, charging_station=charging_station, start_time=start_time,
                            end_time=end_time, charged_energy=charged_energy, cost=cost, vehicle=vehicle,
                            mileage=mileage)
    db.session.add(new_charging)
    db.session.commit()

    flash('Charging data added successfully!')
    return redirect(url_for('charging_page'))

@app.route('/edit_charging/<int:charging_id>', methods=['GET', 'POST'])
def edit_charging(charging_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    charging = Charging.query.get_or_404(charging_id)

    if request.method == 'POST':
        charging.charging_station = request.form['charging_station']
        charging.start_time = request.form['start_time']
        charging.end_time = request.form['end_time']
        charging.charged_energy = request.form['charged_energy']
        charging.cost = request.form['cost']
        charging.vehicle = request.form['vehicle']
        charging.mileage = request.form['mileage']

        db.session.commit()
        flash('Charging data updated successfully!')
        return redirect(url_for('charging'))

    return render_template('edit_charging.html', charging=charging)

@app.route('/delete_charging/<int:charging_id>', methods=['POST'])
def delete_charging(charging_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    charging = Charging.query.get_or_404(charging_id)
    db.session.delete(charging)
    db.session.commit()
    flash('Charging data deleted successfully!')
    return redirect(url_for('charging'))


if __name__ == '__main__':
    app.run(debug=True)
