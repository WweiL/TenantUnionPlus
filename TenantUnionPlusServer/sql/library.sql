DROP TABLE if exists restaurant;
CREATE TABLE library (
  building_name varchar(20) not NULL 'home',
  lat FLOAT(20) NOT NULL,
  lng FLOAT(20) NOT NULL,
  PRIMARY KEY (building_name)
);
