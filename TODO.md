- database system (schema, type, system)
- fix permission check for admin-only commands
- async PIL py library
- re-organizing plugins?
- discord loggers
- permission handlers > double check
- better event runner of queue system (new db system first)
- important helpers - discord ID validation...
- background task checker
- better system statistics
- support server setup

# SECURITY:
- metaclass BaseSecuredMeta with hash (how to save it?)
- database access for only xyz hashes
- lots of honey tokens/pots
- required password for doing updates/runtime manipulation
- background tasks for checking integrity - what if they get terminated?
- discord notifications

* somehow isolate critical modules?

# DATABASE:
SQLite - simple and fast

Each plugin - own table + global table (on/off plugin)

### Example Global:

| guild_id | general | cmd   | alt   | imper | ai    | automod | link  | ping  | auto_delete |
|----------|---------|-------|-------|-------|-------|---------|-------|-------|-------------|
|  1234567 | false   | false | false | false | false | false   | false | false | false       |

### Example plugin-specific:
```
CREATE TABLE reaction (
    guild_ID INT(20) PRIMARY KEY,
    log_channel int,
    reactionBanRole int,
);
```

| guild_id | log_channel | reactionBanRole |
|----------|-------------|-----------------|
|  1234567 | 54857285236 | 64282285266     |