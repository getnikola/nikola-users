DROP TABLE IF EXISTS nupages;
DROP TABLE IF EXISTS nuadmins;
DROP SEQUENCE IF EXISTS nupages_id_seq;
DROP SEQUENCE IF EXISTS nuadmins_id_seq;

CREATE TABLE nupages (
    id SERIAL PRIMARY KEYS UNIQUE,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    author TEXT NOT NULL,
    description TEXT NOT NULL,
    sourcelink TEXT NULL,
    visible BOOLEAN NOT NULL,
    date DATE NOT NULL,
    email TEXT NOT NULL
);

CREATE TABLE nuadmins (
    id SERIAL PRIMARY KEY UNIQUE,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL UNIQUE
);

INSERT INTO nuadmins(username, password) VALUES (
    'admin',
    'c7ad44cbad762a5da0a452f9e854fdc1e0e7a52a38015f23f3eab1d80b931dd472634dfac71cd34ebc35d16ab7fb8a90c81f975113d6c7538dc69dd8de9077ec' /* admin */
);
