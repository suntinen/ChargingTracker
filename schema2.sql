-- Luo tietokanta ensin psql-komennolla: CREATE DATABASE chargingtrackerdb;
-- CREATE DATABASE chargingtrackerdb;
-- Luo käyttäjä ensin psql-komennolla: CREATE USER ctadmin WITH PASSWORD 'salasana';
-- CREATE USER ctadmin WITH PASSWORD 'salasana';
-- Aseta käyttäjälle oikeudet tietokantaan
GRANT ALL PRIVILEGES ON DATABASE chargingtrackerdb TO ctadmin;
-- Oletetaan, että tietokanta on nyt luotu ja vaihdetaan siihen yhteyttä
\c chargingtrackerdb

-- Aja tämä tiedosto psql-komennolla: \i schema2.sql

-- Antaa ctadmin-käyttäjälle oikeuden luoda tauluja public-skeemassa
GRANT CREATE ON SCHEMA public TO ctadmin;

-- Antaa ctadmin-käyttäjälle oikeuden käyttää public-skeemaa
GRANT USAGE ON SCHEMA public TO ctadmin;

-- Antaa ctadmin-käyttäjälle oikeuden lukea ja kirjoittaa kaikkiin public-skeeman tauluihin
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ctadmin;

-- Antaa ctadmin-käyttäjälle oikeuden lukea ja kirjoittaa kaikkiin public-skeeman sekvensseihin
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ctadmin;

-- Varmistaa, että ctadmin saa oikeudet myös tulevaisuudessa luotuihin tauluihin
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO ctadmin;

-- Varmistaa, että ctadmin saa oikeudet myös tulevaisuudessa luotuihin sekvensseihin
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO ctadmin;

-- Vaihdetaan tietokantaan yhteyttä
\c chargingtrackerdb ctadmin

-- Poista vanha schema, jos se on olemassa
-- DROP SCHEMA IF EXISTS public CASCADE;

-- Luo uusi schema
-- CREATE SCHEMA public;