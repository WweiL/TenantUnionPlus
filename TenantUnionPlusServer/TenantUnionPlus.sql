drop table if exists student;
create table student(
  NetID char(10) not NULL default 'siebel999',
  name varchar(20) not NULL default 'Wallace',
  gender char(10) not NULL default 'none',
  age integer(2) not NULL default 0,
  info varchar(140) not NULL default 'none',
  major char(20) not NULL default 'CS',
  mailbox varchar(30) not NULL default 'none',
  phone_num integer(12) not NULL default 0,

  PRIMARY KEY (NetID)
);

drop table if exists room;
create table room (
  building_name varchar(20) not NULL default 'home',
  location varchar(40) not NULL default'home',
  price integer(4) not NULL default 0,
  bedroom_num integer(1) not NULL default 0,
  bath_num integer(1) not NULL default 0,
  furnished bit not NULL default 0,
  air_condition bit not NULL default 0,
  dishwasher bit not NULL default 0,
  parking bit not NULL default 0,
  pet bit not NULL default 0,
  water bit not NULL default 0,
  internet bit not NULL default 0,
  tv bit not NULL default 0,
  electricity BIT NOT NULL DEFAULT 0,
  url char(100),
  lat FLOAT(20),
  lng FLOAT(20),
  rscore FLOAT(20) NOT NULL,
  gymscore FLOAT(20) NOT NULL,
  marketscore FLOAT(20) NOT NULL,
  libraryscore FLOAT(20) NOT NULL,
  north integer(1) default -1,
  out integer(1) default -1,
  id INTEGER(5),
  PRIMARY KEY (id)
);

DROP TABLE IF EXISTS roomImage;
CREATE TABLE roomImage(
    img0 VARCHAR(150),
    img1 VARCHAR(150),
    img2 VARCHAR(150),
    img3 VARCHAR(150),
    img4 VARCHAR(150),
    id INTEGER(5),
    PRIMARY KEY (id)
);

drop table if exists gym;
create table gym (
  building_name varchar(20) not NULL default 'home',
  location varchar(40) not NULL default 'home',
  info char(100) not NULL default 'none',
  PRIMARY KEY (building_name)
);

DROP TABLE if exists likes;
create table likes (
  location varchar(20) not NULL default 'home',
  NetID varchar(40) not NULL default 'siebel999',
  word char(140) default 'like',
  likeornot integer(1) default -1,
  PRIMARY KEY (location, NetID)
);

DROP TABLE if exists library;
CREATE TABLE library (
  building_name varchar(20) NOT NULL default 'main lib',
  lat FLOAT(20) NOT NULL,
  lng FLOAT(20) NOT NULL,
  PRIMARY KEY (building_name)
);

DROP TABLE if exists restaurant;
CREATE TABLE restaurant (
  building_name varchar(20) NOT NULL default 'DiaoSiZhiJia',
  lat FLOAT(20) NOT NULL,
  lng FLOAT(20) NOT NULL
);

DROP TABLE if exists supermarket;
CREATE TABLE supermarket (
  building_name varchar(20) NOT NULL default 'countymarket',
  lat FLOAT(20) NOT NULL,
  lng FLOAT(20) NOT NULL
);

DROP TABLE if exists gym;
CREATE TABLE gym (
  building_name varchar(20) NOT NULL default 'arc',
  lat FLOAT(20) NOT NULL,
  lng FLOAT(20) NOT NULL
);
