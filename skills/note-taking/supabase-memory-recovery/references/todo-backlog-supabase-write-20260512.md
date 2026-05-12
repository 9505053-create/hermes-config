# Todo / Backlog Write Pattern — 2026-05-12

## Trigger

Scott asked to list phase-2 skill-conversion candidates as a durable todo and write the record to both local disk log and Supabase.

## Local log target

File updated:

`/home/chien/.hermes/memories/RECOVERY_LOG_20260512_0427_skill_conversion.md`

Append a concise section containing:

- Task name
- Status and priority
- Candidate list
- Conditional candidates
- Supabase target tables

## Supabase discovery

Check containers:

```bash
docker ps -a --format '{{.Names}} | {{.Status}} | {{.Image}}' | grep -iE 'supabase|postgres|kong|studio|pooler|gotrue'
```

Check schema:

```bash
docker exec -u postgres supabase-db psql -d postgres -X -A -F '|' -c "SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema='public' AND table_name IN ('hermes_todos','hermes_knowledge') ORDER BY table_name; SELECT table_name, column_name, data_type, is_nullable FROM information_schema.columns WHERE table_schema='public' AND table_name IN ('hermes_todos','hermes_knowledge') ORDER BY table_name, ordinal_position;"
```

Check constraints before deciding whether `ON CONFLICT` is valid:

```bash
docker exec -u postgres supabase-db psql -d postgres -X -A -F '|' -c "SELECT conname, contype, pg_get_constraintdef(c.oid) FROM pg_constraint c JOIN pg_class t ON c.conrelid=t.oid JOIN pg_namespace n ON t.relnamespace=n.oid WHERE n.nspname='public' AND t.relname IN ('hermes_knowledge','hermes_todos') ORDER BY t.relname, contype, conname;"
```

## Idempotent write pattern without UNIQUE constraints

Use this when natural keys such as `hermes_todos.task` or `hermes_knowledge.title` do not have unique constraints:

```sql
BEGIN;

UPDATE public.hermes_todos
SET status = '<status>', priority = '<priority>', updated_at = now()
WHERE task = '<task>';

INSERT INTO public.hermes_todos (task, status, priority, created_at, updated_at)
SELECT '<task>', '<status>', '<priority>', now(), now()
WHERE NOT EXISTS (
  SELECT 1 FROM public.hermes_todos WHERE task = '<task>'
);

UPDATE public.hermes_knowledge
SET module = 'BACKLOG',
    content = $$<markdown summary>$$,
    tags = ARRAY['todo','backlog','skills'],
    updated_at = now()
WHERE title = '<title>';

INSERT INTO public.hermes_knowledge (module, title, content, tags, updated_at)
SELECT 'BACKLOG', '<title>', $$<markdown summary>$$, ARRAY['todo','backlog','skills'], now()
WHERE NOT EXISTS (
  SELECT 1 FROM public.hermes_knowledge WHERE title = '<title>'
);

COMMIT;
```

## Verification query

```bash
docker exec -u postgres supabase-db psql -d postgres -X -A -F '|' -c "SELECT id, task, status, priority, created_at, updated_at FROM public.hermes_todos WHERE task = '<task>'; SELECT id, module, title, array_to_string(tags, ',') AS tags, char_length(content) AS content_chars, updated_at FROM public.hermes_knowledge WHERE title = '<title>';"
```

## Pitfalls

- Do not use `ON CONFLICT` unless the conflict target has a matching UNIQUE or PRIMARY KEY constraint.
- Keep the Supabase summary compact; local markdown can hold more detail.
- Read back both the local file and database rows before reporting success.
