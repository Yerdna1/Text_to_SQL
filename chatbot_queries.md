# Sales Pipeline Chatbot - SQL Queries

This document contains SQL queries for the AI chatbot to answer specific business questions about the sales pipeline.

## Pipeline Overview

### 1. What is the total value of deals currently in the pipeline?

```sql
-- Total pipeline value across all stages (excluding Won/Lost)
SELECT 
    SUM(OPPORTUNITY_VALUE) AS TOTAL_PIPELINE_VALUE,
    SUM(QUALIFY_PLUS_AMT) AS QUALIFIED_PIPELINE_VALUE,
    SUM(PPV_AMT) AS PREDICTED_PIPELINE_VALUE,
    COUNT(DISTINCT CLIENT_NAME) AS UNIQUE_CLIENTS
FROM 
    PROD_MQT_CONSULTING_PIPELINE
WHERE 
    RELATIVE_QUARTER_MNEUMONIC = 'CQ'
    AND SNAPSHOT_LEVEL = 'W'
    AND WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
    AND SALES_STAGE NOT IN ('Won', 'Lost');
```

### 2. Show me pipeline by region / industry / lead source / deal size

```sql
-- Pipeline by Geography
SELECT 
    GEOGRAPHY,
    MARKET,
    SECTOR,
    SUM(OPPORTUNITY_VALUE) AS TOTAL_PIPELINE,
    SUM(QUALIFY_PLUS_AMT) AS QUALIFIED_PIPELINE,
    COUNT(*) AS DEAL_COUNT,
    AVG(OPPORTUNITY_VALUE) AS AVG_DEAL_SIZE
FROM 
    PROD_MQT_CONSULTING_PIPELINE
WHERE 
    RELATIVE_QUARTER_MNEUMONIC = 'CQ'
    AND SNAPSHOT_LEVEL = 'W'
    AND WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
    AND SALES_STAGE NOT IN ('Won', 'Lost')
GROUP BY 
    GEOGRAPHY, MARKET, SECTOR
ORDER BY 
    TOTAL_PIPELINE DESC;

-- Pipeline by Industry
SELECT 
    INDUSTRY,
    SUM(OPPORTUNITY_VALUE) AS TOTAL_PIPELINE,
    SUM(QUALIFY_PLUS_AMT) AS QUALIFIED_PIPELINE,
    COUNT(DISTINCT CLIENT_NAME) AS CLIENT_COUNT,
    COUNT(*) AS DEAL_COUNT
FROM 
    PROD_MQT_CONSULTING_PIPELINE
WHERE 
    RELATIVE_QUARTER_MNEUMONIC = 'CQ'
    AND SNAPSHOT_LEVEL = 'W'
    AND WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
    AND SALES_STAGE NOT IN ('Won', 'Lost')
GROUP BY 
    INDUSTRY
ORDER BY 
    TOTAL_PIPELINE DESC;

-- Pipeline by Deal Size
SELECT 
    DEAL_SIZE,
    COUNT(*) AS DEAL_COUNT,
    SUM(OPPORTUNITY_VALUE) AS TOTAL_PIPELINE,
    AVG(OPPORTUNITY_VALUE) AS AVG_DEAL_VALUE,
    MIN(OPPORTUNITY_VALUE) AS MIN_DEAL_VALUE,
    MAX(OPPORTUNITY_VALUE) AS MAX_DEAL_VALUE
FROM 
    PROD_MQT_CONSULTING_PIPELINE
WHERE 
    RELATIVE_QUARTER_MNEUMONIC = 'CQ'
    AND SNAPSHOT_LEVEL = 'W'
    AND WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
    AND SALES_STAGE NOT IN ('Won', 'Lost')
GROUP BY 
    DEAL_SIZE
ORDER BY 
    AVG_DEAL_VALUE DESC;
```

### 3. How many deals are in each sales stage?

```sql
-- Deal count and value by sales stage
SELECT 
    SALES_STAGE,
    COUNT(*) AS DEAL_COUNT,
    SUM(OPPORTUNITY_VALUE) AS STAGE_PIPELINE_VALUE,
    AVG(OPPORTUNITY_VALUE) AS AVG_DEAL_SIZE,
    DECIMAL(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 5, 2) AS PCT_OF_DEALS,
    DECIMAL(SUM(OPPORTUNITY_VALUE) * 100.0 / SUM(SUM(OPPORTUNITY_VALUE)) OVER(), 5, 2) AS PCT_OF_VALUE
FROM 
    PROD_MQT_CONSULTING_PIPELINE
WHERE 
    RELATIVE_QUARTER_MNEUMONIC = 'CQ'
    AND SNAPSHOT_LEVEL = 'W'
    AND WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
GROUP BY 
    SALES_STAGE
ORDER BY 
    CASE SALES_STAGE
        WHEN 'Won' THEN 1
        WHEN 'Closing' THEN 2
        WHEN 'Negotiate' THEN 3
        WHEN 'Propose' THEN 4
        WHEN 'Qualify' THEN 5
        WHEN 'Design' THEN 6
        WHEN 'Engage' THEN 7
        WHEN 'Lost' THEN 8
        ELSE 9
    END;
```

### 4. What's the average deal size this quarter?

```sql
-- Average deal size metrics for current quarter
SELECT 
    AVG(OPPORTUNITY_VALUE) AS AVG_DEAL_SIZE_ALL,
    AVG(CASE WHEN SALES_STAGE NOT IN ('Won', 'Lost') THEN OPPORTUNITY_VALUE END) AS AVG_DEAL_SIZE_OPEN,
    AVG(CASE WHEN SALES_STAGE = 'Won' THEN OPPORTUNITY_VALUE END) AS AVG_DEAL_SIZE_WON,
    MEDIAN(OPPORTUNITY_VALUE) AS MEDIAN_DEAL_SIZE,
    COUNT(*) AS TOTAL_DEALS,
    COUNT(CASE WHEN SALES_STAGE = 'Won' THEN 1 END) AS WON_DEALS
FROM 
    PROD_MQT_CONSULTING_PIPELINE
WHERE 
    RELATIVE_QUARTER_MNEUMONIC = 'CQ'
    AND SNAPSHOT_LEVEL = 'W'
    AND WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ');
```

### 5. What is the win rate across the team?

```sql
-- Win rate calculation
WITH deal_outcomes AS (
    SELECT 
        COUNT(CASE WHEN SALES_STAGE = 'Won' THEN 1 END) AS WON_DEALS,
        COUNT(CASE WHEN SALES_STAGE = 'Lost' THEN 1 END) AS LOST_DEALS,
        COUNT(CASE WHEN SALES_STAGE IN ('Won', 'Lost') THEN 1 END) AS CLOSED_DEALS,
        SUM(CASE WHEN SALES_STAGE = 'Won' THEN OPPORTUNITY_VALUE END) AS WON_VALUE,
        SUM(CASE WHEN SALES_STAGE = 'Lost' THEN OPPORTUNITY_VALUE END) AS LOST_VALUE
    FROM 
        PROD_MQT_CONSULTING_PIPELINE
    WHERE 
        RELATIVE_QUARTER_MNEUMONIC = 'CQ'
        AND SNAPSHOT_LEVEL = 'W'
        AND WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
)
SELECT 
    WON_DEALS,
    LOST_DEALS,
    CLOSED_DEALS,
    CASE 
        WHEN CLOSED_DEALS > 0 
        THEN DECIMAL(WON_DEALS * 100.0 / CLOSED_DEALS, 5, 2) 
        ELSE 0 
    END AS WIN_RATE_BY_COUNT,
    CASE 
        WHEN (WON_VALUE + LOST_VALUE) > 0 
        THEN DECIMAL(WON_VALUE * 100.0 / (WON_VALUE + LOST_VALUE), 5, 2) 
        ELSE 0 
    END AS WIN_RATE_BY_VALUE,
    WON_VALUE,
    LOST_VALUE
FROM 
    deal_outcomes;
```

