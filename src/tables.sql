CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    alias VARCHAR(255) NOT NULL,
    date_registered BIGINT NOT NULL
);

CREATE TABLE meetings (
    meeting_id SERIAL PRIMARY KEY,
    creator_id BIGINT,
    aliases VARCHAR(1000) NOT NULL,
    time VARCHAR(1000),
    description TEXT,
    link_to_meeting VARCHAR(500) NOT NULL,
    notified60 BOOLEAN,
    notified15 BOOLEAN
);