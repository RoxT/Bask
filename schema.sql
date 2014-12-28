drop table if exists event;
create table event (
  id integer primary key autoincrement,
  band_id integer,
  description text,
  event_date date,
  event_time time,
  address text,
  minors boolean,
  cover smallint,
  lat text,
  lng text
);