### 6. What's the forecasted revenue this month/quarter/year?

```sql
-- Forecasted revenue by time period
SELECT 
    'Current Quarter' AS PERIOD,
    SUM(PPV_AMT) AS FORECASTED_REVENUE,
    SUM(CALL_AMT) AS COMMITTED_REVENUE,
    SUM(UPSIDE_AMT) AS UPSIDE_REVENUE,
    SUM(QUALIFY_PLUS_AMT) AS QUALIFIED_PIPELINE
FROM 
    PROD_MQT_CONSULTING_PIPELINE
WHERE 
    RELATIVE_QUARTER_MNEUMONIC = 'CQ'
    AND SNAPSHOT_LEVEL = 'W'
    AND WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
    AND SALES_STAGE NOT IN ('Won', 'Lost')

UNION ALL

-- Current Month
SELECT 
    'Current Month' AS PERIOD,
    SUM(PPV_AMT) AS FORECASTED_REVENUE,
    SUM(CALL_AMT) AS COMMITTED_REVENUE,
    SUM(UPSIDE_AMT) AS UPSIDE_REVENUE,
    SUM(QUALIFY_PLUS_AMT) AS QUALIFIED_PIPELINE
FROM 
    PROD_MQT_CONSULTING_PIPELINE
WHERE 
    RELATIVE_QUARTER_MNEUMONIC = 'CQ'
    AND SNAPSHOT_LEVEL = 'W'
    AND WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
    AND MONTH = MONTH(CURRENT DATE)
    AND SALES_STAGE NOT IN ('Won', 'Lost')

UNION ALL

-- Full Year
SELECT 
    'Full Year' AS PERIOD,
    SUM(PPV_AMT) AS FORECASTED_REVENUE,
    SUM(CALL_AMT) AS COMMITTED_REVENUE,
    SUM(UPSIDE_AMT) AS UPSIDE_REVENUE,
    SUM(QUALIFY_PLUS_AMT) AS QUALIFIED_PIPELINE
FROM 
    PROD_MQT_CONSULTING_PIPELINE
WHERE 
    YEAR = YEAR(CURRENT DATE)
    AND SNAPSHOT_LEVEL = 'W'
    AND WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE YEAR = YEAR(CURRENT DATE))
    AND SALES_STAGE NOT IN ('Won', 'Lost');
```

### 7. Compare the forecasted revenue to the target (budget) this month/quarter/year?

```sql
-- Forecast vs Budget comparison
WITH forecast_data AS (
    SELECT 
        p.YEAR,
        p.QUARTER,
        p.GEOGRAPHY,
        p.MARKET,
        SUM(p.PPV_AMT) AS FORECASTED_REVENUE,
        SUM(p.CALL_AMT) AS COMMITTED_REVENUE,
        SUM(p.WON_AMT) AS WON_REVENUE
    FROM 
        PROD_MQT_CONSULTING_PIPELINE p
    WHERE 
        p.RELATIVE_QUARTER_MNEUMONIC = 'CQ'
        AND p.SNAPSHOT_LEVEL = 'W'
        AND p.WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
    GROUP BY 
        p.YEAR, p.QUARTER, p.GEOGRAPHY, p.MARKET
),
budget_data AS (
    SELECT 
        YEAR,
        QUARTER,
        GEOGRAPHY,
        MARKET,
        SUM(REVENUE_BUDGET_AMT) AS BUDGET_REVENUE
    FROM 
        PROD_MQT_CONSULTING_BUDGET
    WHERE 
        YEAR = YEAR(CURRENT DATE)
        AND QUARTER = QUARTER(CURRENT DATE)
    GROUP BY 
        YEAR, QUARTER, GEOGRAPHY, MARKET
)
SELECT 
    f.GEOGRAPHY,
    f.MARKET,
    f.FORECASTED_REVENUE,
    b.BUDGET_REVENUE,
    f.FORECASTED_REVENUE - b.BUDGET_REVENUE AS VARIANCE,
    CASE 
        WHEN b.BUDGET_REVENUE > 0 
        THEN DECIMAL(f.FORECASTED_REVENUE / b.BUDGET_REVENUE * 100, 5, 2) 
        ELSE 0 
    END AS FORECAST_TO_BUDGET_PCT,
    f.COMMITTED_REVENUE,
    CASE 
        WHEN b.BUDGET_REVENUE > 0 
        THEN DECIMAL(f.COMMITTED_REVENUE / b.BUDGET_REVENUE * 100, 5, 2) 
        ELSE 0 
    END AS COMMITTED_TO_BUDGET_PCT,
    f.WON_REVENUE
FROM 
    forecast_data f
LEFT JOIN 
    budget_data b
    ON f.YEAR = b.YEAR 
    AND f.QUARTER = b.QUARTER
    AND f.GEOGRAPHY = b.GEOGRAPHY
    AND f.MARKET = b.MARKET
ORDER BY 
    VARIANCE DESC;
```

### 8. What actions can I take to improve pipeline generation/conversion?

```sql
-- Pipeline improvement insights
WITH pipeline_analysis AS (
    SELECT 
        GEOGRAPHY,
        MARKET,
        -- Pipeline metrics
        SUM(QUALIFY_PLUS_AMT) AS QUALIFIED_PIPELINE,
        SUM(CASE WHEN SALES_STAGE = 'Closing' THEN OPPORTUNITY_VALUE ELSE 0 END) AS CLOSING_PIPELINE,
        SUM(CASE WHEN SALES_STAGE IN ('Qualify', 'Design', 'Engage') THEN OPPORTUNITY_VALUE ELSE 0 END) AS EARLY_STAGE_PIPELINE,
        -- Deal metrics
        COUNT(DISTINCT CLIENT_NAME) AS UNIQUE_CLIENTS,
        AVG(OPPORTUNITY_VALUE) AS AVG_DEAL_SIZE,
        COUNT(CASE WHEN DEAL_SIZE = 'large' THEN 1 END) AS LARGE_DEALS,
        -- Conversion metrics
        DECIMAL(
            SUM(CASE WHEN SALES_STAGE = 'Closing' THEN OPPORTUNITY_VALUE ELSE 0 END) / 
            NULLIF(SUM(QUALIFY_PLUS_AMT), 0) * 100
        , 5, 2) AS CLOSING_RATE
    FROM 
        PROD_MQT_CONSULTING_PIPELINE
    WHERE 
        RELATIVE_QUARTER_MNEUMONIC = 'CQ'
        AND SNAPSHOT_LEVEL = 'W'
        AND WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
        AND SALES_STAGE NOT IN ('Won', 'Lost')
    GROUP BY 
        GEOGRAPHY, MARKET
)
SELECT 
    GEOGRAPHY,
    MARKET,
    QUALIFIED_PIPELINE,
    CLOSING_RATE,
    CASE 
        WHEN CLOSING_RATE < 20 THEN 'Action: Focus on advancing deals through stages'
        WHEN EARLY_STAGE_PIPELINE > CLOSING_PIPELINE * 2 THEN 'Action: Accelerate qualification process'
        WHEN UNIQUE_CLIENTS < 10 THEN 'Action: Expand client outreach'
        WHEN AVG_DEAL_SIZE < 100000 THEN 'Action: Target larger opportunities'
        WHEN LARGE_DEALS = 0 THEN 'Action: Pursue enterprise deals'
        ELSE 'Pipeline health is good'
    END AS RECOMMENDED_ACTION,
    CASE 
        WHEN CLOSING_RATE < 20 THEN 'Low conversion from pipeline to closing'
        WHEN EARLY_STAGE_PIPELINE > CLOSING_PIPELINE * 2 THEN 'Too many deals stuck in early stages'
        WHEN UNIQUE_CLIENTS < 10 THEN 'Limited client diversification'
        WHEN AVG_DEAL_SIZE < 100000 THEN 'Deal sizes below optimal threshold'
        WHEN LARGE_DEALS = 0 THEN 'Missing large enterprise opportunities'
        ELSE 'No critical issues identified'
    END AS ISSUE_IDENTIFIED
FROM 
    pipeline_analysis
ORDER BY 
    CLOSING_RATE ASC;
```

