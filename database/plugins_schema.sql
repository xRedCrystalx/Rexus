CREATE DATABASE IF NOT EXISTS Rexus;
USE Rexus;

START TRANSACTION;

-- Plugin main table
CREATE TABLE IF NOT EXISTS plugins (
    guild_id INT(24) NOT NULL PRIMARY KEY,

    general BOOLEAN NOT NULL DEFAULT FALSE,
    cmd BOOLEAN NOT NULL DEFAULT FALSE,
    alt BOOLEAN NOT NULL DEFAULT FALSE,
    imper BOOLEAN NOT NULL DEFAULT FALSE,
    automod BOOLEAN NOT NULL DEFAULT FALSE,
    link BOOLEAN NOT NULL DEFAULT FALSE,
    ping BOOLEAN NOT NULL DEFAULT FALSE,
    auto_delete BOOLEAN NOT NULL DEFAULT FALSE,
    auto_slowmode BOOLEAN NOT NULL DEFAULT FALSE,
    reaction BOOLEAN NOT NULL DEFAULT FALSE
);

-- Plugin specific tables
CREATE TABLE IF NOT EXISTS pl_general (
    guild_id INT(24) NOT NULL,

    language VARCHAR(8),
    allowAdminEditing BOOLEAN NOT NULL DEFAULT FALSE,
    staffRole INT(24),
    staffChannel INT(24),
    adminRole INT(24),
    adminChannel INT(24),

    PRIMARY KEY (guild_id),
    FOREIGN KEY (guild_id) REFERENCES plugins (guild_id)
);

CREATE TABLE IF NOT EXISTS pl_cmd (
    guild_id INT(24) NOT NULL,

    logCmdExecution BOOLEAN DEFAULT FALSE,
    failedCmdExecution BOOLEAN DEFAULT FALSE,
    cmdExecutionLogChannel INT(24),

    PRIMARY KEY (guild_id),
    FOREIGN KEY (guild_id) REFERENCES plugins (guild_id)
);

CREATE TABLE IF NOT EXISTS pl_alt (
    guild_id INT(24) NOT NULL,

    log_channel INT(24),

    PRIMARY KEY (guild_id),
    FOREIGN KEY (guild_id) REFERENCES plugins (guild_id)
);

CREATE TABLE IF NOT EXISTS pl_imper (
    guild_id INT(24) NOT NULL,

    log_channel INT(24),
    
    PRIMARY KEY (guild_id),
    FOREIGN KEY (guild_id) REFERENCES plugins (guild_id)
);

CREATE TABLE IF NOT EXISTS pl_automod (
    guild_id INT(24) NOT NULL,

    log_channel INT(24),
    rules JSON NOT NULL,

    PRIMARY KEY (guild_id),
    FOREIGN KEY (guild_id) REFERENCES plugins (guild_id)
);

CREATE TABLE IF NOT EXISTS pl_link (
    guild_id INT(24) NOT NULL,

    log_channel INT(24),
    options JSON NOT NULL,
    
    PRIMARY KEY (guild_id),
    FOREIGN KEY (guild_id) REFERENCES plugins (guild_id)
);

CREATE TABLE IF NOT EXISTS pl_ping (
    guild_id INT(24) NOT NULL,

    detectReplyPings BOOLEAN NOT NULL DEFAULT FALSE,
    ignoredChannels JSON NOT NULL,
    rules JSON NOT NULL,

    PRIMARY KEY (guild_id),
    FOREIGN KEY (guild_id) REFERENCES plugins (guild_id)
);

CREATE TABLE IF NOT EXISTS pl_auto_delete (
    guild_id INT(24) NOT NULL,

    monitored JSON NOT NULL,
    
    PRIMARY KEY (guild_id),
    FOREIGN KEY (guild_id) REFERENCES plugins (guild_id)
);

CREATE TABLE IF NOT EXISTS pl_auto_slowmode (
    guild_id INT(24) NOT NULL,

    log_channel INT(24),
    monitored JSON NOT NULL,
    
    PRIMARY KEY (guild_id),
    FOREIGN KEY (guild_id) REFERENCES plugins (guild_id)
);

CREATE TABLE IF NOT EXISTS pl_reaction (
    guild_id INT(24) NOT NULL,

    log_channel INT(24),
    reactionBanRole INT(24),
    
    PRIMARY KEY (guild_id),
    FOREIGN KEY (guild_id) REFERENCES plugins (guild_id)
);

COMMIT;