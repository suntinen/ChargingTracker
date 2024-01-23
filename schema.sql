
SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: charging; Type: TABLE; Schema: public
--

CREATE TABLE public.charging (
    charging_id integer NOT NULL,
    user_id integer NOT NULL,
    charging_station_id integer,
    start_time timestamp without time zone,
    end_time timestamp without time zone,
    charged_energy integer,
    cost integer,
    vehicle integer,
    mileage integer
);


ALTER TABLE public.charging OWNER TO ctadmin;

--
-- Name: charging_charging_id_seq; Type: SEQUENCE; Schema: public
--

CREATE SEQUENCE public.charging_charging_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.charging_charging_id_seq OWNER TO ctadmin;

--
-- Name: charging_charging_id_seq; Type: SEQUENCE OWNED BY; Schema: public
--

ALTER SEQUENCE public.charging_charging_id_seq OWNED BY public.charging.charging_id;


--
-- Name: charging_station; Type: TABLE; Schema: public
--

CREATE TABLE public.charging_station (
    id integer NOT NULL,
    station_name character varying(50),
    streetname1 character varying(50),
    streetname2 character varying(50),
    zip character varying(20),
    city character varying(30),
    country character varying(30),
    operator integer,
    user_id integer
);


ALTER TABLE public.charging_station OWNER TO ctadmin;

--
-- Name: charging_station_id_seq; Type: SEQUENCE; Schema: public
--

CREATE SEQUENCE public.charging_station_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.charging_station_id_seq OWNER TO ctadmin;

--
-- Name: charging_station_id_seq; Type: SEQUENCE OWNED BY; Schema: public
--

ALTER SEQUENCE public.charging_station_id_seq OWNED BY public.charging_station.id;


--
-- Name: operators; Type: TABLE; Schema: public
--

CREATE TABLE public.operators (
    id integer NOT NULL,
    operator_name character varying(50),
    user_id integer
);


ALTER TABLE public.operators OWNER TO ctadmin;

--
-- Name: operators_id_seq; Type: SEQUENCE; Schema: public
--

CREATE SEQUENCE public.operators_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.operators_id_seq OWNER TO ctadmin;

--
-- Name: operators_id_seq; Type: SEQUENCE OWNED BY; Schema: public
--

ALTER SEQUENCE public.operators_id_seq OWNED BY public.operators.id;


--
-- Name: user; Type: TABLE; Schema: public
--

CREATE TABLE public."user" (
    id integer NOT NULL,
    username character varying(80) NOT NULL,
    password_hash character varying(256) NOT NULL
);


ALTER TABLE public."user" OWNER TO ctadmin;

--
-- Name: user_id_seq; Type: SEQUENCE; Schema: public
--

CREATE SEQUENCE public.user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_id_seq OWNER TO ctadmin;

--
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: public
--

ALTER SEQUENCE public.user_id_seq OWNED BY public."user".id;


--
-- Name: vehicle; Type: TABLE; Schema: public
--

CREATE TABLE public.vehicle (
    id integer NOT NULL,
    vehicle_name text NOT NULL,
    user_id integer NOT NULL,
    battery_size integer NOT NULL,
    last_mileage integer
);


ALTER TABLE public.vehicle OWNER TO ctadmin;

--
-- Name: vehicle_id_seq; Type: SEQUENCE; Schema: public
--

CREATE SEQUENCE public.vehicle_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vehicle_id_seq OWNER TO ctadmin;

--
-- Name: vehicle_id_seq; Type: SEQUENCE OWNED BY; Schema: public
--

ALTER SEQUENCE public.vehicle_id_seq OWNED BY public.vehicle.id;


--
-- Name: charging charging_id; Type: DEFAULT; Schema: public
--

ALTER TABLE ONLY public.charging ALTER COLUMN charging_id SET DEFAULT nextval('public.charging_charging_id_seq'::regclass);


--
-- Name: charging_station id; Type: DEFAULT; Schema: public
--

ALTER TABLE ONLY public.charging_station ALTER COLUMN id SET DEFAULT nextval('public.charging_station_id_seq'::regclass);


