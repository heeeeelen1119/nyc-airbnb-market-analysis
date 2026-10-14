-- 1. Market overview: count and price distribution by borough and room type.
SELECT borough, room_type, COUNT(*) AS listing_count,
       ROUND(AVG(price), 2) AS mean_price,
       PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price) AS median_price,
       PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY price) AS p25_price,
       PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY price) AS p75_price
FROM listings
GROUP BY borough, room_type
ORDER BY borough, room_type;

-- 2. Price premium: combination ranking after excluding sparse groups (< 30 listings).
WITH group_prices AS (
    SELECT borough, neighborhood, room_type, COUNT(*) AS listing_count,
           PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price) AS median_price
    FROM listings
    GROUP BY borough, neighborhood, room_type
    HAVING COUNT(*) >= 30
)
SELECT *, RANK() OVER (ORDER BY median_price DESC) AS median_price_rank_desc,
          RANK() OVER (ORDER BY median_price ASC) AS median_price_rank_asc
FROM group_prices
ORDER BY median_price_rank_desc;

-- 3. Neighborhood rank within borough by median price and listing count.
WITH neighborhood_metrics AS (
    SELECT borough, neighborhood, COUNT(*) AS listing_count,
           PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price) AS median_price
    FROM listings
    GROUP BY borough, neighborhood
)
SELECT *,
       RANK() OVER (PARTITION BY borough ORDER BY median_price DESC) AS median_price_rank,
       ROW_NUMBER() OVER (PARTITION BY borough ORDER BY listing_count DESC, neighborhood) AS listing_count_rank,
       PERCENT_RANK() OVER (PARTITION BY borough ORDER BY median_price) AS price_percent_rank
FROM neighborhood_metrics
ORDER BY borough, median_price_rank;

-- 4. Latest-review recency. This describes reviews, not occupancy.
SELECT
    CASE
        WHEN last_review IS NULL THEN 'missing'
        WHEN last_review >= DATE '2019-06-01' THEN 'recent (Jun-Jul 2019)'
        ELSE 'stale (before Jun 2019)'
    END AS review_recency,
    COUNT(*) AS listings,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS listing_share_pct
FROM listings
GROUP BY 1
ORDER BY listings DESC;

-- 4b. Cumulative review-date pattern by month.
WITH monthly_reviews AS (
    SELECT DATE_TRUNC('month', last_review)::date AS review_month, COUNT(*) AS listings
    FROM listings
    WHERE last_review IS NOT NULL
    GROUP BY 1
)
SELECT review_month, listings,
       SUM(listings) OVER (ORDER BY review_month) AS cumulative_listings
FROM monthly_reviews
ORDER BY review_month;

-- 5. Approximate host-name concentration (names are not unique host identifiers).
WITH host_counts AS (
    SELECT host_name, COUNT(*) AS listing_count
    FROM listings
    WHERE host_name IS NOT NULL
    GROUP BY host_name
), ranked_hosts AS (
    SELECT *, ROW_NUMBER() OVER (ORDER BY listing_count DESC, host_name) AS host_rank
    FROM host_counts
)
SELECT CASE WHEN host_rank <= 10 THEN 'top 10 names' ELSE 'all other names' END AS host_group,
       COUNT(*) AS distinct_names,
       SUM(listing_count) AS listings,
       ROUND(100.0 * SUM(listing_count) / SUM(SUM(listing_count)) OVER (), 2) AS listing_share_pct
FROM ranked_hosts
GROUP BY 1;

-- 6. Description signals with conditional aggregation.
SELECT room_type,
       AVG(price) AS mean_price,
       AVG(CASE WHEN mentions_view THEN price END) AS mean_price_with_view,
       AVG(CASE WHEN mentions_subway THEN price END) AS mean_price_with_subway,
       AVG(CASE WHEN mentions_spacious THEN price END) AS mean_price_with_spacious
FROM listings
GROUP BY room_type
ORDER BY room_type;
