# NYC Airbnb market: 2019 listing snapshot

## What the data says

The cleaned analysis covers **25,202** NYC Airbnb listings with valid positive nightly prices. Prices vary widely: the mean is **$141.82**, but the median is only **$105.00**. The gap matters because a small number of expensive listings pull the average upward, so this report uses medians to compare typical prices.

Manhattan has the highest typical price, with a median of **$149** per night. Brooklyn's median is **$95**, Queens' is **$70**, Staten Island's is **$71**, and the Bronx's is **$65**. Among borough-neighborhood-room-type groups with at least 30 listings, the highest median is **$350** for entire homes/apartments in Tribeca, Manhattan. The lowest is **$35** for shared rooms in Bedford-Stuyvesant, Brooklyn.

Room type is strongly associated with price. The median is **$159** for entire homes/apartments, **$70** for private rooms, and **$41** for shared rooms. In a descriptive model that accounts for borough and simple description features, private rooms are associated with an approximately **53.6%** lower price than entire homes/apartments, while shared rooms are associated with an approximately **71.3%** lower price. The model has an R-squared of **0.530** across **25,192** listings. It summarizes observed relationships; it does not establish that room type causes price changes.

Latest-review dates cluster late in the observed period: **68.73%** of listings have a most recent review in June or July 2019, while **31.27%** were last reviewed before June. This is only review recency—not occupancy, demand, or revenue. The ten most frequently occurring host names appear on **5.88%** of listings, but this is an approximation because the data has names rather than unique host IDs.

## Limits

This is a 2019, listing-level snapshot without precise coordinates, occupancy, bookings, size, amenities, or a unique host key. It cannot show the current market or support causal claims. Extremely high prices were retained and flagged rather than deleted; the median comparisons reduce, but do not eliminate, their influence on interpretation.

## Hypotheses worth testing

1. Test whether professionally managed listings explain the high concentration of expensive entire homes in Manhattan, using a dataset with a unique host ID and management status.
2. Test whether proximity to transit explains the observed text association for descriptions mentioning “subway,” using coordinates and walking-distance measures.
3. Test whether review recency predicts bookings or revenue using longitudinal reservation data; the present data cannot answer that question.