### 9. Are we on track to hit revenue targets?

```sql
-- Revenue target tracking
WITH current_performance AS (
    SELECT 
        p.GEOGRAPHY,
        p.MARKET,
        SUM(p.WON_AMT) AS WON_TO_DATE,
        SUM(p.PPV_AMT) AS FORECAST_REMAINDER,
        SUM(p.WON_AMT) + SUM(p.PPV_AMT) AS PROJECTED_TOTAL
    FROM 
        PROD_MQT_CONSULTING_PIPELINE p
    WHERE 
        p.RELATIVE_QUARTER_MNEUMONIC = 'CQ'
        AND p.SNAPSHOT_LEVEL = 'W'
        AND p.WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
    GROUP BY 
        p.GEOGRAPHY, p.MARKET
),
targets AS (
    SELECT 
        GEOGRAPHY,
        MARKET,
        SUM(REVENUE_BUDGET_AMT) AS QUARTER_TARGET
    FROM 
        PROD_MQT_CONSULTING_BUDGET
    WHERE 
        YEAR = YEAR(CURRENT DATE)
        AND QUARTER = QUARTER(CURRENT DATE)
    GROUP BY 
        GEOGRAPHY, MARKET
)
SELECT 
    cp.GEOGRAPHY,
    cp.MARKET,
    cp.WON_TO_DATE,
    cp.FORECAST_REMAINDER,
    cp.PROJECTED_TOTAL,
    t.QUARTER_TARGET,
    cp.PROJECTED_TOTAL - t.QUARTER_TARGET AS GAP_TO_TARGET,
    CASE 
        WHEN t.QUARTER_TARGET > 0 
        THEN DECIMAL(cp.PROJECTED_TOTAL / t.QUARTER_TARGET * 100, 5, 2) 
        ELSE 0 
    END AS PROJECTED_ATTAINMENT_PCT,
    CASE 
        WHEN cp.PROJECTED_TOTAL >= t.QUARTER_TARGET THEN 'On Track'
        WHEN cp.PROJECTED_TOTAL >= t.QUARTER_TARGET * 0.9 THEN 'At Risk'
        ELSE 'Off Track'
    END AS STATUS,
    CASE 
        WHEN cp.PROJECTED_TOTAL < t.QUARTER_TARGET 
        THEN 'Need additional pipeline of: ' || CHAR(DECIMAL(t.QUARTER_TARGET - cp.PROJECTED_TOTAL, 15, 2))
        ELSE 'Target achievable with current pipeline'
    END AS ACTION_REQUIRED
FROM 
    current_performance cp
JOIN 
    targets t
    ON cp.GEOGRAPHY = t.GEOGRAPHY 
    AND cp.MARKET = t.MARKET
ORDER BY 
    PROJECTED_ATTAINMENT_PCT ASC;
```

### 10. What's the current forecast vs actual sales?

```sql
-- Forecast vs Actuals comparison
WITH actuals AS (
    SELECT 
        GEOGRAPHY,
        MARKET,
        SUM(REVENUE_AMT) AS ACTUAL_REVENUE,
        SUM(GROSS_PROFIT_AMT) AS ACTUAL_GP
    FROM 
        PROD_MQT_CONSULTING_REVENUE_ACTUALS
    WHERE 
        YEAR = YEAR(CURRENT DATE)
        AND QUARTER = QUARTER(CURRENT DATE)
        AND MONTH <= MONTH(CURRENT DATE)
    GROUP BY 
        GEOGRAPHY, MARKET
),
forecast AS (
    SELECT 
        GEOGRAPHY,
        MARKET,
        SUM(PPV_AMT) AS FORECASTED_REVENUE,
        SUM(WON_AMT) AS WON_REVENUE
    FROM 
        PROD_MQT_CONSULTING_PIPELINE
    WHERE 
        RELATIVE_QUARTER_MNEUMONIC = 'CQ'
        AND SNAPSHOT_LEVEL = 'W'
        AND WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
    GROUP BY 
        GEOGRAPHY, MARKET
)
SELECT 
    COALESCE(a.GEOGRAPHY, f.GEOGRAPHY) AS GEOGRAPHY,
    COALESCE(a.MARKET, f.MARKET) AS MARKET,
    a.ACTUAL_REVENUE,
    f.FORECASTED_REVENUE,
    f.WON_REVENUE,
    a.ACTUAL_REVENUE + f.FORECASTED_REVENUE AS TOTAL_EXPECTED,
    CASE 
        WHEN a.ACTUAL_REVENUE > 0 
        THEN DECIMAL(a.ACTUAL_GP / a.ACTUAL_REVENUE * 100, 5, 2) 
        ELSE 0 
    END AS ACTUAL_GP_MARGIN_PCT
FROM 
    actuals a
FULL OUTER JOIN 
    forecast f
    ON a.GEOGRAPHY = f.GEOGRAPHY 
    AND a.MARKET = f.MARKET
ORDER BY 
    TOTAL_EXPECTED DESC;
```

## Deal Progress & Status

### 1. Which deals are stuck or overdue in the pipeline? (Aged Pipeline)

```sql
-- Aged pipeline analysis
WITH deal_age AS (
    SELECT 
        CLIENT_NAME,
        UT30_NAME,
        OPPORTUNITY_VALUE,
        SALES_STAGE,
        GEOGRAPHY,
        MARKET,
        -- Calculate age based on historical data availability
        DATEDIFF('day', 
            DATE(YEAR || '-01-01') + ((QUARTER - 1) * 3) MONTHS + ((WEEK - 1) * 7) DAYS,
            CURRENT DATE
        ) AS DAYS_IN_PIPELINE,
        PPV_AMT
    FROM 
        PROD_MQT_CONSULTING_PIPELINE
    WHERE 
        RELATIVE_QUARTER_MNEUMONIC = 'CQ'
        AND SNAPSHOT_LEVEL = 'W'
        AND WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
        AND SALES_STAGE NOT IN ('Won', 'Lost')
)
SELECT 
    CLIENT_NAME,
    UT30_NAME AS PRODUCT,
    SALES_STAGE,
    OPPORTUNITY_VALUE,
    DAYS_IN_PIPELINE,
    CASE 
        WHEN DAYS_IN_PIPELINE > 180 THEN 'Critical - Over 6 months'
        WHEN DAYS_IN_PIPELINE > 120 THEN 'High - Over 4 months'
        WHEN DAYS_IN_PIPELINE > 90 THEN 'Medium - Over 3 months'
        WHEN DAYS_IN_PIPELINE > 60 THEN 'Low - Over 2 months'
        ELSE 'Normal'
    END AS AGE_CATEGORY,
    GEOGRAPHY,
    MARKET
FROM 
    deal_age
WHERE 
    DAYS_IN_PIPELINE > 60  -- Focus on deals over 2 months old
ORDER BY 
    DAYS_IN_PIPELINE DESC, OPPORTUNITY_VALUE DESC
FETCH FIRST 50 ROWS ONLY;
```

