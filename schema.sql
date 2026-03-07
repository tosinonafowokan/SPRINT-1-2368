CREATE DATABASE vip_event_manager;
USE vip_event_manager;

CREATE TABLE members (
member_id int auto_increment PRIMARY KEY,
first_name varchar(100) NOT NULL,
last_name varchar(100) NOT NULL,
email varchar(100) unique,
details text,
title varchar(100),
membership_level enum('Bronze', 'Silver', 'Gold') NOT NULL
);

CREATE TABLE events (
event_id int auto_increment PRIMARY KEY,
event_name varchar(100) NOT NULL,
event_description text,
capacity int NOT NULL,
level_requirement enum('Bronze', 'Silver', 'Gold') NOT NULL,
event_date date NOT NULL
);

CREATE TABLE registrations (
registration_id int auto_increment PRIMARY KEY,
member_id int NOT NULL,
event_id int NOT NULL,
registration_date datetime default current_timestamp,
registration_status enum('confirmed', 'waitlist', 'denied') default 'confirmed',
FOREIGN KEY (member_id) REFERENCES members(member_id),
FOREIGN KEY (event_id) REFERENCES events(event_id),
unique (member_id, event_id)
);
