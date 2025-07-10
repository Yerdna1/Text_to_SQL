# SQL Query Explanations - Table and Column Selection Rationale

This document explains why specific tables and columns were chosen for each query in the chatbot_queries.md file.

## Pipeline Overview Queries

### 1. What is the total value of deals currently in the pipeline?

**Tables Used**: `PROD_MQT_CONSULTING_PIPELINE`

**Rationale**:
- This table contains all opportunity/deal information with their current status
- `OPPORTUNITY_VALUE`: Total value of each deal as entered in CRM
- `QUALIFY_PLUS_AMT`: Filtered value for deals in advanced stages (more reliable)
- `PPV_AMT`: AI-predicted value based on historical conversion rates (most accurate forecast)
- `SALES_STAGE NOT IN ('Won', 'Lost')`: Excludes closed deals to show only active pipeline

**Why not other tables**: 
- REVENUE tables contain historical/actual data, not future pipeline
- BUDGET tables contain targets, not actual opportunities

### 2. Show me pipeline by region / industry / lead source / deal size

**Tables Used**: `PROD_MQT_CONSULTING_PIPELINE`

**Rationale**:
- Contains all dimensional breakdowns needed:
  - `GEOGRAPHY`, `MARKET`, `SECTOR`: Territory dimensions
  - `INDUSTRY`: Customer industry classification
  - `DEAL_SIZE`: Categorized as small/medium/large
- Single table has all needed dimensions, avoiding complex joins

**Why not other tables**: 
- Other tables lack the deal-level detail and dimensional richness

### 3. How many deals are in each sales stage?

**Tables Used**: `PROD_MQT_CONSULTING_PIPELINE`

**Rationale**:
- `SALES_STAGE`: Contains the current stage of each opportunity
- Includes all stages from Engage to Won/Lost
- Can calculate both count and value distributions

**Why not other tables**: 
- Only PIPELINE tables track sales stage progression

### 4. What's the average deal size this quarter?

**Tables Used**: `PROD_MQT_CONSULTING_PIPELINE`

**Rationale**:
- `OPPORTUNITY_VALUE`: Actual deal values for averaging
- `RELATIVE_QUARTER_MNEUMONIC = 'CQ'`: Filters for current quarter only
- Can segment by deal status (open vs won)

**Why not other tables**: 
- REVENUE tables would only show closed/won deals, missing pipeline

### 5. What is the win rate across the team?

**Tables Used**: `PROD_MQT_CONSULTING_PIPELINE`

**Rationale**:
- Contains both Won and Lost deals needed for win rate calculation
- `SALES_STAGE IN ('Won', 'Lost')`: Closed deals only
- Can calculate by count or by value

**Why not other tables**: 
- Need visibility to both won AND lost deals, which only PIPELINE provides

### 6. What's the forecasted revenue this month/quarter/year?

**Tables Used**: `PROD_MQT_CONSULTING_PIPELINE`

**Rationale**:
- `PPV_AMT`: PERFORM Pipeline Value - IBM's official forecast methodology
- `CALL_AMT`: FLM-committed deals (high confidence)
- `UPSIDE_AMT`: Additional opportunities (medium confidence)
- `QUALIFY_PLUS_AMT`: All qualified pipeline

**Why not REVENUE_FORECAST table**:
- `PROD_MQT_CONSULTING_REVENUE_FORECAST` exists but based on data inspection, it appears to contain different forecasting methodology
- PIPELINE table's PPV is the standardized forecasting metric used across IBM
- PPV is updated weekly with latest AI predictions
- PIPELINE provides more granular deal-level forecasts vs aggregate forecasts

**Column Selection**:
- PPV provides the most accurate forecast based on historical conversion
- CALL shows committed pipeline
- UPSIDE shows stretch opportunities

### 7. Compare the forecasted revenue to the target (budget) this month/quarter/year?

**Tables Used**: `PROD_MQT_CONSULTING_PIPELINE` + `PROD_MQT_CONSULTING_BUDGET`

**Rationale**:
- PIPELINE provides forecast (PPV_AMT)
- BUDGET provides targets (REVENUE_BUDGET_AMT)
- Join on geography/market/time dimensions for comparison

**Why this combination**:
- Need both forecast and target for variance analysis
- BUDGET table is the official source for quotas/targets

### 8. What actions can I take to improve pipeline generation/conversion?

**Tables Used**: `PROD_MQT_CONSULTING_PIPELINE`

**Rationale**:
- Analyzes pipeline composition to identify issues:
  - Stage distribution (early vs late stage balance)
  - Client concentration (CLIENT_NAME diversity)
  - Deal size mix (DEAL_SIZE distribution)
  - Conversion metrics (stage progression)

**Why not other tables**: 
- Need current pipeline composition for actionable insights

### 9. Are we on track to hit revenue targets?

**Tables Used**: `PROD_MQT_CONSULTING_PIPELINE` + `PROD_MQT_CONSULTING_BUDGET`

