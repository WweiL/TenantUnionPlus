drop table if exists housing_building;
create table housing_building (
  building_name varchar(20) not NULL 'home',
  location varchar(40) not NULL 'home',
  info char(100) not NULL 'none',
  shop bit not NULL 0,
  dining_hall bit not NULL 0,
  gym bit not NULL 0,
  PRIMARY KEY (building_name)
);
