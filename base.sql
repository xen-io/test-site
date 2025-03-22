SET datestyle = dmy;

CREATE TABLE IF NOT EXISTS owners (
	owner_id SERIAL PRIMARY KEY,
	owner_name TEXT NOT NULL,
	owner_lastname TEXT NOT NULL,
	owner_middlename TEXT NOT NULL,
	owner_sex BOOLEAN NOT NULL,
	owner_birthday DATE NOT NULL,
	owner_home INTEGER NOT NULL,
	CHECK (
		(owner_name ~ '[а-яА-Я\-]+') AND
		(owner_lastname ~ '[а-яА-Я\-]+') AND
		(owner_middlename ~ '[а-яА-Я\-]+')
	)
);

CREATE TABLE IF NOT EXISTS animals (
	animal_id SERIAL PRIMARY KEY,
	owner_id INTEGER NOT NULL REFERENCES owners (owner_id),
	animal_nick TEXT NOT NULL,
	animal_type TEXT NOT NULL,
	animal_sex BOOLEAN NOT NULL,
	animal_birthday DATE NOT NULL,
	animal_reg_date TIMESTAMP NOT NULL,
	animal_description TEXT NOT NULL,
	CHECK (
		(animal_nick ~ '[а-яА-Я]+') AND
		(animal_type ~ '[а-яА-Я]+')
	)
);