### 2. Which opportunities have gone the longest without activity?

```sql
-- This query would require activity/interaction data which isn't in the current tables
-- Using week-over-week changes as a proxy for activity
WITH deal_movement AS (
    SELECT 
        p1.CLIENT_NAME,
        p1.UT30_NAME,
        p1.OPPORTUNITY_VALUE,
        p1.SALES_STAGE AS CURRENT_STAGE,
        p2.SALES_STAGE AS PRIOR_WEEK_STAGE,
        CASE 
            WHEN p1.SALES_STAGE = p2.SALES_STAGE THEN 'No Movement'
            ELSE 'Stage Changed'
        END AS ACTIVITY_STATUS,
        p1.GEOGRAPHY,
        p1.MARKET
    FROM 
        PROD_MQT_CONSULTING_PIPELINE p1
    LEFT JOIN 
        PROD_MQT_CONSULTING_PIPELINE p2
        ON p1.CLIENT_NAME = p2.CLIENT_NAME
        AND p1.UT30_NAME = p2.UT30_NAME
        AND p1.YEAR = p2.YEAR
        AND p1.QUARTER = p2.QUARTER
        AND p1.WEEK = p2.WEEK + 1
    WHERE 
        p1.RELATIVE_QUARTER_MNEUMONIC = 'CQ'
        AND p1.SNAPSHOT_LEVEL = 'W'
        AND p1.WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
        AND p1.SALES_STAGE NOT IN ('Won', 'Lost')
)
SELECT 
    CLIENT_NAME,
    UT30_NAME AS PRODUCT,
    CURRENT_STAGE,
    OPPORTUNITY_VALUE,
    ACTIVITY_STATUS,
    GEOGRAPHY,
    MARKET
FROM 
    deal_movement
WHERE 
    ACTIVITY_STATUS = 'No Movement'
ORDER BY 
    OPPORTUNITY_VALUE DESC
FETCH FIRST 50 ROWS ONLY;
```

### 3. Which deals are expected to close this week/month?

```sql
-- Deals expected to close in current period
SELECT 
    CLIENT_NAME,
    UT30_NAME AS PRODUCT,
    OPPORTUNITY_VALUE,
    CALL_AMT AS COMMITTED_AMOUNT,
    PPV_AMT AS PREDICTED_VALUE,
    SALES_STAGE,
    GEOGRAPHY,
    MARKET,
    CASE 
        WHEN SALES_STAGE = 'Closing' THEN 'High Probability'
        WHEN SALES_STAGE = 'Negotiate' AND CALL_AMT > 0 THEN 'Medium Probability'
        ELSE 'Lower Probability'
    END AS CLOSE_PROBABILITY
FROM 
    PROD_MQT_CONSULTING_PIPELINE
WHERE 
    RELATIVE_QUARTER_MNEUMONIC = 'CQ'
    AND SNAPSHOT_LEVEL = 'W'
    AND WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
    AND SALES_STAGE IN ('Closing', 'Negotiate')
    AND (CALL_AMT > 0 OR SALES_STAGE = 'Closing')
ORDER BY 
    CLOSE_PROBABILITY, OPPORTUNITY_VALUE DESC;
```

### 4. Which deals are at risk of being lost?

```sql
-- At-risk deals identification
WITH deal_trends AS (
    SELECT 
        p1.CLIENT_NAME,
        p1.UT30_NAME,
        p1.OPPORTUNITY_VALUE AS CURRENT_VALUE,
        p2.OPPORTUNITY_VALUE AS PRIOR_VALUE,
        p1.SALES_STAGE AS CURRENT_STAGE,
        p2.SALES_STAGE AS PRIOR_STAGE,
        p1.PPV_AMT AS CURRENT_PPV,
        p2.PPV_AMT AS PRIOR_PPV,
        p1.GEOGRAPHY,
        p1.MARKET
    FROM 
        PROD_MQT_CONSULTING_PIPELINE p1
    LEFT JOIN 
        PROD_MQT_CONSULTING_PIPELINE p2
        ON p1.CLIENT_NAME = p2.CLIENT_NAME
        AND p1.UT30_NAME = p2.UT30_NAME
        AND p1.YEAR = p2.YEAR
        AND p1.QUARTER = p2.QUARTER
        AND p1.WEEK = p2.WEEK + 1
    WHERE 
        p1.RELATIVE_QUARTER_MNEUMONIC = 'CQ'
        AND p1.SNAPSHOT_LEVEL = 'W'
        AND p1.WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
        AND p1.SALES_STAGE NOT IN ('Won', 'Lost')
)
SELECT 
    CLIENT_NAME,
    UT30_NAME AS PRODUCT,
    CURRENT_VALUE,
    CURRENT_STAGE,
    GEOGRAPHY,
    MARKET,
    CASE 
        WHEN CURRENT_PPV < PRIOR_PPV * 0.5 THEN 'High Risk - PPV dropped >50%'
        WHEN CURRENT_VALUE < PRIOR_VALUE * 0.8 THEN 'High Risk - Value dropped >20%'
        WHEN CURRENT_STAGE = PRIOR_STAGE AND CURRENT_STAGE IN ('Qualify', 'Design') THEN 'Medium Risk - No progression'
        WHEN CURRENT_PPV < PRIOR_PPV THEN 'Low Risk - PPV declining'
        ELSE 'Normal'
    END AS RISK_LEVEL,
    CURRENT_PPV - COALESCE(PRIOR_PPV, 0) AS PPV_CHANGE
FROM 
    deal_trends
WHERE 
    CURRENT_PPV < PRIOR_PPV OR CURRENT_VALUE < PRIOR_VALUE
ORDER BY 
    RISK_LEVEL, CURRENT_VALUE DESC;
```

## Velocity & Efficiency

### 1. What is the average sales cycle length by stage?

```sql
-- Sales cycle analysis by stage
WITH stage_duration AS (
    SELECT 
        SALES_STAGE,
        GEOGRAPHY,
        AVG(WEEK) AS AVG_WEEKS_IN_STAGE,
        COUNT(*) AS DEALS_IN_STAGE,
        AVG(OPPORTUNITY_VALUE) AS AVG_DEAL_VALUE
    FROM 
        PROD_MQT_CONSULTING_PIPELINE
    WHERE 
        RELATIVE_QUARTER_MNEUMONIC = 'CQ'
        AND SNAPSHOT_LEVEL = 'W'
        AND SALES_STAGE NOT IN ('Won', 'Lost')
    GROUP BY 
        SALES_STAGE, GEOGRAPHY
)
SELECT 
    SALES_STAGE,
    GEOGRAPHY,
    AVG_WEEKS_IN_STAGE,
    DEALS_IN_STAGE,
    AVG_DEAL_VALUE,
    CASE 
        WHEN AVG_WEEKS_IN_STAGE > 8 THEN 'Above Average Duration'
        WHEN AVG_WEEKS_IN_STAGE > 4 THEN 'Average Duration'
        ELSE 'Fast Moving'
    END AS VELOCITY_ASSESSMENT
FROM 
    stage_duration
ORDER BY 
    CASE SALES_STAGE
        WHEN 'Closing' THEN 1
        WHEN 'Negotiate' THEN 2
        WHEN 'Propose' THEN 3
        WHEN 'Qualify' THEN 4
        WHEN 'Design' THEN 5
        ELSE 6
    END,
    GEOGRAPHY;
```

