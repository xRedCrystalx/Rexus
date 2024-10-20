# MAIN TODO

- fix permission check for admin-only commands
- async PIL py library
- discord loggers
- permission handlers > double check
- better event runner of queue system (new db system first)
- important helpers - discord ID validation...
- background task checker
- better system statistics
- support server setup
- terminator to safely end connections/modules

## SECURITY

- metaclass BaseSecuredMeta with hash (how to save it?)
- database access for only xyz hashes
- lots of honey tokens/pots
- required password for doing updates/runtime manipulation
- background tasks for checking integrity - what if they get terminated?
- discord notifications

* somehow isolate critical modules?

## DATABASE

PostgreSQL - psycopg[pool]
Each plugin - own table