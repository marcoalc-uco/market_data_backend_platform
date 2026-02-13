# Grafana Visualization Guide

## Overview

This guide explains how to use Grafana to visualize market data from the Market Data Backend Platform. The dashboard provides real-time insights into price evolution, trading volumes, and latest market prices grouped by asset type.

---

## Dashboard Access

Once the Docker Compose environment is running:

1. Open your browser and navigate to: `http://localhost:3000`
2. Login with default credentials:
   - **Username**: `admin`
   - **Password**: `admin` (change this in production!)
3. Navigate to **Dashboards** → **Market Data - Multi-Instrument by Asset Type**

---

## Dashboard Overview

### Main Dashboard: Market Data - Multi-Instrument by Asset Type

The dashboard is designed to display multiple instruments grouped by asset type (STOCK, INDEX, CRYPTO, etc.).

**Key Features:**

- **Asset Type Selector**: Dropdown variable to filter by asset type
- **Time Range Picker**: Adjust the time window for analysis
- **Auto-Refresh**: Dashboard refreshes every 30 seconds

---

## Dashboard Panels

### 1. Price Evolution by Asset Type

**Type**: Time Series Chart
**Description**: Displays closing prices over time for all instruments of the selected asset type.

**Features:**

- Smooth line interpolation
- Multi-series comparison
- Legend with last and mean values
- Hover tooltip for detailed values

**SQL Query:**

```sql
SELECT
  mp.timestamp AS time,
  mp.close AS value,
  i.symbol AS metric
FROM market_prices mp
JOIN instruments i ON mp.instrument_id = i.id
WHERE
  i.asset_type = '${asset_type}'
  AND mp.timestamp >= $__timeFrom()
  AND mp.timestamp <= $__timeTo()
ORDER BY mp.timestamp ASC
```

---

### 2. Trading Volume by Asset Type

**Type**: Bar Chart
**Description**: Shows trading volume over time for instruments of the selected asset type.

**Features:**

- Bar visualization for volume data
- Sum and mean calculations in legend
- Synchronized time axis with price chart

**SQL Query:**

```sql
SELECT
  mp.timestamp AS time,
  mp.volume AS value,
  i.symbol AS metric
FROM market_prices mp
JOIN instruments i ON mp.instrument_id = i.id
WHERE
  i.asset_type = '${asset_type}'
  AND mp.timestamp >= $__timeFrom()
  AND mp.timestamp <= $__timeTo()
ORDER BY mp.timestamp ASC
```

---

### 3. Latest Prices Table

**Type**: Table
**Description**: Displays the most recent OHLCV data for each instrument.

**Columns:**

- Symbol
- Name
- Asset Type
- Timestamp (latest)
- Open, High, Low, Close (color-coded)
- Volume

**SQL Query:**

```sql
SELECT
  i.symbol,
  i.name,
  i.asset_type,
  mp.timestamp,
  mp.open,
  mp.high,
  mp.low,
  mp.close,
  mp.volume
FROM instruments i
JOIN LATERAL (
  SELECT *
  FROM market_prices
  WHERE instrument_id = i.id
  ORDER BY timestamp DESC
  LIMIT 1
) mp ON true
WHERE i.asset_type = '${asset_type}'
ORDER BY mp.timestamp DESC
```

---

## Using the Dashboard

### Filtering by Asset Type

1. Click the **Asset Type** dropdown at the top of the dashboard
2. Select from available types: `STOCK`, `INDEX`, `CRYPTO`, etc.
3. All panels will automatically update to show data for the selected type

### Adjusting Time Range

1. Click the **time picker** in the top-right corner
2. Select a preset range (Last 7 days, Last 30 days, etc.) or define a custom range
3. All time-series panels will update accordingly

### Zooming and Panning

- **Zoom**: Click and drag horizontally on any time-series chart
- **Reset Zoom**: Double-click on the chart
- **Pan**: Hold Shift and drag

---

## Customizing the Dashboard

### Editing Panels

1. Click the panel title → **Edit**
2. Modify the query, visualization settings, or display options
3. Click **Apply** to save changes

### Adding New Panels

1. Click **Add panel** in the dashboard toolbar
2. Select **Add a new panel**
3. Configure the data source (PostgreSQL) and query
4. Choose visualization type and configure display options
5. Click **Apply** to add to dashboard

### Creating New Dashboards

1. Navigate to **Dashboards** → **New Dashboard**
2. Add panels as needed
3. Save with a descriptive name
4. Optionally, export as JSON and save to `docker/grafana/dashboards/` for version control

---

## Common Queries

