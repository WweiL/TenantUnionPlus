drop table if exists student;
create table student(
  NetID char(10) not NULL 'siebel999'
  name varchar(20) not NULL 'Wallace',
  gender char(10) not NULL 'none',
  age integer(2) not NULL 0,
  info varchar(140) not NULL 'none',
  major char(20) not NULL 'CS',
  mailbox varchar(30) not NULL 'none',
  phone_num integer(12) not NULL 0,
  PRIMARY KEY (NetID)
);
