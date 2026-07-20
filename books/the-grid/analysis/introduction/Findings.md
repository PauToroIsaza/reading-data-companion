# Introduction Chapter: Analysis Findings

## Dataset: EAGLE-I Outage Data

Source: `/data/raw/introduction/Outage_Dataset/`

### Data collection limitation: 2014

**Use 2015 and beyond for analysis.** The 2014 data only covers November–December (data collection began Nov 1, 2014). This results in:

- ~13.5k records in 2014 vs ~116k+ in subsequent years
- 0 records for Jan–Oct 2014
- Fewer states (46) and counties (987) compared to 2015 (49 states, 1,406 counties)

Exclude 2014 from year-over-year comparisons to avoid misleading trends.

### How customer_weighted_hours is calculated

The `merged` files contain individual outage events with:
- `duration` — outage length in hours
- `min_customers`, `max_customers`, `mean_customers` — customer impact sampled at regular intervals during the outage

Because outages are sampled over time (not a single snapshot), there's no single "true" customer count. EAGLE-I uses `mean_customers` as the representative value.

**Formula (verified by comparing merged → group files):**

```
customer_weighted_hours = sum(duration × mean_customers)
```

This approximates the area under the "customers affected over time" curve.

### Metric decision for visualization

**Primary metric:** Customer-hours at county level per year

```
county_customer_hours = sum(duration × mean_customers) for all outages in county/year
```

**Normalized metric:** Customer-hours per capita

```
county_customer_hours_per_capita = county_customer_hours / county_population
```

The per-capita version allows fair comparison across counties of different sizes. A county of 10k people with 50k customer-hours experienced worse outages than a county of 500k with the same total.

### Open questions

- [ ] Source for county population data (Census ACS?)
- [ ] How to handle zip code lookup (zip → FIPS crosswalk needed)