--
-- Name: operators id; Type: DEFAULT; Schema: public
--

ALTER TABLE ONLY public.operators ALTER COLUMN id SET DEFAULT nextval('public.operators_id_seq'::regclass);


--
-- Name: user id; Type: DEFAULT; Schema: public
--

ALTER TABLE ONLY public."user" ALTER COLUMN id SET DEFAULT nextval('public.user_id_seq'::regclass);


--
-- Name: vehicle id; Type: DEFAULT; Schema: public
--

ALTER TABLE ONLY public.vehicle ALTER COLUMN id SET DEFAULT nextval('public.vehicle_id_seq'::regclass);


--
-- Name: charging charging_pkey; Type: CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.charging
    ADD CONSTRAINT charging_pkey PRIMARY KEY (charging_id);


--
-- Name: charging_station charging_station_pkey; Type: CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.charging_station
    ADD CONSTRAINT charging_station_pkey PRIMARY KEY (id);


--
-- Name: operators operators_pkey; Type: CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.operators
    ADD CONSTRAINT operators_pkey PRIMARY KEY (id);


--
-- Name: user users_pkey; Type: CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: user users_username_key; Type: CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: vehicle vehicle_pkey; Type: CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.vehicle
    ADD CONSTRAINT vehicle_pkey PRIMARY KEY (id);


--
-- Name: charging charging_charging_station_id_fkey; Type: FK CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.charging
    ADD CONSTRAINT charging_charging_station_id_fkey FOREIGN KEY (charging_station_id) REFERENCES public.charging_station(id);


--
-- Name: charging_station charging_station_operator_fkey; Type: FK CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.charging_station
    ADD CONSTRAINT charging_station_operator_fkey FOREIGN KEY (operator) REFERENCES public.operators(id);


--
-- Name: charging_station charging_station_user_id_fkey; Type: FK CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.charging_station
    ADD CONSTRAINT charging_station_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: charging charging_user_id_fkey; Type: FK CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.charging
    ADD CONSTRAINT charging_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: charging charging_vehicle_fkey; Type: FK CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.charging
    ADD CONSTRAINT charging_vehicle_fkey FOREIGN KEY (vehicle) REFERENCES public.vehicle(id);


--
-- Name: operators operators_user_id_fkey; Type: FK CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.operators
    ADD CONSTRAINT operators_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: vehicle vehicle_user_id_fkey; Type: FK CONSTRAINT; Schema: public
--

ALTER TABLE ONLY public.vehicle
    ADD CONSTRAINT vehicle_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: TABLE charging; Type: ACL; Schema: public
--

GRANT ALL ON TABLE public.charging TO ctadmin;


--
-- Name: SEQUENCE charging_charging_id_seq; Type: ACL; Schema: public
--

GRANT ALL ON SEQUENCE public.charging_charging_id_seq TO ctadmin;


--
-- Name: TABLE charging_station; Type: ACL; Schema: public
--

GRANT ALL ON TABLE public.charging_station TO ctadmin;


--
-- Name: SEQUENCE charging_station_id_seq; Type: ACL; Schema: public
--

GRANT ALL ON SEQUENCE public.charging_station_id_seq TO ctadmin;


--
-- Name: TABLE operators; Type: ACL; Schema: public
--

GRANT ALL ON TABLE public.operators TO ctadmin;


--
-- Name: SEQUENCE operators_id_seq; Type: ACL; Schema: public
--

GRANT ALL ON SEQUENCE public.operators_id_seq TO ctadmin;


--
-- Name: TABLE "user"; Type: ACL; Schema: public
--

GRANT ALL ON TABLE public."user" TO ctadmin;


--
-- Name: SEQUENCE user_id_seq; Type: ACL; Schema: public
--

GRANT ALL ON SEQUENCE public.user_id_seq TO ctadmin;


--
-- Name: TABLE vehicle; Type: ACL; Schema: public
--

GRANT ALL ON TABLE public.vehicle TO ctadmin;


--
-- Name: SEQUENCE vehicle_id_seq; Type: ACL; Schema: public
--

GRANT ALL ON SEQUENCE public.vehicle_id_seq TO ctadmin;


