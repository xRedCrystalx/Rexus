/*
Command for creating a database user. Due to privacy and security, accounts needs to be set/created manually.
*/

-- Can replace `host` with `localhost` (for local connections) or `%` (for all connections)
-- Within subnet: 192.168.1.% - Whitin private range: 192.168.%
CREATE USER 'custom-username'@'host' IDENTIFIED BY 'custom-password';
-- To remove user, use DROP command instead of CREATE

-- For all privileges use `ALL PRIVILEGES` - For all databases and tables use `*.*`
GRANT {privileges} ON {db.table} TO 'custom-username'@'host';
-- To revoke privileges, use REVOKE command instead of GRANT

FLUSH PRIVILEGES;

/*
MariaDB by default only listens to local host - 127.0.0.0
edit `bind-address: 0.0.0.0` in `/etc/mysql/mariadb.conf.d/50-server.cnf`
make sure to `service mariadb restart`

Login cmd: mariadb -u custom-username -p
*/

-- Pre-made examples
CREATE USER 'custom-username'@'192.168.%' IDENTIFIED BY 'custom-password';
CREATE USER 'custom-username'@'%' IDENTIFIED BY 'custom-password';

DROP USER 'custom-username'@'host';

-- Only use these when needed.
GRANT ALL PRIVILEGES ON *.* TO 'custom-username'@'host';
GRANT ALL PRIVILEGES ON *.* TO 'custom-username'@'host' WITH GRANT OPTION;

-- Full permissions inside the database
GRANT ALL PRIVILEGES ON {db}.* TO 'custom-username'@'host';
-- Connect and select - READ ONLY USER
GRANT SELECT ON {db}.* TO 'custom-username'@'host';
-- Table updating
GRANT SELECT, UPDATE ON {db}.* TO 'custom-username'@'host';
-- Removing/Inserting + updating
GRANT SELECT, UPDATE, INSERT, DELETE ON {db}.* TO 'custom-username'@'host';
-- Manipulation with tables
GRANT SELECT, ALTER, CREATE, DROP, INDEX, TRIGGER ON {db}.* TO 'custom-username'@'host';

REVOKE ALL PRIVILEGES ON *.* FROM 'custom-username'@'host';
REVOKE ALL PRIVILEGES ON {db}.* FROM 'custom-username'@'host';