drop table if exists users;
create table users (
	id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	email TEXT NOT NULL UNIQUE,
	password TEXT NOT NULL,
	username TEXT NOT NULL UNIQUE,
	access_level INTEGER NOT NULL,
	is_admin BOOLEAN NOT NULL,
	is_verified BOOLEAN NOT NULL
);
