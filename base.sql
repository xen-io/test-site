SET datestyle = dmy;

CREATE TABLE IF NOT EXISTS owners (
	id SERIAL PRIMARY KEY,
	name TEXT NOT NULL,
	last_name TEXT NOT NULL,
	middle_name TEXT NOT NULL,
	sex BOOLEAN NOT NULL,
	birthday DATE NOT NULL,
	home INTEGER NOT NULL,
	CHECK (
		(name ~ '[а-яА-Я\-]+') AND
		(last_name ~ '[а-яА-Я\-]+') AND
		(middle_name ~ '[а-яА-Я\-]+')
	)
);

CREATE TABLE IF NOT EXISTS animals (
	id SERIAL PRIMARY KEY,
	owner INTEGER NOT NULL REFERENCES owners (id),
	nick TEXT NOT NULL,
	breed TEXT NOT NULL,
	sex BOOLEAN NOT NULL,
	birthday DATE NOT NULL,
	reg_date TIMESTAMP NOT NULL,
	description TEXT NOT NULL,
	CHECK (
		(nick ~ '[а-яА-Я]+') AND
		(breed ~ '[а-яА-Я]+')
	)
);
