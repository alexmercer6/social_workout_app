DROP TABLE IF EXISTS users;

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name TEXT,
    email TEXT,
    number INTEGER,
    password_hash TEXT
);

CREATE TABLE babies (
    baby_id SERIAL PRIMARY KEY,]
    name TEXT,
    ddmmyyyy TEXT,
    parent_id INTEGER REFERENCES users (user_id)
    

)