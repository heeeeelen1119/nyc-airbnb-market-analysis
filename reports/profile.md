# Raw data profile

Generated with `python src/profile.py`.

## prices

- Shape: **25,209 rows × 3 columns**

| column | dtype | null_count | null_pct |
| --- | --- | --- | --- |
| listing_id | int64 | 0 | 0.00% |
| price | object | 0 | 0.00% |
| nbhood_full | object | 0 | 0.00% |

- Duplicate `listing_id` rows: **0**

### Top values: `price`

| value | count |
| --- | --- |
| 150 dollars | 982 |
| 100 dollars | 891 |
| 60 dollars | 717 |
| 50 dollars | 709 |
| 75 dollars | 691 |
| 65 dollars | 666 |
| 200 dollars | 618 |
| 80 dollars | 603 |
| 120 dollars | 576 |
| 70 dollars | 556 |
| 125 dollars | 554 |
| 90 dollars | 533 |
| 55 dollars | 512 |
| 85 dollars | 483 |
| 99 dollars | 455 |
| 45 dollars | 446 |
| 250 dollars | 432 |
| 95 dollars | 381 |
| 40 dollars | 377 |
| 110 dollars | 369 |

### Top values: `nbhood_full`

| value | count |
| --- | --- |
| Brooklyn, Bedford-Stuyvesant | 2209 |
| Brooklyn, Williamsburg | 1853 |
| Manhattan, Harlem | 1435 |
| Brooklyn, Bushwick | 1202 |
| Manhattan, Hell's Kitchen | 1119 |
| Manhattan, East Village | 866 |
| Manhattan, Upper East Side | 839 |
| Manhattan, Upper West Side | 775 |
| Brooklyn, Crown Heights | 752 |
| Manhattan, East Harlem | 672 |
| Manhattan, Midtown | 608 |
| Manhattan, Chelsea | 510 |
| Brooklyn, Greenpoint | 479 |
| Manhattan, Lower East Side | 461 |
| Queens, Astoria | 448 |
| Manhattan, Washington Heights | 437 |
| Manhattan, Financial District | 374 |
| Manhattan, West Village | 358 |
| Brooklyn, East Flatbush | 323 |
| Queens, Flushing | 319 |

## room_types

- Shape: **25,209 rows × 3 columns**

| column | dtype | null_count | null_pct |
| --- | --- | --- | --- |
| listing_id | int64 | 0 | 0.00% |
| description | object | 10 | 0.04% |
| room_type | object | 0 | 0.00% |

- Duplicate `listing_id` rows: **0**

### Top values: `description`

| value | count |
| --- | --- |
| <missing> | 10 |
| Home away from home | 10 |
| Loft Suite @ The Box House Hotel | 10 |
| Beautiful Brooklyn Brownstone | 5 |
| Brooklyn Apartment | 5 |
| Private Room | 5 |
| Harlem Gem | 5 |
| Private room | 5 |
| Brooklyn Garden Apartment | 4 |
| Cozy Room | 4 |
| Loft Suite @ Box House Hotel | 4 |
| New york Multi-unit building | 4 |
| Cozy Apartment | 4 |
| Private room with private bathroom | 4 |
| WEST VILLAGE Bohemian flat in neo-Tudor town house | 4 |
| Luminous Modern Apt Share for Young Professionals | 4 |
| AC Hotel New York Downtown-7 Nights Min | 3 |
| Harlem Hideaway | 3 |
| Cozy apartment by Central Park | 3 |
| Cozy, Friendly Apt Share for Young Professionals | 3 |

### Top values: `room_type`

| value | count |
| --- | --- |
| Entire home/apt | 8458 |
| Private room | 7241 |
| entire home/apt | 2665 |
| private room | 2248 |
| ENTIRE HOME/APT | 2143 |
| PRIVATE ROOM | 1867 |
| Shared room | 380 |
| shared room | 110 |
| SHARED ROOM | 97 |

## reviews

- Shape: **25,209 rows × 3 columns**

| column | dtype | null_count | null_pct |
| --- | --- | --- | --- |
| listing_id | int64 | 0 | 0.00% |
| host_name | object | 8 | 0.03% |
| last_review | object | 0 | 0.00% |

- Duplicate `listing_id` rows: **0**

### Top values: `host_name`

| value | count |
| --- | --- |
| Michael | 215 |
| Sonder (NYC) | 207 |
| David | 197 |
| John | 177 |
| Alex | 153 |
| Maria | 122 |
| Melissa | 110 |
| Daniel | 103 |
| Anna | 103 |
| Chris | 94 |
| Mike | 89 |
| Jessica | 89 |
| Jason | 88 |
| Andrew | 84 |
| Sarah | 77 |
| Michelle | 75 |
| Laura | 75 |
| James | 74 |
| Jennifer | 72 |
| Amy | 72 |

### Top values: `last_review`

| value | count |
| --- | --- |
| June 23 2019 | 1413 |
| July 01 2019 | 1359 |
| June 30 2019 | 1341 |
| June 24 2019 | 875 |
| July 07 2019 | 718 |
| July 02 2019 | 658 |
| June 22 2019 | 655 |
| June 16 2019 | 601 |
| July 05 2019 | 580 |
| July 06 2019 | 564 |
| June 29 2019 | 529 |
| June 21 2019 | 529 |
| July 03 2019 | 426 |
| June 19 2019 | 426 |
| June 25 2019 | 423 |
| June 20 2019 | 421 |
| June 28 2019 | 399 |
| January 01 2019 | 398 |
| June 26 2019 | 390 |
| June 09 2019 | 383 |

## Join coverage

| group | listing_ids |
| --- | --- |
| prices | 25209 |
| room_types | 25209 |
| reviews | 25209 |
| all three files | 25209 |
| in at least one file | 25209 |

The downstream cleaned table uses an inner join on `listing_id` after confirming the key is unique in each file. This retains 25,209 IDs shared across all three sources.
