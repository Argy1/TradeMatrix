-- Private Storage bucket for trained model files (docs/02, docs/03).
-- No storage policies are added, so only the backend's service-role key can read or write it.
insert into storage.buckets (id, name, public)
values ('models', 'models', false)
on conflict (id) do nothing;
