-- ==============================================================================
-- DevHamid Portfolio - Supabase Database Schema
-- Production SQL setup for Cloud PostgreSQL
-- Paste this script into your Supabase Dashboard -> SQL Editor and click 'Run'.
-- ==============================================================================

-- 1. Site Analytics Table (Single-row persistent counter)
CREATE TABLE IF NOT EXISTS public.site_analytics (
    id INT PRIMARY KEY DEFAULT 1 CHECK (id = 1),
    total_visits BIGINT NOT NULL DEFAULT 1482,
    last_visit_at TIMESTAMPTZ DEFAULT NOW()
);

-- Seed baseline counter if not already initialized
INSERT INTO public.site_analytics (id, total_visits, last_visit_at)
VALUES (1, 1482, NOW())
ON CONFLICT (id) DO NOTHING;

-- 2. Visitor Sessions Table (Deduplication across 24h windows)
CREATE TABLE IF NOT EXISTS public.visitor_sessions (
    id BIGSERIAL PRIMARY KEY,
    visitor_hash VARCHAR(64) NOT NULL,
    ip_hash VARCHAR(64) NOT NULL,
    user_agent VARCHAR(255),
    date_bucket DATE NOT NULL,
    visited_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_visitor_daily UNIQUE(visitor_hash, date_bucket)
);

CREATE INDEX IF NOT EXISTS idx_visitor_sessions_lookup 
ON public.visitor_sessions(visitor_hash, date_bucket);

-- 3. Contact Inquiries Table (Archive of messages sent through portfolio form)
CREATE TABLE IF NOT EXISTS public.contact_messages (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL,
    message TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'delivered',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Enable Row Level Security (RLS)
ALTER TABLE public.site_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.visitor_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.contact_messages ENABLE ROW LEVEL SECURITY;

-- 5. Public Access Policies for Anon / Service Roles
CREATE POLICY "Allow public read access to analytics" 
ON public.site_analytics FOR SELECT TO anon, authenticated USING (true);

CREATE POLICY "Allow public update to analytics" 
ON public.site_analytics FOR UPDATE TO anon, authenticated USING (true);

CREATE POLICY "Allow insert into visitor_sessions" 
ON public.visitor_sessions FOR INSERT TO anon, authenticated WITH CHECK (true);

CREATE POLICY "Allow read of visitor_sessions" 
ON public.visitor_sessions FOR SELECT TO anon, authenticated USING (true);

CREATE POLICY "Allow insert into contact_messages" 
ON public.contact_messages FOR INSERT TO anon, authenticated WITH CHECK (true);

COMMENT ON TABLE public.site_analytics IS 'Persistent visitor counter for DevHamid portfolio';
COMMENT ON TABLE public.visitor_sessions IS 'Deduplicated visitor session logs';
COMMENT ON TABLE public.contact_messages IS 'Contact form inquiries received via portfolio';
