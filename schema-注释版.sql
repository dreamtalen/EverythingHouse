drop table if exists user;
# 用户信息表
create table user (
    id integer primary key autoincrement,
    # 编号
    username text not null,
    # 用户名
    password text not null,
    # 密码
    honor integer default 0,
    # 个人信誉度
    complain text,
    # 投诉内容和时间
    nicecard integer not null default 0,
    # 好人卡数量
    noticenum integer not null default 0,
    # 个人通知的数量
    notification text,
    # 私信和公共通知
    draft text,
    # 草稿箱的内容
    rubbish text,
    # 垃圾筒的内容
);

drop table if exists item;
# 单子列表
create table item (
    id integer primary key autoincrement,
    # 编号
    username text not null,
    # 投条人
    content text not null,
    # 单子说明
    nicecard integer default 0,
    # 额外需要支付的好人卡
    is_anonymity integer default 0,
    # 是否是匿名发布
    state integer default 0,
    # 交易状态，新单子、交易中、执行中
    time text not null,
    # 生成时间
    position text not null
    # 地点
);

drop table if exists history;
# 单子历史
create table history (
    id integer primary key autoincrement,
    # 编号
    username_1 text not null,
    # 投条人
    username_2 text not null,
    # 接单人
    content_1 text not null,
    # 单子1说明
    content_2 text not null,
    # 单子2说明
    time integer not null
    # 交易完成时间
);