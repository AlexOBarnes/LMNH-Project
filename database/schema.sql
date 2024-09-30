DROP TABLE IF EXISTS countries;
DROP TABLE IF EXISTS plant_species;
DROP TABLE IF EXISTS continents;
DROP TABLE IF EXISTS origins;
DROP TABLE IF EXISTS recordings;
DROP TABLE IF EXISTS regions;
DROP TABLE IF EXISTS botanists;
DROP TABLE IF EXISTS plants;

CREATE TABLE countries (
    country_id SMALLINT NOT NULL,
    country_code VARCHAR(8) NOT NULL,
    country_name VARCHAR(255) NOT NULL,
    PRIMARY KEY(country_id)
);

CREATE TABLE plant_species (
    plant_species_id INT NOT NULL,
    common_name VARCHAR(255) NOT NULL,
    scientific_name VARCHAR(255) NOT NULL,
    PRIMARY KEY(plant_species_id)
);

CREATE TABLE continents (
    continent_id SMALLINT NOT NULL,
    continent_name VARCHAR(255) NOT NULL,
    PRIMARY KEY(continent_id)
);

CREATE TABLE regions (
    town_id INT NOT NULL,
    town_name VARCHAR(255) NOT NULL,
    continent_id SMALLINT NOT NULL,
    country_id SMALLINT NOT NULL,
    PRIMARY KEY(town_id),
    FOREIGN KEY(continent_id) REFERENCES continents(continent_id),
    FOREIGN KEY(country_id) REFERENCES countries(country_id)
);

CREATE TABLE origins (
    location_id INT NOT NULL,
    longitude FLOAT(53) NOT NULL,
    latitude FLOAT(53) NOT NULL,
    town_id INT NOT NULL,
    PRIMARY KEY(location_id),
    FOREIGN KEY(town_id) REFERENCES regions(town_id)
);

CREATE TABLE botanists (
    botanist_id INT NOT NULL,
    email VARCHAR(255) NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    phone VARCHAR(255) NOT NULL,
    PRIMARY KEY(botanist_id)
);

CREATE TABLE plants (
    plant_id INT NOT NULL,
    location_id INT NOT NULL,
    last_watering DATETIME NOT NULL,
    plant_species_id INT NOT NULL,
    PRIMARY KEY(plant_id),
    FOREIGN KEY(location_id) REFERENCES origins(location_id),
    FOREIGN KEY(plant_species_id) REFERENCES plant_species(plant_species_id)
);

CREATE TABLE recordings (
    recording_id BIGINT NOT NULL,
    time DATETIME NOT NULL,
    soil_moisture FLOAT(53) NOT NULL,
    temperature FLOAT(53) NOT NULL,
    plant_id INT NOT NULL,
    botanist_id INT NOT NULL,
    PRIMARY KEY(recording_id),
    FOREIGN KEY(botanist_id) REFERENCES botanists(botanist_id),
    FOREIGN KEY(plant_id) REFERENCES plants(plant_id)
);