### 2. What is the historical pipeline to revenue conversion do I need to make budget?

```sql
-- Historical conversion analysis
WITH historical_conversion AS (
    SELECT 
        GEOGRAPHY,
        MARKET,
        -- Historical conversion rates
        AVG(CASE WHEN PPV_AMT > 0 THEN WON_AMT / PPV_AMT ELSE 0 END) AS AVG_PPV_CONVERSION,
        AVG(CASE WHEN QUALIFY_PLUS_AMT > 0 THEN WON_AMT / QUALIFY_PLUS_AMT ELSE 0 END) AS AVG_QUALIFY_CONVERSION,
        AVG(CASE WHEN CALL_AMT > 0 THEN WON_AMT / CALL_AMT ELSE 0 END) AS AVG_CALL_CONVERSION
    FROM 
        PROD_MQT_CONSULTING_PIPELINE
    WHERE 
        YEAR = YEAR(CURRENT DATE) - 1  -- Last year's data
        AND SALES_STAGE IN ('Won', 'Lost')
    GROUP BY 
        GEOGRAPHY, MARKET
),
current_pipeline AS (
    SELECT 
        p.GEOGRAPHY,
        p.MARKET,
        SUM(p.QUALIFY_PLUS_AMT) AS CURRENT_PIPELINE,
        SUM(p.PPV_AMT) AS CURRENT_PPV,
        SUM(b.REVENUE_BUDGET_AMT) AS BUDGET
    FROM 
        PROD_MQT_CONSULTING_PIPELINE p
    JOIN 
        PROD_MQT_CONSULTING_BUDGET b
        ON p.GEOGRAPHY = b.GEOGRAPHY
        AND p.MARKET = b.MARKET
        AND p.YEAR = b.YEAR
        AND p.QUARTER = b.QUARTER
    WHERE 
        p.RELATIVE_QUARTER_MNEUMONIC = 'CQ'
        AND p.SNAPSHOT_LEVEL = 'W'
        AND p.WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
    GROUP BY 
        p.GEOGRAPHY, p.MARKET
)
SELECT 
    cp.GEOGRAPHY,
    cp.MARKET,
    cp.BUDGET,
    cp.CURRENT_PIPELINE,
    hc.AVG_QUALIFY_CONVERSION * 100 AS HISTORICAL_CONVERSION_PCT,
    CASE 
        WHEN hc.AVG_QUALIFY_CONVERSION > 0 
        THEN DECIMAL(cp.BUDGET / hc.AVG_QUALIFY_CONVERSION, 15, 2)
        ELSE 0 
    END AS PIPELINE_NEEDED,
    CASE 
        WHEN hc.AVG_QUALIFY_CONVERSION > 0 
        THEN DECIMAL((cp.BUDGET / hc.AVG_QUALIFY_CONVERSION) - cp.CURRENT_PIPELINE, 15, 2)
        ELSE 0 
    END AS PIPELINE_GAP,
    CASE 
        WHEN hc.AVG_QUALIFY_CONVERSION > 0 
        THEN DECIMAL(cp.CURRENT_PIPELINE / (cp.BUDGET / hc.AVG_QUALIFY_CONVERSION), 5, 2)
        ELSE 0 
    END AS COVERAGE_MULTIPLIER
FROM 
    current_pipeline cp
LEFT JOIN 
    historical_conversion hc
    ON cp.GEOGRAPHY = hc.GEOGRAPHY
    AND cp.MARKET = hc.MARKET
ORDER BY 
    PIPELINE_GAP DESC;
```

### 3. How long do deals typically stay in each stage?

```sql
-- Stage duration analysis
WITH stage_transitions AS (
    SELECT 
        SALES_STAGE,
        DEAL_SIZE,
        COUNT(*) AS DEAL_COUNT,
        AVG(OPPORTUNITY_VALUE) AS AVG_DEAL_VALUE,
        -- Using week numbers as proxy for duration
        MIN(WEEK) AS MIN_WEEK,
        MAX(WEEK) AS MAX_WEEK,
        MAX(WEEK) - MIN(WEEK) AS WEEKS_IN_STAGE
    FROM 
        PROD_MQT_CONSULTING_PIPELINE
    WHERE 
        YEAR = YEAR(CURRENT DATE)
        AND SALES_STAGE NOT IN ('Won', 'Lost')
    GROUP BY 
        SALES_STAGE, DEAL_SIZE
)
SELECT 
    SALES_STAGE,
    DEAL_SIZE,
    DEAL_COUNT,
    AVG_DEAL_VALUE,
    WEEKS_IN_STAGE,
    CASE 
        WHEN SALES_STAGE = 'Qualify' AND WEEKS_IN_STAGE > 6 THEN 'Too Long - Accelerate qualification'
        WHEN SALES_STAGE = 'Propose' AND WEEKS_IN_STAGE > 4 THEN 'Too Long - Push for decision'
        WHEN SALES_STAGE = 'Negotiate' AND WEEKS_IN_STAGE > 3 THEN 'Too Long - Close or reassess'
        WHEN SALES_STAGE = 'Closing' AND WEEKS_IN_STAGE > 2 THEN 'Too Long - Remove blockers'
        ELSE 'Normal Duration'
    END AS DURATION_ASSESSMENT
FROM 
    stage_transitions
ORDER BY 
    CASE SALES_STAGE
        WHEN 'Closing' THEN 1
        WHEN 'Negotiate' THEN 2
        WHEN 'Propose' THEN 3
        WHEN 'Qualify' THEN 4
        WHEN 'Design' THEN 5
        ELSE 6
    END,
    DEAL_SIZE;
```

### 4. Where do most deals drop off in the funnel?

