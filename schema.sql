DROP TABLE IF EXISTS eating_habits;
DROP TABLE IF EXISTS sleeping_habits;
DROP TABLE IF EXISTS completed_milestones;
DROP TABLE IF EXISTS milestones;
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
    birth_date TEXT,
    weight FLOAT,
    height FLOAT,
    profile_picture TEXT,
    user_id INTEGER REFERENCES users (user_id)
    

);

CREATE TABLE milestones (
    id SERIAL PRIMARY KEY,
    milestone TEXT,
    month_range INTEGER
);

CREATE TABLE completed_milestones (
    id SERIAL PRIMARY KEY,
    completed BOOLEAN,
    completed_on TIMESTAMP DEFAULT NOW(),
    milestone_id INTEGER REFERENCES milestones(id),
    baby_id INTEGER REFERENCES babies (baby_id)
);

CREATE TABLE sleeping_habits (
    id SERIAL PRIMARY KEY,
    time_of_day TEXT,
    duration TEXT,
    baby_id INTEGER REFERENCES babies (baby_id)

);

CREATE TABLE eating_habits (
    id SERIAL PRIMARY KEY,
    time_of_day TEXT,
    food_type TEXT,
    baby_id INTEGER REFERENCES babies (baby_id)
);

-- CREATE TABLE milestones_3_6_months (
--     id SERIAL PRIMARY KEY,
--     milestone TEXT,
--     checked TEXT,
--     baby_id INTEGER REFERENCES babies (baby_id)
-- );

-- CREATE TABLE milestones_6_9_months (
--     id SERIAL PRIMARY KEY,
--     milestone TEXT,
--     checked TEXT,
--     baby_id INTEGER REFERENCES babies (baby_id)
-- );

-- CREATE TABLE milestones_9_12_months (
--     id SERIAL PRIMARY KEY,
--     milestone TEXT,
--     checked TEXT,
--     baby_id INTEGER REFERENCES babies (baby_id)
-- );