### Daily Returns

Calculate daily percentage returns:

```sql
SELECT
  timestamp AS time,
  symbol,
  (close - LAG(close) OVER (PARTITION BY instrument_id ORDER BY timestamp))
    / LAG(close) OVER (PARTITION BY instrument_id ORDER BY timestamp) * 100 AS daily_return
FROM market_prices mp
JOIN instruments i ON mp.instrument_id = i.id
WHERE i.asset_type = '${asset_type}'
  AND timestamp >= $__timeFrom()
  AND timestamp <= $__timeTo()
ORDER BY timestamp ASC
```

### Average Volume by Instrument

```sql
SELECT
  i.symbol,
  AVG(mp.volume) AS avg_volume
FROM market_prices mp
JOIN instruments i ON mp.instrument_id = i.id
WHERE i.asset_type = '${asset_type}'
  AND mp.timestamp >= $__timeFrom()
  AND mp.timestamp <= $__timeTo()
GROUP BY i.symbol
ORDER BY avg_volume DESC
```

### Price Range (High-Low Spread)

```sql
SELECT
  mp.timestamp AS time,
  i.symbol AS metric,
  (mp.high - mp.low) AS value
FROM market_prices mp
JOIN instruments i ON mp.instrument_id = i.id
WHERE i.asset_type = '${asset_type}'
  AND mp.timestamp >= $__timeFrom()
  AND mp.timestamp <= $__timeTo()
ORDER BY mp.timestamp ASC
```

---

## Troubleshooting

### Dashboard Shows "No Data"

**Possible Causes:**

1. No data in database for selected asset type
2. Time range doesn't match available data
3. PostgreSQL datasource not connected

**Solutions:**

1. Check if instruments exist: `docker-compose exec postgres psql -U market_data -d market_data -c "SELECT * FROM instruments;"`
2. Verify data exists: `docker-compose exec postgres psql -U market_data -d market_data -c "SELECT COUNT(*) FROM market_prices;"`
3. Run ETL ingestion: See Phase 4 documentation
4. Check datasource connection: **Settings** → **Data Sources** → **PostgreSQL** → **Save & Test**

### Datasource Connection Failed

**Error**: "Database connection failed"

**Solutions:**

1. Verify PostgreSQL is running: `docker-compose ps postgres`
2. Check credentials in `docker/grafana/provisioning/datasources/postgres.yml`
3. Ensure services are on the same Docker network
4. Restart Grafana: `docker-compose restart grafana`

### Dashboard Not Loading

**Solutions:**

1. Check Grafana logs: `docker-compose logs grafana`
2. Verify dashboard JSON is valid
3. Re-provision: `docker-compose restart grafana`

---

## Performance Optimization

### For Large Datasets

1. **Use Time-Based Aggregation**:

   ```sql
   SELECT
     DATE_TRUNC('hour', timestamp) AS time,
     AVG(close) AS value
   FROM market_prices
   GROUP BY time
   ORDER BY time
   ```

2. **Limit Data Points**: Add `LIMIT` clause to queries

3. **Use Indexes**: Ensure composite index exists on `(instrument_id, timestamp)`

4. **Consider TimescaleDB**: For production, migrate to TimescaleDB for better time-series performance

---

## Exporting Dashboards

### Export as JSON

1. Open the dashboard
2. Click **Dashboard settings** (gear icon)
3. Select **JSON Model**
4. Copy JSON and save to `docker/grafana/dashboards/`
5. Commit to Git for version control

### Export as PDF/PNG

1. Open the dashboard
2. Click **Share** → **Export**
3. Select format (PDF, PNG)
4. Configure options and download

---

## Security Considerations

### Production Deployment

1. **Change Default Credentials**:
   - Update `GRAFANA_ADMIN_PASSWORD` in `.env`
   - Use strong passwords

2. **Enable HTTPS**:
   - Configure reverse proxy (nginx, Traefik)
   - Use SSL certificates

3. **Restrict Database Access**:
   - Create read-only PostgreSQL user for Grafana
   - Grant only SELECT permissions

4. **Enable Authentication**:
   - Configure OAuth, LDAP, or SAML
   - Disable anonymous access

---

## Additional Resources

- **Grafana Documentation**: https://grafana.com/docs/
- **PostgreSQL Data Source**: https://grafana.com/docs/grafana/latest/datasources/postgres/
- **Dashboard Best Practices**: https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/best-practices/

---

**Version**: 1.0
**Last Updated**: 2026-02-13
**Related**: [architecture.md](./architecture.md), [roadmap.md](./roadmap.md)