```sql
-- Funnel drop-off analysis
WITH stage_flow AS (
    SELECT 
        SALES_STAGE,
        COUNT(*) AS DEALS_IN_STAGE,
        SUM(OPPORTUNITY_VALUE) AS VALUE_IN_STAGE,
        SUM(CASE WHEN SALES_STAGE = 'Lost' THEN 1 ELSE 0 END) AS LOST_DEALS
    FROM 
        PROD_MQT_CONSULTING_PIPELINE
    WHERE 
        YEAR = YEAR(CURRENT DATE)
        AND SNAPSHOT_LEVEL = 'W'
    GROUP BY 
        SALES_STAGE
),
funnel_metrics AS (
    SELECT 
        SALES_STAGE,
        DEALS_IN_STAGE,
        VALUE_IN_STAGE,
        SUM(DEALS_IN_STAGE) OVER (ORDER BY 
            CASE SALES_STAGE
                WHEN 'Engage' THEN 1
                WHEN 'Design' THEN 2
                WHEN 'Qualify' THEN 3
                WHEN 'Propose' THEN 4
                WHEN 'Negotiate' THEN 5
                WHEN 'Closing' THEN 6
                WHEN 'Won' THEN 7
                WHEN 'Lost' THEN 8
            END
        ) AS CUMULATIVE_DEALS
    FROM 
        stage_flow
)
SELECT 
    SALES_STAGE,
    DEALS_IN_STAGE,
    VALUE_IN_STAGE,
    LAG(DEALS_IN_STAGE) OVER (ORDER BY 
        CASE SALES_STAGE
            WHEN 'Engage' THEN 1
            WHEN 'Design' THEN 2
            WHEN 'Qualify' THEN 3
            WHEN 'Propose' THEN 4
            WHEN 'Negotiate' THEN 5
            WHEN 'Closing' THEN 6
            WHEN 'Won' THEN 7
            WHEN 'Lost' THEN 8
        END
    ) AS PREV_STAGE_DEALS,
    CASE 
        WHEN LAG(DEALS_IN_STAGE) OVER (ORDER BY 
            CASE SALES_STAGE
                WHEN 'Engage' THEN 1
                WHEN 'Design' THEN 2
                WHEN 'Qualify' THEN 3
                WHEN 'Propose' THEN 4
                WHEN 'Negotiate' THEN 5
                WHEN 'Closing' THEN 6
                WHEN 'Won' THEN 7
                WHEN 'Lost' THEN 8
            END
        ) > 0 
        THEN DECIMAL((LAG(DEALS_IN_STAGE) OVER (ORDER BY 
            CASE SALES_STAGE
                WHEN 'Engage' THEN 1
                WHEN 'Design' THEN 2
                WHEN 'Qualify' THEN 3
                WHEN 'Propose' THEN 4
                WHEN 'Negotiate' THEN 5
                WHEN 'Closing' THEN 6
                WHEN 'Won' THEN 7
                WHEN 'Lost' THEN 8
            END
        ) - DEALS_IN_STAGE) * 100.0 / LAG(DEALS_IN_STAGE) OVER (ORDER BY 
            CASE SALES_STAGE
                WHEN 'Engage' THEN 1
                WHEN 'Design' THEN 2
                WHEN 'Qualify' THEN 3
                WHEN 'Propose' THEN 4
                WHEN 'Negotiate' THEN 5
                WHEN 'Closing' THEN 6
                WHEN 'Won' THEN 7
                WHEN 'Lost' THEN 8
            END
        ), 5, 2)
        ELSE 0 
    END AS DROP_OFF_PCT
FROM 
    funnel_metrics
ORDER BY 
    CASE SALES_STAGE
        WHEN 'Engage' THEN 1
        WHEN 'Design' THEN 2
        WHEN 'Qualify' THEN 3
        WHEN 'Propose' THEN 4
        WHEN 'Negotiate' THEN 5
        WHEN 'Closing' THEN 6
        WHEN 'Won' THEN 7
        WHEN 'Lost' THEN 8
    END;
```

## Conversion & Funnel Analysis

### 1. Which enterprise deals are closing in the next 30 days?

```sql
-- Enterprise deals closing soon
SELECT 
    CLIENT_NAME,
    UT30_NAME AS PRODUCT,
    OPPORTUNITY_VALUE,
    CALL_AMT AS COMMITTED_VALUE,
    PPV_AMT AS PREDICTED_VALUE,
    SALES_STAGE,
    GEOGRAPHY,
    MARKET,
    CLIENT_TYPE,
    CLIENT_SUB_TYPE,
    CASE 
        WHEN SALES_STAGE = 'Closing' THEN 'Very High'
        WHEN SALES_STAGE = 'Negotiate' AND CALL_AMT > 0 THEN 'High'
        WHEN SALES_STAGE = 'Negotiate' THEN 'Medium'
        ELSE 'Low'
    END AS CLOSE_PROBABILITY
FROM 
    PROD_MQT_CONSULTING_PIPELINE
WHERE 
    RELATIVE_QUARTER_MNEUMONIC = 'CQ'
    AND SNAPSHOT_LEVEL = 'W'
    AND WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
    AND SALES_STAGE IN ('Closing', 'Negotiate', 'Propose')
    AND (DEAL_SIZE = 'large' OR OPPORTUNITY_VALUE > 5000000)  -- Enterprise threshold
    AND CLIENT_TYPE IN ('TARGET ENTERPRISE', 'ENTERPRISE')
ORDER BY 
    CLOSE_PROBABILITY DESC, OPPORTUNITY_VALUE DESC;
```

### 2. Which deals were created from specific sources?

```sql
-- Deal source analysis (using available dimensions as proxy)
SELECT 
    PRACTICE,
    UT17_NAME AS SERVICE_LINE,
    COUNT(*) AS DEAL_COUNT,
    SUM(OPPORTUNITY_VALUE) AS TOTAL_PIPELINE,
    SUM(QUALIFY_PLUS_AMT) AS QUALIFIED_PIPELINE,
    AVG(OPPORTUNITY_VALUE) AS AVG_DEAL_SIZE,
    SUM(CASE WHEN SALES_STAGE = 'Won' THEN OPPORTUNITY_VALUE ELSE 0 END) AS WON_VALUE,
    COUNT(DISTINCT CLIENT_NAME) AS UNIQUE_CLIENTS
FROM 
    PROD_MQT_CONSULTING_PIPELINE
WHERE 
    YEAR = YEAR(CURRENT DATE)
    AND QUARTER = QUARTER(CURRENT DATE)
    AND SNAPSHOT_LEVEL = 'W'
GROUP BY 
    PRACTICE, UT17_NAME
ORDER BY 
    TOTAL_PIPELINE DESC;
```

## Predictive & Prescriptive Insights

### 1. Which deals are most likely to close this quarter?

```sql
-- Deal scoring for close probability
WITH deal_scoring AS (
    SELECT 
        CLIENT_NAME,
        UT30_NAME,
        OPPORTUNITY_VALUE,
        SALES_STAGE,
        PPV_AMT,
        CALL_AMT,
        GEOGRAPHY,
        MARKET,
        -- Scoring logic
        CASE WHEN SALES_STAGE = 'Closing' THEN 40 ELSE 0 END +
        CASE WHEN SALES_STAGE = 'Negotiate' THEN 30 ELSE 0 END +
        CASE WHEN SALES_STAGE = 'Propose' THEN 20 ELSE 0 END +
        CASE WHEN CALL_AMT > 0 THEN 20 ELSE 0 END +
        CASE WHEN PPV_AMT > OPPORTUNITY_VALUE * 0.7 THEN 10 ELSE 0 END +
        CASE WHEN DEAL_SIZE = 'small' THEN 5 ELSE 0 END AS CLOSE_SCORE
    FROM 
        PROD_MQT_CONSULTING_PIPELINE
    WHERE 
        RELATIVE_QUARTER_MNEUMONIC = 'CQ'
        AND SNAPSHOT_LEVEL = 'W'
        AND WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
        AND SALES_STAGE NOT IN ('Won', 'Lost')
)
SELECT 
    CLIENT_NAME,
    UT30_NAME AS PRODUCT,
    OPPORTUNITY_VALUE,
    SALES_STAGE,
    PPV_AMT,
    CLOSE_SCORE,
    CASE 
        WHEN CLOSE_SCORE >= 70 THEN 'Very Likely (>70% probability)'
        WHEN CLOSE_SCORE >= 50 THEN 'Likely (50-70% probability)'
        WHEN CLOSE_SCORE >= 30 THEN 'Possible (30-50% probability)'
        ELSE 'Unlikely (<30% probability)'
    END AS CLOSE_LIKELIHOOD,
    GEOGRAPHY,
    MARKET
FROM 
    deal_scoring
WHERE 
    CLOSE_SCORE >= 30  -- Focus on deals with reasonable probability
ORDER BY 
    CLOSE_SCORE DESC, OPPORTUNITY_VALUE DESC
FETCH FIRST 50 ROWS ONLY;
```

### 2. Which reps/teams/brand might miss their quota based on current pipeline?

