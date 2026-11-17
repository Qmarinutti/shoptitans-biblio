-- Bibliothèque de plans Shop Titans — structure + sécurité (RLS)
-- À exécuter une fois dans Supabase > SQL Editor. Ré-exécutable sans casse.

-- ===== Catalogue des plans (public, rempli par 02_plans.sql) =====
create table if not exists public.plans (
  id          text primary key,          -- uid du jeu, ex. "eclipsesword"
  nom_fr      text not null,
  nom_en      text not null,
  categorie   text not null,             -- Armes, Armures, Accessoires, Pierres, Enchantements
  type_code   text not null,             -- ws, wa, ah...
  type_nom    text not null,             -- Épées, Haches...
  ordre_type  int  not null default 0,
  ordre       int  not null default 0,
  tier        int,
  origine     text                       -- pack, chest, special ou null
);

-- ===== Profil joueur (1 par compte) =====
create table if not exists public.profils (
  id         uuid primary key references auth.users(id) on delete cascade,
  pseudo     text not null unique check (char_length(pseudo) between 2 and 30),
  membre     boolean not null default false,   -- passe à true avec le code de guilde
  est_admin  boolean not null default false,
  cree_le    timestamptz not null default now()
);

-- ===== Plans possédés =====
create table if not exists public.possessions (
  joueur_id  uuid not null references public.profils(id) on delete cascade,
  plan_id    text not null references public.plans(id) on delete cascade,
  ajoute_le  timestamptz not null default now(),
  primary key (joueur_id, plan_id)
);
create index if not exists possessions_plan_idx on public.possessions(plan_id);

-- ===== Code de guilde (table privée, aucune lecture depuis le site) =====
create table if not exists public.config_privee (
  cle    text primary key,
  valeur text not null
);
insert into public.config_privee (cle, valeur)
values ('code_guilde', 'A-CHANGER')
on conflict (cle) do nothing;

-- ===== Fonctions =====
create or replace function public.est_membre() returns boolean
language sql stable security definer set search_path = public as $$
  select coalesce((select membre from public.profils where id = auth.uid()), false);
$$;

-- Crée le profil et vérifie le code de guilde en une fois.
create or replace function public.rejoindre_guilde(p_pseudo text, p_code text) returns text
language plpgsql security definer set search_path = public as $$
declare
  v_code text;
begin
  if auth.uid() is null then
    raise exception 'Non connecté';
  end if;
  select valeur into v_code from public.config_privee where cle = 'code_guilde';
  if p_code is distinct from v_code then
    raise exception 'Code de guilde incorrect';
  end if;
  insert into public.profils (id, pseudo, membre)
  values (auth.uid(), trim(p_pseudo), true)
  on conflict (id) do update set membre = true, pseudo = excluded.pseudo;
  return 'ok';
end;
$$;

revoke all on function public.rejoindre_guilde(text, text) from public, anon;
grant execute on function public.rejoindre_guilde(text, text) to authenticated;
grant execute on function public.est_membre() to authenticated;

-- ===== Sécurité ligne par ligne =====
alter table public.plans          enable row level security;
alter table public.profils        enable row level security;
alter table public.possessions    enable row level security;
alter table public.config_privee  enable row level security;   -- aucune policy = personne n'y accède via l'API

revoke all on public.config_privee from anon, authenticated;

drop policy if exists plans_lecture on public.plans;
create policy plans_lecture on public.plans for select using (true);

drop policy if exists profils_lecture on public.profils;
create policy profils_lecture on public.profils for select to authenticated
  using (public.est_membre() or id = auth.uid());

drop policy if exists profils_maj on public.profils;
create policy profils_maj on public.profils for update to authenticated
  using (id = auth.uid())
  with check (id = auth.uid());

-- un joueur ne peut pas se mettre admin/membre lui-même
revoke update on public.profils from authenticated;
grant update (pseudo) on public.profils to authenticated;
revoke insert, delete on public.profils from anon, authenticated;

drop policy if exists poss_lecture on public.possessions;
create policy poss_lecture on public.possessions for select to authenticated
  using (public.est_membre());

drop policy if exists poss_ajout on public.possessions;
create policy poss_ajout on public.possessions for insert to authenticated
  with check (joueur_id = auth.uid() and public.est_membre());

drop policy if exists poss_suppr on public.possessions;
create policy poss_suppr on public.possessions for delete to authenticated
  using (joueur_id = auth.uid());

revoke all on public.plans from anon, authenticated;
grant select on public.plans to anon, authenticated;
revoke all on public.possessions from anon;
revoke update on public.possessions from authenticated;
