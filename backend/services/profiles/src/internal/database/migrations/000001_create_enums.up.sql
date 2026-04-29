CREATE TYPE gender AS ENUM (
    'male',
    'female'
);

CREATE TYPE relationship_type AS ENUM (
    'friendship',
    'relationship',
    'networking'
);

CREATE TYPE moderation_status AS ENUM (
    'pending',
    'approved',
    'rejected'
);