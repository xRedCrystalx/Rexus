USE Rexus;

-- Drop the existing trigger
DROP TRIGGER IF EXISTS guild_setup;

-- Creates trigger
CREATE TRIGGER guild_setup
AFTER INSERT ON plugins
    FOR EACH ROW BEGIN
        -- Starts inserting data
        INSERT INTO general (guild_id) VALUES (NEW.guild_id);
        INSERT INTO cmd (guild_id) VALUES (NEW.guild_id);
        INSERT INTO alt (guild_id) VALUES (NEW.guild_id);
        INSERT INTO imper (guild_id) VALUES (NEW.guild_id);
        INSERT INTO automod (guild_id, rules) VALUES (NEW.guild_id, JSON_ARRAY());
        INSERT INTO link (guild_id, options) VALUES (NEW.guild_id, JSON_ARRAY());
        INSERT INTO ping (guild_id, ignoredChannels, rules) VALUES (NEW.guild_id, JSON_ARRAY(), JSON_ARRAY());
        INSERT INTO auto_delete (guild_id, monitored) VALUES (NEW.guild_id, JSON_ARRAY());
        INSERT INTO auto_slowmode (guild_id, monitored) VALUES (NEW.guild_id, JSON_ARRAY());
        INSERT INTO reaction (guild_id) VALUES (NEW.guild_id);
END;
