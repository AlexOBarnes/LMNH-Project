DROP TABLE IF EXISTS gamma.recordings;
DROP TABLE IF EXISTS gamma.plants;
DROP TABLE IF EXISTS gamma.origins;
DROP TABLE IF EXISTS gamma.regions;
DROP TABLE IF EXISTS gamma.countries;
DROP TABLE IF EXISTS gamma.plant_species;
DROP TABLE IF EXISTS gamma.continents;
DROP TABLE IF EXISTS gamma.botanists;


CREATE TABLE gamma.countries (
    country_id SMALLINT IDENTITY(1,1),
    country_code VARCHAR(8) NOT NULL UNIQUE,
    country_name VARCHAR(255) NOT NULL UNIQUE,
    PRIMARY KEY(country_id)
);

CREATE TABLE gamma.plant_species (
    plant_species_id INT IDENTITY(1,1),
    common_name VARCHAR(255) NOT NULL,
    scientific_name VARCHAR(255) NOT NULL UNIQUE,
    PRIMARY KEY(plant_species_id)
);

CREATE TABLE gamma.continents (
    continent_id SMALLINT IDENTITY(1,1),
    continent_name VARCHAR(255) NOT NULL UNIQUE,
    PRIMARY KEY(continent_id)
);

CREATE TABLE gamma.regions (
    town_id INT IDENTITY(1,1),
    town_name VARCHAR(255) NOT NULL,
    continent_id SMALLINT NOT NULL,
    country_id SMALLINT NOT NULL,
    PRIMARY KEY(town_id),
    FOREIGN KEY(continent_id) REFERENCES gamma.continents(continent_id),
    FOREIGN KEY(country_id) REFERENCES gamma.countries(country_id)
);

CREATE TABLE gamma.origins (
    location_id INT IDENTITY(1,1),
    longitude FLOAT(53) NOT NULL UNIQUE,
    latitude FLOAT(53) NOT NULL UNIQUE,
    town_id INT NOT NULL,
    PRIMARY KEY(location_id),
    FOREIGN KEY(town_id) REFERENCES gamma.regions(town_id)
);

CREATE TABLE gamma.botanists (
    botanist_id INT IDENTITY(1,1),
    email VARCHAR(255) NOT NULL UNIQUE,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    phone VARCHAR(255) NOT NULL UNIQUE,
    PRIMARY KEY(botanist_id)
);

CREATE TABLE gamma.plants (
    plant_id INT IDENTITY(1,1),
    location_id INT NOT NULL,
    last_watering DATETIME NOT NULL CHECK (last_watering <= CURRENT_TIMESTAMP),
    plant_species_id INT NOT NULL,
    PRIMARY KEY(plant_id),
    FOREIGN KEY(location_id) REFERENCES gamma.origins(location_id),
    FOREIGN KEY(plant_species_id) REFERENCES gamma.plant_species(plant_species_id)
);

CREATE TABLE gamma.recordings (
    recording_id BIGINT IDENTITY(1,1),
    time_taken DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP CHECK (time_taken <= CURRENT_TIMESTAMP),
    soil_moisture FLOAT(53) NOT NULL,
    temperature FLOAT(53) NOT NULL,
    plant_id INT NOT NULL,
    botanist_id INT NOT NULL,
    PRIMARY KEY(recording_id),
    FOREIGN KEY(botanist_id) REFERENCES gamma.botanists(botanist_id),
    FOREIGN KEY(plant_id) REFERENCES gamma.plants(plant_id)
);
