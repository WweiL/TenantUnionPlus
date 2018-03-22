drop table if exists restaurant;
create table restaurant (
  building_name varchar(20) not NULL 'home',
  location varchar(40) not NULL 'home',
  info char(100) not NULL 'none',
  PRIMARY KEY (building_name)
);
