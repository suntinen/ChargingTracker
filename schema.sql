-- Käytä tätä tiedostoa luodaksesi tietokantaan tarvittavat taulut ja asetukset

-- Käytä chargingtrackerdb-tietokantaa
\c chargingtrackerdb ctadmin

-- Poista vanha schema, jos se on olemassa
DROP SCHEMA IF EXISTS public CASCADE;

-- Luo uusi schema
CREATE SCHEMA public;

ALTER USER ctadmin SET search_path TO public;

-- Määrittele taulut skeeman sisällä
CREATE TABLE IF NOT EXISTS public.users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) NOT NULL,
    password_hash VARCHAR(256) NOT NULL
);

CREATE TABLE IF NOT EXISTS public.operators (
    id SERIAL PRIMARY KEY,
    operator_name VARCHAR(50),
    user_id INTEGER REFERENCES public.users(id)
);

CREATE TABLE IF NOT EXISTS public.vehicle (
    id SERIAL PRIMARY KEY,
    vehicle_name TEXT NOT NULL,
    user_id INTEGER NOT NULL REFERENCES public.users(id),
    battery_size INTEGER NOT NULL,
    last_mileage INTEGER
);

CREATE TABLE IF NOT EXISTS public.destinations (
    id SERIAL PRIMARY KEY,
    destination_name VARCHAR(255) NOT NULL,
    user_id INTEGER NOT NULL REFERENCES public.users(id)
);

CREATE TABLE IF NOT EXISTS public.charging_station (
    id SERIAL PRIMARY KEY,
    station_name VARCHAR(50),
    streetname1 VARCHAR(50),
    streetname2 VARCHAR(50),
    zip VARCHAR(20),
    city VARCHAR(30),
    country VARCHAR(30),
    operator INTEGER REFERENCES public.operators(id),
    user_id INTEGER REFERENCES public.users(id)
);

CREATE TABLE IF NOT EXISTS public.charging (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES public.users(id),
    charging_station_id INTEGER REFERENCES public.charging_station(id),
    start_time TIMESTAMP WITHOUT TIME ZONE,
    end_time TIMESTAMP WITHOUT TIME ZONE,
    charged_energy INTEGER,
    cost INTEGER,
    vehicle INTEGER REFERENCES public.vehicle(id),
    mileage INTEGER,
    destination_id INTEGER REFERENCES public.destinations(id) -- Lisätty destination_id viiteavaimella
);

-- Aseta kaikkien taulujen ja sekvenssien omistajaksi ctadmin
ALTER TABLE public.charging OWNER TO ctadmin;
ALTER TABLE public.charging_station OWNER TO ctadmin;
ALTER TABLE public.operators OWNER TO ctadmin;
ALTER TABLE public.users OWNER TO ctadmin;
ALTER TABLE public.vehicle OWNER TO ctadmin;
ALTER TABLE public.destinations OWNER TO ctadmin;

-- Aseta oikeudet
GRANT ALL ON TABLE public.charging, public.charging_station, public.operators, public.users, public.vehicle, public.destinations TO ctadmin;
GRANT ALL ON SEQUENCE public.charging_id_seq, public.charging_station_id_seq, public.operators_id_seq, public.users_id_seq, public.vehicle_id_seq, public.destinations_id_seq TO ctadmin;
