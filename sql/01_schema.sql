-- PostgreSQL analytical table for the cleaned NYC Airbnb listings.
DROP TABLE IF EXISTS listings;

CREATE TABLE listings (
    listing_id BIGINT PRIMARY KEY,
    price NUMERIC(10, 2) NOT NULL CHECK (price > 0),
    nbhood_full TEXT NOT NULL,
    borough TEXT NOT NULL,
    neighborhood TEXT NOT NULL,
    description TEXT,
    room_type TEXT NOT NULL CHECK (room_type IN ('Entire home/apt', 'Private room', 'Shared room')),
    host_name TEXT,
    last_review DATE,
    is_extreme_price BOOLEAN NOT NULL,
    description_length INTEGER,
    mentions_private BOOLEAN NOT NULL,
    mentions_view BOOLEAN NOT NULL,
    mentions_subway BOOLEAN NOT NULL,
    mentions_cozy BOOLEAN NOT NULL,
    mentions_spacious BOOLEAN NOT NULL
);

CREATE INDEX idx_listings_borough_room_type ON listings (borough, room_type);
CREATE INDEX idx_listings_neighborhood ON listings (borough, neighborhood);
CREATE INDEX idx_listings_last_review ON listings (last_review);
