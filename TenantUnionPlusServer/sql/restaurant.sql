DROP TABLE if exists restaurant;
CREATE TABLE restaurant (
  building_name varchar(20) not NULL default 'home',
  lat FLOAT(20) NOT NULL,
  lng FLOAT(20) NOT NULL,
  PRIMARY KEY (building_name)
);
