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

### Event type normalization needed

The raw `Event Type` field has 75 unique values with significant inconsistencies:

- **Whitespace/case issues**: `Vandalism` vs `Vandalism `, `Suspicious Activity` vs `Suspicious activity`
- **Typos**: `Sever Weather`, `Transmisison`
- **2023 schema change**: Uses leading dashes and compound types (`- Physical attack - Vandalism - Suspicious activity`)
- **Overlapping categories**: `Severe Weather`, `Weather`, `Natural Disaster` all refer to weather events

**Proposed normalization** uses one-hot encoding with 15 categories, allowing events to belong to multiple categories (e.g., `Severe Weather/Transmission Interruption` → `[severe_weather, transmission]`).

### "Natural Disaster" is predominantly weather

The "Natural Disaster" and "Weather or natural disaster" event types are **weather-skewed**, not earthquake/seismic events:

- **Seasonal clustering**: 75% of events occur June–October (hurricane/storm season)
- **Geographic pattern**: Top states are Texas, California, Georgia — hurricane and wildfire areas
- **Event scale**: Largest events affect 100+ counties (hurricane behavior, not earthquakes)
- **California events align with wildfires**: Nov 2018 (Camp Fire), Jul–Aug 2018 (Carr/Mendocino), Sept 2020 (August Complex)

Earthquakes rarely cause widespread prolonged outages at this scale. Treat this category as functionally equivalent to `severe_weather`.

### Open questions

- [ ] Source for county population data (Census ACS?)
- [ ] How to handle zip code lookup (zip → FIPS crosswalk needed)
- [ ] Finalize event type normalization mapping and create processing script
