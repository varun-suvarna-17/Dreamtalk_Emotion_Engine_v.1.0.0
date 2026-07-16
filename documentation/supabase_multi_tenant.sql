create table if not exists avatar_config (
    user_id text not null,
    avatar_id text not null,

    name text default 'Alex',
    profession text default 'Software Architect',
    relationship text default 'Friend',
    tone text default 'casual',
    traits jsonb not null default '{}'::jsonb,

    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),

    primary key (user_id, avatar_id)
);

create table if not exists brain_output (
    id uuid primary key default gen_random_uuid(),

    user_id text not null,
    avatar_id text not null,
    session_id text,
    turn_id integer,

    timestamp timestamptz not null default now(),
    response_text text not null,
    sentiment_emotion jsonb not null default '{}'::jsonb,

    created_at timestamptz not null default now()
);

create index if not exists idx_brain_output_user_avatar
on brain_output (user_id, avatar_id);

create index if not exists idx_brain_output_user_avatar_time
on brain_output (user_id, avatar_id, timestamp desc);
