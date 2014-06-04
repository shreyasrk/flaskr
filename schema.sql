drop table if exists entries;
create table entries (
    id integer primary key autoincrement,
    title not null,
    text not null
);
