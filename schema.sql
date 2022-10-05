
create table session (
    id serial primary key,
    chat_id integer unique,
    user_id integer,
    first_name text,
    last_name text,
    username text,
    state_path text, -- path to the state file for this session
    created timestamp default(current_timestamp at time zone 'utc'),
    last_updated timestamp default(current_timestamp at time zone 'utc')
);

create table message (
    id serial primary key,
    session_id integer references session,
    message_id integer,
    message_type text, -- request/response/other
    content_type text, -- text/image
    message text,
    image_path text, -- path to the image if image is sent
    reply_to integer references message,
    created timestamp default(current_timestamp at time zone 'utc')
);

create table task (
    id serial primary key,
    session_id integer,
    message_id integer references message,
    message text,
    status text default 'pending', -- pending, inprogress, completed, archived
    exit_status integer,
    stdout text,
    stderr text,
    image_path text,
    reply_id integer, -- id of the reply message

    t_created timestamp default(current_timestamp at time zone 'utc'),
    t_started timestamp,
    t_completed timestamp,
    t_sent timestamp
);
