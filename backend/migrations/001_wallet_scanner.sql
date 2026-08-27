-- Apply with the project's migration process before enabling wallet scans.
-- This migration is intentionally explicit; do not auto-create production tables at startup.

CREATE TABLE IF NOT EXISTS scam_wallets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    address VARCHAR(42) NOT NULL UNIQUE,
    chain VARCHAR(20) NOT NULL,
    category VARCHAR(64) NOT NULL,
    severity INTEGER NOT NULL DEFAULT 100 CHECK (severity BETWEEN 0 AND 100),
    source VARCHAR(128) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_scam_wallets_chain_address
    ON scam_wallets (chain, address);

CREATE TABLE IF NOT EXISTS scans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    chain VARCHAR(20) NOT NULL,
    address VARCHAR(42) NOT NULL,
    score INTEGER CHECK (score IS NULL OR score BETWEEN 0 AND 100),
    risk VARCHAR(32) NOT NULL,
    confidence VARCHAR(16) NOT NULL,
    status VARCHAR(32) NOT NULL,
    engine_version VARCHAR(32) NOT NULL,
    evidence JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_scans_user_created
    ON scans (user_id, created_at DESC);
