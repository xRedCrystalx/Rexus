/*
Command for creating a database user. Due to privacy and security, accounts needs to be set/created manually.
*/

-- Can replace `localhost` with `%` for all connections
-- Within subnet: 192.168.1.%
-- Whitin private range: 192.168.%
CREATE USER 'custom-username'@'localhost' IDENTIFIED BY 'custom-password';
-- To remove user, use DROP command instead of CREATE

-- For all privileges use `ALL PRIVILEGES`
-- For all databases and tables use `*.*`
GRANT {privileges} ON {db.table} TO 'custom-username'@'localhost';
-- To revoke privileges, use REVOKE command instead of GRANT

FLUSH PRIVILEGES;

-- Login cmd: mariadb -u custom-username -p

/*
MariaDB by default only listens to local host - 127.0.0.0
edit `bind-address: 0.0.0.0` in `/etc/mysql/mariadb.conf.d/50-server.cnf`
make sure to `service mariadb restart`
*/