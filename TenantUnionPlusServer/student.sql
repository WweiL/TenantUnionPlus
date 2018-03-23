drop table if exists student;
create table student(
<<<<<<< HEAD
  NetID char(10) not NULL default 'siebel999',
  name varchar(20) not NULL default 'notSet',
  gender char(10) not NULL default 'notSet',
  age integer(2) not NULL default 0,
  info varchar(140) not NULL default 'notSet',
  major char(20) not NULL default 'notSet',
  mailbox varchar(30) not NULL default 'notSet',
  phone_num integer(12) not NULL default 0,
=======
  NetID char(10) not NULL 'siebel999',
  name varchar(20) not NULL 'Wallace',
  gender char(10) not NULL 'none',
  age integer(2) not NULL 0,
  info varchar(140) not NULL 'none',
  major char(20) not NULL 'CS',
  mailbox varchar(30) not NULL 'none',
  phone_num integer(12) not NULL 0,
>>>>>>> 95403dec5446928402196c430cd25effda9cbda0
  PRIMARY KEY (NetID)
);
