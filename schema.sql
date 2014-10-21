drop table if exists user;
create table user (
    id integer primary key autoincrement,
    username text not null,
    password text not null,
    honor integer default 0,
    complain text,
    nicecard integer not null default 0,
    noticenum integer not null default 0,
    notification text,
    draft text,
    rubbish text
);

drop table if exists item;
create table item (
    id integer primary key autoincrement,
    username text not null,
    content text not null,
    nicecard integer default 0,
    is_anonymity integer default 0,
    state integer default 0,
    time text not null,
    position text not null,
    dealername text
);

drop table if exists history;
create table history (
    id integer primary key autoincrement,
    username_1 text not null,
    username_2 text not null,
    content_1 text not null,
    content_2 text not null,
    time integer not null
);