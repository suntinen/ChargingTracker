# ChargingTracker

Welcome to the GitHub page of **ChargingTracker**! This web application provides a convenient way to track the energy consumption and associated costs of charging your electric vehicle. Built using the Flask web framework and leveraging PostgreSQL for data storage, ChargingTracker offers a user-friendly interface for managing vehicles, charging stations, operators, and charging records, which can be grouped with destinations.

## Features

- **User Authentication:** Secure login and registration system with hashed passwords using `werkzeug.security`.
- **Vehicle Management:** Add, edit, and delete vehicles with details such as battery size and mileage.
- **Charging Station Management:** Manage charging stations, including location details and associated operators.
- **Operator Management:** Add and manage operators for charging stations.
- **Charging Records:** Track charging sessions with details like start/end times, cost, and energy charged.
- **Destination Management:** Add and manage frequent charging destinations.

## Templates

- `charging.html`: Storing charging events.
- `index.html`: Main page.
- `station.html`: Charging stations' data.
- `edit_charging.html`: Edit view for charging events.
- `layout.html`: Application navigation and formats.
- `vehicles.html`: Cars data.
- `edit_operator.html`: Edit view for operators.
- `login.html`: Login page.
- `welcome.html`: Welcome page (shows 'commercials' without login).
- `edit_station.html`: Edit view for stations.
- `operator.html`: Operators' data.
- `edit_vehicle.html`: Edit view for cars.
- `register.html`: User registration.
- `destination.html`: Destinations data.
- `edit_destination.html`: Edit view for destinations.

## Technology Stack

- **Flask:** A lightweight WSGI web application framework.
- **SQLAlchemy:** SQL toolkit and ORM for Python.
- **PostgreSQL:** Open source relational database.
- **werkzeug.security:** Provides hashing utilities for password security.
- **dotenv:** Loads environment variables from a `.env` file.

## Database

**Tables:**
- `charging`
- `charging_station`
- `operators`
- `user`
- `vehicle`
- `destinations`

## Code

- `app.py`: Main application file. Planning to add additional modules (db.py, routes.py, etc.) to make it more readable.

## Getting Started

### Prerequisites

- Python 3.6 or later.
- PostgreSQL installed and running.
- pip for installing dependencies.

### Installation

1. **Clone this project to your local machine:**

    ```bash
    git clone https://github.com/suntinen/ChargingTracker.git
    cd ChargingTracker
    pip install -r requirements.txt
    ```

2. **Create a `.env` file in the root directory and add your secret key and database URI:**

    ```plaintext
    SECRET_KEY='your_secret_key_here'
    DATABASE_URI='postgresql:///chargingtrackerdb'
    ```

3. **Set up the PostgreSQL database:**

    ```bash
    sudo -u postgres psql
    CREATE DATABASE db_name_here;
    \c db_name_here;
    \i schema.sql;
    \q
    ```

4. **Initialize the database:**

    ```bash
    flask db upgrade
    ```

5. **Run the application:**

    ```bash
    flask run
    ```

    The application should now be running on [http://localhost:5000/](http://localhost:5000/).

## Usage

- Visit [http://localhost:5000/](http://localhost:5000/) in your browser to start using ChargingTracker.
- Register a new user account or log in.
- Begin by adding your vehicles, operators, and charging stations. Track your charging sessions and manage your electric vehicle charging data efficiently. You can group charging events with destinations.
