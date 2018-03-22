drop table if exists classroom;
create table classroom (
  building_name varchar(20) not NULL 'home',
  room integer(4) not NULL 0000,
  location varchar(40) not NULL 'home',
  info char(100) not NULL 'none',
  PRIMARY KEY (building_name,room)
);
