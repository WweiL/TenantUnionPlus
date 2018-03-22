drop table if exists course;
create table course (
  subject varchar(5) not NULL 'CS',
  course_number integer(3) not NULL 999,
  name char(30) not NULL 'intro',
  info char(100) not NULL 'none',
  credit integer(1) not NULL 0,
  PRIMARY KEY (subject,course_number)
);