```sql
-- Team performance vs quota risk assessment
WITH team_performance AS (
    SELECT 
        p.GEOGRAPHY,
        p.MARKET,
        p.SECTOR,
        SUM(p.WON_AMT) AS WON_TO_DATE,
        SUM(p.PPV_AMT) AS FORECAST_PIPELINE,
        SUM(p.QUALIFY_PLUS_AMT) AS QUALIFIED_PIPELINE,
        SUM(b.REVENUE_BUDGET_AMT) AS QUOTA
    FROM 
        PROD_MQT_CONSULTING_PIPELINE p
    LEFT JOIN 
        PROD_MQT_CONSULTING_BUDGET b
        ON p.GEOGRAPHY = b.GEOGRAPHY
        AND p.MARKET = b.MARKET
        AND p.SECTOR = b.SECTOR
        AND p.YEAR = b.YEAR
        AND p.QUARTER = b.QUARTER
    WHERE 
        p.RELATIVE_QUARTER_MNEUMONIC = 'CQ'
        AND p.SNAPSHOT_LEVEL = 'W'
        AND p.WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
    GROUP BY 
        p.GEOGRAPHY, p.MARKET, p.SECTOR
)
SELECT 
    GEOGRAPHY,
    MARKET,
    SECTOR,
    QUOTA,
    WON_TO_DATE,
    FORECAST_PIPELINE,
    WON_TO_DATE + FORECAST_PIPELINE AS PROJECTED_TOTAL,
    QUOTA - (WON_TO_DATE + FORECAST_PIPELINE) AS GAP_TO_QUOTA,
    CASE 
        WHEN QUOTA > 0 
        THEN DECIMAL((WON_TO_DATE + FORECAST_PIPELINE) / QUOTA * 100, 5, 2) 
        ELSE 0 
    END AS PROJECTED_ATTAINMENT_PCT,
    CASE 
        WHEN (WON_TO_DATE + FORECAST_PIPELINE) < QUOTA * 0.7 THEN 'High Risk - Below 70%'
        WHEN (WON_TO_DATE + FORECAST_PIPELINE) < QUOTA * 0.9 THEN 'Medium Risk - Below 90%'
        WHEN (WON_TO_DATE + FORECAST_PIPELINE) < QUOTA THEN 'Low Risk - Below 100%'
        ELSE 'On Track'
    END AS RISK_LEVEL
FROM 
    team_performance
WHERE 
    QUOTA > 0
ORDER BY 
    PROJECTED_ATTAINMENT_PCT ASC;
```

### 3. What actions should I take to improve my close rate?

```sql
-- Close rate improvement recommendations
WITH performance_metrics AS (
    SELECT 
        GEOGRAPHY,
        MARKET,
        -- Win rates
        SUM(CASE WHEN SALES_STAGE = 'Won' THEN 1 ELSE 0 END) AS WON_DEALS,
        SUM(CASE WHEN SALES_STAGE IN ('Won', 'Lost') THEN 1 ELSE 0 END) AS CLOSED_DEALS,
        -- Pipeline composition
        SUM(CASE WHEN SALES_STAGE = 'Closing' THEN OPPORTUNITY_VALUE ELSE 0 END) AS CLOSING_VALUE,
        SUM(CASE WHEN SALES_STAGE IN ('Qualify', 'Design') THEN OPPORTUNITY_VALUE ELSE 0 END) AS EARLY_STAGE_VALUE,
        SUM(QUALIFY_PLUS_AMT) AS TOTAL_QUALIFIED,
        -- Deal characteristics
        AVG(OPPORTUNITY_VALUE) AS AVG_DEAL_SIZE,
        COUNT(DISTINCT CLIENT_NAME) AS CLIENT_DIVERSITY,
        SUM(CASE WHEN DEAL_SIZE = 'large' THEN 1 ELSE 0 END) AS LARGE_DEALS
    FROM 
        PROD_MQT_CONSULTING_PIPELINE
    WHERE 
        YEAR = YEAR(CURRENT DATE)
        AND SNAPSHOT_LEVEL = 'W'
    GROUP BY 
        GEOGRAPHY, MARKET
)
SELECT 
    GEOGRAPHY,
    MARKET,
    CASE 
        WHEN CLOSED_DEALS > 0 
        THEN DECIMAL(WON_DEALS * 100.0 / CLOSED_DEALS, 5, 2) 
        ELSE 0 
    END AS WIN_RATE,
    -- Recommendations based on metrics
    CASE 
        WHEN CLOSING_VALUE < TOTAL_QUALIFIED * 0.2 
        THEN 'Action 1: Move more deals to closing stage - increase urgency'
        WHEN AVG_DEAL_SIZE < 100000 
        THEN 'Action 1: Focus on larger deals - qualify for budget early'
        WHEN CLIENT_DIVERSITY < 10 
        THEN 'Action 1: Diversify client base - reduce concentration risk'
        ELSE 'Action 1: Maintain current approach'
    END AS PRIMARY_ACTION,
    CASE 
        WHEN EARLY_STAGE_VALUE > TOTAL_QUALIFIED * 0.6 
        THEN 'Action 2: Accelerate deal velocity - implement stage gates'
        WHEN LARGE_DEALS = 0 
        THEN 'Action 2: Target enterprise accounts - leverage executive sponsors'
        WHEN WON_DEALS * 100.0 / NULLIF(CLOSED_DEALS, 0) < 30 
        THEN 'Action 2: Improve qualification criteria - focus on fit'
        ELSE 'Action 2: Continue current practices'
    END AS SECONDARY_ACTION,
    -- Key metrics
    AVG_DEAL_SIZE,
    CLIENT_DIVERSITY,
    LARGE_DEALS
FROM 
    performance_metrics
ORDER BY 
    WIN_RATE ASC;
```

## Activity & Follow-up

### 1. Which deals need follow-up this week?

```sql
-- Priority follow-up list
SELECT 
    CLIENT_NAME,
    UT30_NAME AS PRODUCT,
    OPPORTUNITY_VALUE,
    SALES_STAGE,
    PPV_AMT,
    GEOGRAPHY,
    MARKET,
    CASE 
        WHEN SALES_STAGE = 'Negotiate' AND CALL_AMT = 0 
        THEN 'Critical - In Negotiate without commitment'
        WHEN SALES_STAGE = 'Propose' AND UPSIDE_AMT > 0 
        THEN 'High - Proposal needs push'
        WHEN SALES_STAGE = 'Qualify' AND OPPORTUNITY_VALUE > 1000000 
        THEN 'High - Large deal in early stage'
        WHEN PPV_AMT < OPPORTUNITY_VALUE * 0.3 
        THEN 'Medium - Low PPV score'
        ELSE 'Standard follow-up'
    END AS FOLLOW_UP_PRIORITY,
    CASE 
        WHEN SALES_STAGE = 'Negotiate' 
        THEN 'Schedule executive meeting to close'
        WHEN SALES_STAGE = 'Propose' 
        THEN 'Address proposal questions and objections'
        WHEN SALES_STAGE = 'Qualify' 
        THEN 'Confirm budget and decision criteria'
        ELSE 'Standard check-in'
    END AS RECOMMENDED_ACTION
FROM 
    PROD_MQT_CONSULTING_PIPELINE
WHERE 
    RELATIVE_QUARTER_MNEUMONIC = 'CQ'
    AND SNAPSHOT_LEVEL = 'W'
    AND WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
    AND SALES_STAGE NOT IN ('Won', 'Lost', 'Closing')
ORDER BY 
    CASE 
        WHEN SALES_STAGE = 'Negotiate' AND CALL_AMT = 0 THEN 1
        WHEN SALES_STAGE = 'Propose' AND UPSIDE_AMT > 0 THEN 2
        WHEN SALES_STAGE = 'Qualify' AND OPPORTUNITY_VALUE > 1000000 THEN 3
        ELSE 4
    END,
    OPPORTUNITY_VALUE DESC
FETCH FIRST 25 ROWS ONLY;
```

