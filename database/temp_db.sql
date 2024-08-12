CREATE DATABASE IF NOT EXISTS Rexus;
USE Rexus;

START TRANSACTION;

CREATE TABLE IF NOT EXISTS plugins (
    id INT(24) NOT NULL PRIMARY KEY,
    
    general JSON NOT NULL,
    cmd JSON NOT NULL,
    alt JSON NOT NULL,
    imper JSON NOT NULL,
    automod JSON NOT NULL,
    link JSON NOT NULL,
    ping JSON NOT NULL,
    auto_delete JSON NOT NULL,
    auto_slowmode JSON NOT NULL,
    reaction JSON NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    id INT(24) NOT NULL PRIMARY KEY,

    guilds JSON NOT NULL
)

COMMIT;