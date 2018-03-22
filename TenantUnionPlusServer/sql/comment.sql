drop table if exists comment;
create table comment (
  NetID varchar(10) not NULL 'siebel999',
  timet DATETIME not NULL '1000-01-01 12:34:56',
  word char(140) not NULL 'like',
  score Integer(2) not NULL 0,
  PRIMARY KEY (NetID, timet)
);
