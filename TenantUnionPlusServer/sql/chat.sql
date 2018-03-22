drop table if exists comment;
create table comment (
  NetID1 varchar(10) not NULL 'siebel999',
  NetID2 varchar(10) not NULL 'siebel999'
  timet DATETIME not NULL '1000-01-01 12:34:56',
  word char(140) not NULL 'like',
  PRIMARY KEY (NetID1, NetID2,timet)
);
