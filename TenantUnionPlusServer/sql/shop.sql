drop table if exists shop;
create table shop(
  building_name varchar(20) not NULL 'home',
  location varchar(40) not NULL 'home',
  info char(100) not NULL 'none',
  PRIMARY KEY (building_name)
);
