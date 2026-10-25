-- This file creates all the tables for caddy-lite

-- remove any existing tables, run everytime to stop 'table already exists' prompts
DROP TABLE IF EXISTS consent_replies, message_reads, messages, parent_child, children, classes, users;

-- User table; table to store staff and parent logins
CREATE TABLE users (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    -- NO PASSWORDS STORED, ONLY A HASH
    password_hash TEXT NOT NULL,
    -- check correct input so that typos cannot be stored
    role TEXT NOT NULL CHECK (role IN('staff', 'parent'))
);

-- Classes table
CREATE TABLE classes (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL UNIQUE -- no two classes with the same name
);

-- Pupils table 
CREATE TABLE children (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    -- FIRST NAMED STORED ONLY FOR DATA PROTECTION
    first_name TEXT NOT NULL,
    -- FOREIGN KEY TO MATCH CHILD TO A CLASS 
    class_id INTEGER NOT NULL REFERENCES classes(id)

);

-- parent_child table to link parents to children (many to many relationships)
CREATE TABLE parent_child (
    -- on delete cascade, so that if the parents account is removed so are associated child accounts
    parent_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    child_id INTEGER NOT NULL REFERENCES children(id) ON DELETE CASCADE,

    -- COMPOSITE PRIMARY KEY (consisting of two columns, this ensures the same parent-child pair cannot be added twice)
    PRIMARY KEY (parent_id, child_id)
);

-- message posts (staff posts to whole class parents)
CREATE TABLE messages (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    class_id INTEGER NOT NULL REFERENCES classes(id), -- intended class
    author_id INTEGER NOT NULL REFERENCES users(id), -- post author (staff)
    title TEXT NOT NULL,
    body TEXT NOT NULL,

    -- messages which require a yes/no consent, will be applied if TRUE, otherwise it is a normal message
    has_consent BOOLEAN NOT NULL DEFAULT FALSE,

    -- date and time including timezone
    -- default now fills in current time automatically
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- table to records who has opened which message (staff view: read by 17 out of 24 parents)
CREATE TABLE message_reads (
    message_id INTEGER NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    read_At TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- each message read by a person is recorded once
    PRIMARY KEY (message_id, user_id)
);

-- table to store parental consent replies
CREATE TABLE consent_replies (
    message_id INTEGER NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    child_id INTEGER NOT NULL REFERENCES children(id) ON DELETE CASCADE,
    parent_id INTEGER NOT NULL REFERENCES users(id), -- who answered
    answer BOOLEAN NOT NULL, -- true - yes, false - no
    replied_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- one answer per child. child key is primary so that conflicted answers cannot be given by two children
    PRIMARY KEY (message_id, child_id)
);




