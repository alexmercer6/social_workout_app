DROP TABLE IF EXISTS achievements;
DROP TABLE IF EXISTS babies;
DROP TABLE IF EXISTS users;


CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name TEXT,
    email TEXT,
    number INTEGER,
    password_hash TEXT,
    created_on TIMESTAMP NOT NULL DEFAULT NOW(),
    last_login TIMESTAMP
);

CREATE TABLE babies (
    baby_id SERIAL PRIMARY KEY,
    name TEXT,
    birth_ddmmyyyy TEXT,
    user_id INTEGER REFERENCES users (user_id)
    

);

CREATE TABLE achievements (
    id SERIAL PRIMARY KEY,
    achievements TEXT,
    baby_id INTEGER REFERENCES babies (baby_id)
);