### 2. Which prospects haven't been contacted in 10+ days?

```sql
-- This would require activity tracking data not available in current tables
-- Using pipeline age as a proxy
SELECT 
    CLIENT_NAME,
    UT30_NAME AS PRODUCT,
    OPPORTUNITY_VALUE,
    SALES_STAGE,
    GEOGRAPHY,
    MARKET,
    'No recent activity detected' AS STATUS,
    'Immediate outreach required' AS ACTION_REQUIRED
FROM 
    PROD_MQT_CONSULTING_PIPELINE
WHERE 
    RELATIVE_QUARTER_MNEUMONIC = 'CQ'
    AND SNAPSHOT_LEVEL = 'W'
    AND WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
    AND SALES_STAGE IN ('Qualify', 'Design', 'Engage')
    AND UPSIDE_AMT > 0  -- Has potential but not committed
ORDER BY 
    OPPORTUNITY_VALUE DESC
FETCH FIRST 50 ROWS ONLY;
```

### 3. How many people have we touched in x organization in the last 90 days?

```sql
-- Organization engagement summary
SELECT 
    CLIENT_NAME,
    COUNT(DISTINCT UT30_NAME) AS PRODUCTS_DISCUSSED,
    COUNT(*) AS TOTAL_OPPORTUNITIES,
    SUM(OPPORTUNITY_VALUE) AS TOTAL_OPPORTUNITY_VALUE,
    SUM(CASE WHEN SALES_STAGE NOT IN ('Won', 'Lost') THEN 1 ELSE 0 END) AS ACTIVE_OPPORTUNITIES,
    SUM(CASE WHEN SALES_STAGE = 'Won' THEN 1 ELSE 0 END) AS WON_OPPORTUNITIES,
    STRING_AGG(DISTINCT SALES_STAGE, ', ') AS STAGES_ENGAGED,
    MAX(QUARTER || 'Q' || YEAR) AS LAST_ACTIVITY_QUARTER
FROM 
    PROD_MQT_CONSULTING_PIPELINE
WHERE 
    YEAR = YEAR(CURRENT DATE)
    AND CLIENT_NAME IN (
        SELECT DISTINCT CLIENT_NAME 
        FROM PROD_MQT_CONSULTING_PIPELINE 
        WHERE YEAR = YEAR(CURRENT DATE)
    )
GROUP BY 
    CLIENT_NAME
HAVING 
    COUNT(*) > 1  -- Organizations with multiple touchpoints
ORDER BY 
    TOTAL_OPPORTUNITY_VALUE DESC;
```

## Real-Time Alerts

### 1. High-value deals entering specific stages

```sql
-- High-value deal alerts
SELECT 
    'ALERT: High-Value Deal in ' || SALES_STAGE AS ALERT_TYPE,
    CLIENT_NAME,
    UT30_NAME AS PRODUCT,
    OPPORTUNITY_VALUE,
    SALES_STAGE,
    PPV_AMT,
    GEOGRAPHY,
    MARKET,
    CURRENT TIMESTAMP AS ALERT_TIME
FROM 
    PROD_MQT_CONSULTING_PIPELINE
WHERE 
    RELATIVE_QUARTER_MNEUMONIC = 'CQ'
    AND SNAPSHOT_LEVEL = 'W'
    AND WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
    AND OPPORTUNITY_VALUE > 5000000  -- High-value threshold
    AND SALES_STAGE IN ('Negotiate', 'Closing')
ORDER BY 
    OPPORTUNITY_VALUE DESC;
```

### 2. Inactive deal alerts

```sql
-- Stalled deal alerts
WITH deal_activity AS (
    SELECT 
        p1.CLIENT_NAME,
        p1.UT30_NAME,
        p1.OPPORTUNITY_VALUE,
        p1.SALES_STAGE,
        p1.GEOGRAPHY,
        p1.MARKET,
        CASE 
            WHEN p1.SALES_STAGE = COALESCE(p2.SALES_STAGE, p1.SALES_STAGE) 
            AND p1.OPPORTUNITY_VALUE = COALESCE(p2.OPPORTUNITY_VALUE, p1.OPPORTUNITY_VALUE)
            THEN 'No Change Detected'
            ELSE 'Active'
        END AS ACTIVITY_STATUS
    FROM 
        PROD_MQT_CONSULTING_PIPELINE p1
    LEFT JOIN 
        PROD_MQT_CONSULTING_PIPELINE p2
        ON p1.CLIENT_NAME = p2.CLIENT_NAME
        AND p1.UT30_NAME = p2.UT30_NAME
        AND p1.YEAR = p2.YEAR
        AND p1.QUARTER = p2.QUARTER
        AND p1.WEEK = p2.WEEK + 4  -- 4 weeks ago
    WHERE 
        p1.RELATIVE_QUARTER_MNEUMONIC = 'CQ'
        AND p1.SNAPSHOT_LEVEL = 'W'
        AND p1.WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
        AND p1.SALES_STAGE NOT IN ('Won', 'Lost')
)
SELECT 
    'ALERT: Deal Inactive 30+ Days' AS ALERT_TYPE,
    CLIENT_NAME,
    UT30_NAME AS PRODUCT,
    OPPORTUNITY_VALUE,
    SALES_STAGE,
    GEOGRAPHY,
    MARKET,
    'Immediate action required - Risk of deal going cold' AS ACTION_REQUIRED,
    CURRENT TIMESTAMP AS ALERT_TIME
FROM 
    deal_activity
WHERE 
    ACTIVITY_STATUS = 'No Change Detected'
    AND OPPORTUNITY_VALUE > 100000  -- Focus on significant deals
ORDER BY 
    OPPORTUNITY_VALUE DESC;
```

### 3. Lost deal notifications

```sql
-- Lost deal analysis
SELECT 
    'ALERT: Deal Lost' AS ALERT_TYPE,
    CLIENT_NAME,
    UT30_NAME AS PRODUCT,
    OPPORTUNITY_VALUE,
    GEOGRAPHY,
    MARKET,
    PRACTICE,
    'Review loss reasons and capture lessons learned' AS ACTION_REQUIRED,
    CURRENT TIMESTAMP AS ALERT_TIME
FROM 
    PROD_MQT_CONSULTING_PIPELINE
WHERE 
    RELATIVE_QUARTER_MNEUMONIC = 'CQ'
    AND SNAPSHOT_LEVEL = 'W'
    AND WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
    AND SALES_STAGE = 'Lost'
    AND OPPORTUNITY_VALUE > 500000  -- Significant lost deals
ORDER BY 
    OPPORTUNITY_VALUE DESC;
```

## Notes on Query Implementation

1. **Segmentation**: All queries can be modified to add WHERE clauses for specific:
   - Geography (Americas, APAC, EMEA, etc.)
   - Market segments
   - UT levels (UT15, UT17, UT20, UT30)
   - Routes/Practices
   - Time periods

2. **Performance Considerations**:
   - Use appropriate indexes on frequently filtered columns
   - Consider materialized views for complex aggregations
   - Implement query result caching for real-time dashboards

3. **Data Limitations**:
   - Some queries (like rep-level performance) require additional data not in current tables
   - Activity tracking would need integration with CRM activity logs
   - Real-time alerts would need a scheduling/monitoring system

4. **Customization**:
   - Thresholds (deal size, time periods) can be parameterized
   - Additional filters can be added based on business rules
   - Queries can be combined for comprehensive dashboards