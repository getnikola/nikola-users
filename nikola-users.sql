DROP TABLE IF EXISTS nupages;
DROP TABLE IF EXISTS nuadmins;
CREATE TABLE nupages (
    id integer primary key autoincrement unique,
    title text not null,
    url text not null,
    author text not null,
    description text not null,
    sourcelink text null,
    visible boolean not null,
    date date not null,
    email text not null,
);

CREATE TABLE nuadmins (
    id integer primary key autoincrement unique,
    username text not null unique,
    password text not null unique,
);
