CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(320) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    locale VARCHAR(5) NOT NULL DEFAULT 'en' CHECK (locale IN ('en','pl','de')),
    onboarding_completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS plans (
    id VARCHAR(32) PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    monthly_price_cents INTEGER NOT NULL CHECK (monthly_price_cents >= 0),
    daily_scan_limit INTEGER NOT NULL CHECK (daily_scan_limit > 0),
    monthly_scan_limit INTEGER NOT NULL CHECK (monthly_scan_limit >= daily_scan_limit),
    active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_id VARCHAR(32) NOT NULL REFERENCES plans(id),
    status VARCHAR(32) NOT NULL,
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_status ON subscriptions(user_id, status);

CREATE TABLE IF NOT EXISTS usage_counters (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    usage_date DATE NOT NULL,
    scan_count INTEGER NOT NULL DEFAULT 0 CHECK (scan_count >= 0),
    PRIMARY KEY (user_id, usage_date)
);

INSERT INTO plans (id, name, monthly_price_cents, daily_scan_limit, monthly_scan_limit)
VALUES ('free', 'Free', 0, 10, 300), ('pro', 'Pro', 999, 50, 500)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    monthly_price_cents = EXCLUDED.monthly_price_cents,
    daily_scan_limit = EXCLUDED.daily_scan_limit,
    monthly_scan_limit = EXCLUDED.monthly_scan_limit;