**Rationale**:
- `WON_AMT`: What's already closed
- `PPV_AMT`: Forecast for remainder
- `REVENUE_BUDGET_AMT`: Target to achieve
- Combination shows full picture: achieved + forecasted vs target

**Why not REVENUE_ACTUALS**:
- ACTUALS would miss the forward-looking pipeline component
- Need both historical and future view

### 10. What's the current forecast vs actual sales?

**Tables Used**: `PROD_MQT_CONSULTING_REVENUE_ACTUALS` + `PROD_MQT_CONSULTING_PIPELINE`

**Rationale**:
- ACTUALS: Historical revenue already recognized
- PIPELINE: Future forecast
- Combination provides complete revenue picture

**Why both tables**:
- ACTUALS for historical performance
- PIPELINE for forward-looking forecast
- Together show full quarter/year trajectory

## Deal Progress & Status Queries

### 1. Which deals are stuck or overdue in the pipeline? (Aged Pipeline)

**Tables Used**: `PROD_MQT_CONSULTING_PIPELINE`

**Rationale**:
- Uses WEEK field to calculate time in pipeline
- `SALES_STAGE NOT IN ('Won', 'Lost')`: Only active deals
- No direct "created date" but WEEK progression indicates age

**Column choices**:
- WEEK/QUARTER/YEAR: Used to estimate deal age
- OPPORTUNITY_VALUE: To prioritize high-value aged deals

### 2. Which opportunities have gone the longest without activity?

**Tables Used**: `PROD_MQT_CONSULTING_PIPELINE`

**Rationale**:
- Compares week-over-week to detect movement
- If SALES_STAGE unchanged between weeks = no activity
- Proxy for activity since actual activity logs not available

**Limitation noted**: 
- Would ideally use CRM activity data if available

### 3. Which deals are expected to close this week/month?

**Tables Used**: `PROD_MQT_CONSULTING_PIPELINE`

**Rationale**:
- `SALES_STAGE IN ('Closing', 'Negotiate')`: Late-stage deals
- `CALL_AMT > 0`: FLM commitment indicates close probability
- `PPV_AMT`: Predictive value for timing

**Why these columns**:
- Stage + commitment level = close probability
- PPV incorporates historical close rates

### 4. Which deals are at risk of being lost?

**Tables Used**: `PROD_MQT_CONSULTING_PIPELINE` (self-join)

**Rationale**:
- Compares current week to prior week
- Identifies negative trends:
  - PPV dropping significantly
  - Deal value decreasing
  - No stage progression

**Risk indicators**:
- PPV decline = algorithm detecting issues
- Value reduction = scope reduction/competitive pressure

## Velocity & Efficiency Queries

### 1. What is the average sales cycle length by stage?

**Tables Used**: `PROD_MQT_CONSULTING_PIPELINE`

**Rationale**:
- WEEK field used to measure time in stage
- Aggregates by SALES_STAGE
- Geographic differences captured

**Limitation**: 
- Assumes continuous weekly snapshots
- True cycle time would need deal creation date

### 2. What is the historical pipeline to revenue conversion do I need to make budget?

**Tables Used**: `PROD_MQT_CONSULTING_PIPELINE` + `PROD_MQT_CONSULTING_BUDGET`

**Rationale**:
- Historical: Prior year pipeline with WON outcomes
- Calculates actual conversion rates
- Applies to current pipeline to determine coverage needed

**Key calculations**:
- Historical conversion = WON_AMT / QUALIFY_PLUS_AMT
- Required pipeline = BUDGET / historical conversion rate

### 3. How long do deals typically stay in each stage?

**Tables Used**: `PROD_MQT_CONSULTING_PIPELINE`

**Rationale**:
- MIN/MAX WEEK per stage shows duration
- DEAL_SIZE segmentation shows velocity differences
- Identifies bottlenecks by stage

**Why WEEK tracking**:
- Weekly snapshots allow stage duration calculation

### 4. Where do most deals drop off in the funnel?

**Tables Used**: `PROD_MQT_CONSULTING_PIPELINE`

**Rationale**:
- Counts deals by stage
- Uses LAG function to compare sequential stages
- Identifies largest drop-off points

**Key metrics**:
- Stage-to-stage conversion rates
- Volume and value drop-offs

## Conversion & Funnel Analysis Queries

### 1. Which enterprise deals are closing in the next 30 days?

**Tables Used**: `PROD_MQT_CONSULTING_PIPELINE`

**Rationale**:
- `DEAL_SIZE = 'large'` or `OPPORTUNITY_VALUE > 5000000`: Enterprise definition
- `CLIENT_TYPE IN ('TARGET ENTERPRISE', 'ENTERPRISE')`: Client segmentation
- `SALES_STAGE IN ('Closing', 'Negotiate')`: Near-term close

**Why these filters**:
- Multiple ways to identify enterprise deals
- Late stage = 30-day horizon

### 2. Which deals were created from specific sources?

