USE Rexus;

-- Drop the existing trigger
DROP TRIGGER IF EXISTS guild_setup;

-- Creates trigger
CREATE TRIGGER guild_setup
AFTER INSERT ON plugins
    FOR EACH ROW BEGIN
        -- Starts inserting data
        INSERT INTO pl_general (guild_id) VALUES (NEW.guild_id);
        INSERT INTO pl_cmd (guild_id) VALUES (NEW.guild_id);
        INSERT INTO pl_alt (guild_id) VALUES (NEW.guild_id);
        INSERT INTO pl_imper (guild_id) VALUES (NEW.guild_id);
        INSERT INTO pl_automod (guild_id, rules) VALUES (NEW.guild_id, JSON_ARRAY());
        INSERT INTO pl_link (guild_id, options) VALUES (NEW.guild_id, JSON_ARRAY());
        INSERT INTO pl_ping (guild_id, ignoredChannels, rules) VALUES (NEW.guild_id, JSON_ARRAY(), JSON_ARRAY());
        INSERT INTO pl_auto_delete (guild_id, monitored) VALUES (NEW.guild_id, JSON_ARRAY());
        INSERT INTO pl_auto_slowmode (guild_id, monitored) VALUES (NEW.guild_id, JSON_ARRAY());
        INSERT INTO pl_reaction (guild_id) VALUES (NEW.guild_id);
END;
