"""Table definitions and shared constants for Local Loop (Puvanan)."""

# --- Listing / exchange statuses -------------------------------------------
LISTING_AVAILABLE = "available"
LISTING_RESERVED = "reserved"
LISTING_COMPLETED = "completed"

EXCHANGE_RESERVED = "reserved"
EXCHANGE_COMPLETED = "completed"
EXCHANGE_CANCELLED = "cancelled"

# --- Categories --------------------------------------------------------------
# The first four are the weekly challenge rotation (your team can change them).
CHALLENGE_ROTATION = [
    "Books & Stationery",
    "Clothing",
    "Household Items",
    "Recyclables",
]
CATEGORIES = CHALLENGE_ROTATION + ["Other"]

# --- Matching ----------------------------------------------------------------
DEFAULT_RADIUS_KM = 2.0

# --- SQLite schema -----------------------------------------------------------
SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    latitude    REAL NOT NULL,
    longitude   REAL NOT NULL,
    created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS challenges (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    week_start  TEXT NOT NULL UNIQUE,   -- Monday, YYYY-MM-DD
    week_end    TEXT NOT NULL,          -- Sunday, YYYY-MM-DD
    category    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS listings (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id    INTEGER NOT NULL REFERENCES users(id),
    title       TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    category    TEXT NOT NULL,
    latitude    REAL NOT NULL,
    longitude   REAL NOT NULL,
    status      TEXT NOT NULL DEFAULT 'available',
    created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS exchanges (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    listing_id        INTEGER NOT NULL REFERENCES listings(id),
    giver_id          INTEGER NOT NULL REFERENCES users(id),
    receiver_id       INTEGER NOT NULL REFERENCES users(id),
    status            TEXT NOT NULL DEFAULT 'reserved',
    featured_category TEXT,             -- challenge category at completion time
    points_awarded    INTEGER NOT NULL DEFAULT 0,
    created_at        TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at      TEXT
);

-- A listing can have only one active (reserved/completed) exchange.
CREATE UNIQUE INDEX IF NOT EXISTS idx_one_active_exchange
    ON exchanges(listing_id) WHERE status IN ('reserved', 'completed');

-- UNIQUE(exchange_id) guarantees each exchange is rewarded only once.
CREATE TABLE IF NOT EXISTS point_transactions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    exchange_id INTEGER NOT NULL UNIQUE REFERENCES exchanges(id),
    points      INTEGER NOT NULL,
    reason      TEXT NOT NULL DEFAULT '',
    created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""