**Tables Used**: `PROD_MQT_CONSULTING_PIPELINE`

**Rationale**:
- PRACTICE and UT17_NAME used as source proxies
- No explicit lead source field available
- Aggregates by service line/practice

**Limitation**: 
- True lead source would require additional CRM fields

## Predictive & Prescriptive Insights Queries

### 1. Which deals are most likely to close this quarter?

**Tables Used**: `PROD_MQT_CONSULTING_PIPELINE`

**Rationale**:
- Custom scoring algorithm based on:
  - SALES_STAGE (later = higher score)
  - CALL_AMT > 0 (commitment indicator)
  - PPV_AMT ratio (algorithm confidence)
  - DEAL_SIZE (smaller = faster close)

**Scoring logic**:
- Combines multiple predictive factors
- 0-100 score for easy interpretation

### 2. Which reps/teams/brand might miss their quota based on current pipeline?

**Tables Used**: `PROD_MQT_CONSULTING_PIPELINE` + `PROD_MQT_CONSULTING_BUDGET`

**Rationale**:
- Groups by territory (GEOGRAPHY/MARKET/SECTOR)
- `WON_AMT + PPV_AMT`: Total expected achievement
- Compares to BUDGET for gap analysis

**Why not rep-level**:
- Individual rep data not available in tables
- Territory level is available proxy

### 3. What actions should I take to improve my close rate?

**Tables Used**: `PROD_MQT_CONSULTING_PIPELINE`

**Rationale**:
- Analyzes multiple performance indicators:
  - Win rate (WON vs LOST ratio)
  - Pipeline composition (stage distribution)
  - Deal characteristics (size, diversity)
- Generates specific recommendations based on metrics

**Logic flow**:
- Identify weaknesses → Recommend actions
- Data-driven prescriptive analytics

## Activity & Follow-up Queries

### 1. Which deals need follow-up this week?

**Tables Used**: `PROD_MQT_CONSULTING_PIPELINE`

**Rationale**:
- Prioritizes based on:
  - SALES_STAGE + missing CALL_AMT (negotiate without commitment)
  - Large deals in early stages
  - Low PPV scores
- Provides specific follow-up actions

**Why these criteria**:
- Risk-based prioritization
- Actionable recommendations

### 2. Which prospects haven't been contacted in 10+ days?

**Tables Used**: `PROD_MQT_CONSULTING_PIPELINE`

**Rationale**:
- Focuses on early stage deals (Qualify, Design, Engage)
- UPSIDE_AMT > 0 indicates potential but no commitment

**Limitation**: 
- No actual contact history available
- Uses stage/commitment as proxy

### 3. How many people have we touched in x organization in the last 90 days?

**Tables Used**: `PROD_MQT_CONSULTING_PIPELINE`

**Rationale**:
- Groups by CLIENT_NAME
- Counts distinct products (UT30_NAME) as touchpoints
- Shows opportunity spread across organization

**Why this approach**:
- Multiple opportunities = multiple touchpoints
- Product diversity indicates engagement breadth

## Real-Time Alerts Queries

### 1. High-value deals entering specific stages

**Tables Used**: `PROD_MQT_CONSULTING_PIPELINE`

**Rationale**:
- `OPPORTUNITY_VALUE > 5000000`: High-value threshold
- `SALES_STAGE IN ('Negotiate', 'Closing')`: Critical stages
- Real-time monitoring of significant deals

**Alert logic**:
- Size + stage = executive attention needed

### 2. Inactive deal alerts

**Tables Used**: `PROD_MQT_CONSULTING_PIPELINE` (self-join)

**Rationale**:
- Compares current to 4 weeks prior
- No change in stage/value = stalled
- Focus on deals >$100K

**Detection method**:
- Week-over-week comparison
- Multiple weeks of no change = alert

### 3. Lost deal notifications

**Tables Used**: `PROD_MQT_CONSULTING_PIPELINE`

**Rationale**:
- `SALES_STAGE = 'Lost'`: Explicitly lost deals
- `OPPORTUNITY_VALUE > 500000`: Significant losses
- Captures for lessons learned

**Purpose**:
- Loss analysis
- Process improvement

## General Design Principles

1. **Table Selection**:
   - PIPELINE tables for current/future state
   - BUDGET tables for targets/quotas
   - ACTUALS tables for historical performance
   - FORECAST tables when specific forecast methodology needed

2. **Column Selection**:
   - PPV_AMT for AI-based predictions
   - CALL_AMT for committed pipeline
   - QUALIFY_PLUS_AMT for qualified opportunities
   - WON_AMT for closed business

3. **Time Filtering**:
   - RELATIVE_QUARTER_MNEUMONIC for current/next quarter
   - SNAPSHOT_LEVEL = 'W' for weekly snapshots
   - MAX(WEEK) for latest data

4. **Performance Considerations**:
   - Appropriate indexes assumed
   - Aggregations at proper level
   - FETCH FIRST for large result sets