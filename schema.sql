drop table if exists event;
create table event (
  id integer primary key autoincrement,
  description text not null,
  event_date date,
  event_time time,
  address text,
  minors boolean,
  cover smallint,
  lat text,
  lng text
);