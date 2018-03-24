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
