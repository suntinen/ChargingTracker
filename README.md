# ChargingTracker

Welcome to the GitHub page of the ChargingTracker! This web application provides a convenient way to track the energy consumption and associated costs of charging your electric car.

## Features

- **Maintain and review Charging History:** You can maintain and review your electric car's  charging sessions, including dates, energy consumption, and costs. Later adding feature to track costs per destinations.

- Vehicle Data: ** Vehicle name
- Charging Data: ** Charged energy (kWh), time, cost
- Charging Station: ** Charging station name, address, operator
- User Data: ** User name
- Car Data: ** Car name
- To be done later: ** Destinations

## Templates
- charging.html: ** Storing charging events
- index.html: ** Main page 
- station.html: ** Charging statations' data
- edit_charging.html: ** Edit view for charging events
- layout.html: ** Application navigation and formats
- vehicles.html: ** Cars data
- edit_operator.html: ** Edit view for operators
- login.html: ** Login page
- welcome.html: ** Welcome page ('commercials' without login) 
- edit_station.html: ** Edit view for stations
- operator.html: ** Operators' data
- edit_vehicle.html: ** Edit view for cars
- register.html: ** User registration

## Database
- **Tables**
- charging         
- charging_station 
- operators        
- user             
- vehicle
- destinations

# Code
- app.py: ** Adding later additional modules (db.py, routes.py, etc.) to make it more readable

## Installation

1. Clone this project to your local machine:

```bash
git clone https://github.com/suntinen/ChargingTracker.git
cd ChargingTracker
pip install -r requirements.txt

sudo -u postgres psql
CREATE DATABASE db_name_here
\c db_name_here
\i schema.sql
\q

