sudo docker compose up -d galera1
sleep 32
sudo docker compose up -d galera2
sleep 32
sudo docker compose up -d galera3
sleep 32
sudo docker exec -it galera1 /opt/bitnami/mariadb/bin/mariadb -uroot -proot -e "
CREATE DATABASE IF NOT EXISTS app_db;
USE app_db;
CREATE TABLE IF NOT EXISTS counter (
  name VARCHAR(64) PRIMARY KEY,
  value BIGINT
);
INSERT INTO counter (name, value) VALUES ('web', 1);
SELECT * FROM counter;
"
sleep 10
sudo docker exec -it galera1 /opt/bitnami/mariadb/bin/mariadb -uroot -proot -e "USE app_db; SELECT * FROM counter;"
sudo docker exec -it galera2 /opt/bitnami/mariadb/bin/mariadb -uroot -proot -e "USE app_db; SELECT * FROM counter;"
sudo docker exec -it galera3 /opt/bitnami/mariadb/bin/mariadb -uroot -proot -e "USE app_db; SELECT * FROM counter;"

