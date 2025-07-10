# Sales Pipeline Insights Agent - SQL Query Guide

## Table of Contents
1. [Data Model Overview](#data-model-overview)
2. [Key Metrics Definitions](#key-metrics-definitions)
3. [Core SQL Queries](#core-sql-queries)
4. [Advanced Analytics Queries](#advanced-analytics-queries)
5. [Performance Optimization Tips](#performance-optimization-tips)

## Data Model Overview

### Primary MQT Tables

#### 1. PROD_MQT_CONSULTING_PIPELINE
Contains opportunity pipeline data with various sales stages and financial metrics.

**Key Columns:**
- `CALL_AMT`: Committed pipeline amount (FLM Judgement)
- `WON_AMT`: Won opportunities amount
- `UPSIDE_AMT`: Upside opportunities (Negotiate/Propose without FLM commitment)
- `QUALIFY_PLUS_AMT`: Opportunities in Qualify+ stages (Design, Propose, Negotiate, Qualify, Closing)
- `PROPOSE_PLUS_AMT`: Opportunities in Propose and later stages
- `NEGOTIATE_PLUS_AMT`: Opportunities in Negotiate and later stages
- `OPEN_PIPELINE_AMT`: Total open pipeline
- `OPPORTUNITY_VALUE`: Total opportunity value
- `PPV_AMT`: PERFORM Pipeline Value (end-of-quarter assessment)
- `WEEK`, `QUARTER`, `YEAR`: Time dimensions
- `GEOGRAPHY`, `MARKET`, `SECTOR`: Territory dimensions
- `UT15_NAME`, `UT17_NAME`, `UT20_NAME`, `UT30_NAME`: Unified Taxonomy hierarchy
- `SALES_STAGE`: Current sales stage of opportunity
- `CLIENT_NAME`: Customer name
- `_PY` suffix columns: Prior Year values
- `_PPY` suffix columns: Prior Prior Year values

#### 2. PROD_MQT_CONSULTING_BUDGET
Contains budget targets by territory and time period.

**Key Columns:**
- `REVENUE_BUDGET_AMT`: Revenue budget amount
- `SIGNINGS_BUDGET_AMT`: Signings budget amount
- `GROSS_PROFIT_BUDGET_AMT`: Gross profit budget
- `YEAR`, `QUARTER`, `MONTH`: Time dimensions
- `GEOGRAPHY`, `MARKET`, `SECTOR`: Territory dimensions
- `INDUSTRY`, `CLIENT_NAME`: Customer dimensions
- `UT15_NAME`, `UT17_NAME`, `UT20_NAME`, `UT30_NAME`: Product hierarchy

#### 3. PROD_MQT_CONSULTING_REVENUE_ACTUALS
Contains actual revenue and gross profit performance.

**Key Columns:**
- `REVENUE_AMT`: Actual revenue amount
- `GROSS_PROFIT_AMT`: Actual gross profit amount
- `REVENUE_AMT_PY`: Prior year revenue
- `GROSS_PROFIT_AMT_PY`: Prior year gross profit
- Time, territory, and product dimensions similar to budget table

#### 4. PROD_MQT_SOFTWARE_TRANSACTIONAL_PIPELINE
Contains software transactional pipeline data with similar structure to consulting pipeline.

## Key Metrics Definitions

### Core Metrics

1. **Budget ($M)**: Target revenue/signings set for sales leaders
2. **YtY% (Year-over-Year)**: Growth comparison vs same period last year
   - Formula: `((Current Year - Prior Year) / Prior Year) * 100`
3. **PPV Cov% (PPV Coverage)**: Pipeline coverage vs budget
   - Formula: `(PPV_AMT / BUDGET_AMT) * 100`
4. **Qualify+ ($M)**: Pipeline in advanced stages (Design, Propose, Negotiate, Qualify, Closing)
5. **WtW (Week-to-Week)**: Change from previous week
   - Formula: `Current Week - Prior Week`
6. **Multiplier**: Pipeline coverage needed to hit target
   - Formula: `QUALIFY_PLUS_AMT / BUDGET_AMT`
7. **Tracks**: 4x budget target as of week 1 of quarter

## Core SQL Queries

### 1. Pipeline Summary by Geography and Market

```sql
-- Current Quarter Pipeline Summary
SELECT 
    p.GEOGRAPHY,
    p.MARKET,
    p.YEAR,
    p.QUARTER,
    p.WEEK,
    SUM(p.CALL_AMT) AS CALL_PIPELINE,
    SUM(p.WON_AMT) AS WON_DEALS,
    SUM(p.UPSIDE_AMT) AS UPSIDE,
    SUM(p.QUALIFY_PLUS_AMT) AS QUALIFY_PLUS,
    SUM(p.PPV_AMT) AS PPV,
    SUM(b.REVENUE_BUDGET_AMT) AS BUDGET,
    CASE 
        WHEN SUM(b.REVENUE_BUDGET_AMT) > 0 
        THEN DECIMAL(SUM(p.PPV_AMT) / SUM(b.REVENUE_BUDGET_AMT) * 100, 5, 2)
        ELSE 0 
    END AS PPV_COVERAGE_PCT,
    CASE 
        WHEN SUM(b.REVENUE_BUDGET_AMT) > 0 
        THEN DECIMAL(SUM(p.QUALIFY_PLUS_AMT) / SUM(b.REVENUE_BUDGET_AMT), 5, 2)
        ELSE 0 
    END AS MULTIPLIER
FROM 
    PROD_MQT_CONSULTING_PIPELINE p
LEFT JOIN 
    PROD_MQT_CONSULTING_BUDGET b
    ON p.GEOGRAPHY = b.GEOGRAPHY 
    AND p.MARKET = b.MARKET
    AND p.YEAR = b.YEAR
    AND p.QUARTER = b.QUARTER
WHERE 
    p.RELATIVE_QUARTER_MNEUMONIC = 'CQ'
    AND p.SNAPSHOT_LEVEL = 'W'
    AND p.WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE YEAR = p.YEAR AND QUARTER = p.QUARTER)
GROUP BY 
    p.GEOGRAPHY, p.MARKET, p.YEAR, p.QUARTER, p.WEEK
ORDER BY 
    p.GEOGRAPHY, p.MARKET;
```

### 2. Year-over-Year Performance Analysis

```sql
-- YoY Performance by Market
SELECT 
    p.GEOGRAPHY,
    p.MARKET,
    p.YEAR,
    p.QUARTER,
    SUM(p.QUALIFY_PLUS_AMT) AS QUALIFY_PLUS_CY,
    SUM(p.QUALIFY_PLUS_AMT_PY) AS QUALIFY_PLUS_PY,
    CASE 
        WHEN SUM(p.QUALIFY_PLUS_AMT_PY) > 0 
        THEN DECIMAL((SUM(p.QUALIFY_PLUS_AMT) - SUM(p.QUALIFY_PLUS_AMT_PY)) / SUM(p.QUALIFY_PLUS_AMT_PY) * 100, 5, 2)
        ELSE NULL 
    END AS YOY_GROWTH_PCT,
    SUM(b.REVENUE_BUDGET_AMT) AS BUDGET_CY,
    SUM(b_py.REVENUE_BUDGET_AMT) AS BUDGET_PY,
    CASE 
        WHEN SUM(b_py.REVENUE_BUDGET_AMT) > 0 
        THEN DECIMAL((SUM(b.REVENUE_BUDGET_AMT) - SUM(b_py.REVENUE_BUDGET_AMT)) / SUM(b_py.REVENUE_BUDGET_AMT) * 100, 5, 2)
        ELSE NULL 
    END AS BUDGET_YOY_PCT
FROM 
    PROD_MQT_CONSULTING_PIPELINE p
LEFT JOIN 
    PROD_MQT_CONSULTING_BUDGET b
    ON p.GEOGRAPHY = b.GEOGRAPHY 
    AND p.MARKET = b.MARKET
    AND p.YEAR = b.YEAR
    AND p.QUARTER = b.QUARTER
LEFT JOIN 
    PROD_MQT_CONSULTING_BUDGET b_py
    ON p.GEOGRAPHY = b_py.GEOGRAPHY 
    AND p.MARKET = b_py.MARKET
    AND p.YEAR - 1 = b_py.YEAR
    AND p.QUARTER = b_py.QUARTER
WHERE 
    p.RELATIVE_QUARTER_MNEUMONIC = 'CQ'
    AND p.SNAPSHOT_LEVEL = 'W'
    AND p.WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE YEAR = p.YEAR AND QUARTER = p.QUARTER)
GROUP BY 
    p.GEOGRAPHY, p.MARKET, p.YEAR, p.QUARTER
ORDER BY 
    YOY_GROWTH_PCT DESC;
```

### 3. Week-to-Week Pipeline Movement

```sql
-- WtW Pipeline Movement Analysis
WITH current_week AS (
    SELECT 
        GEOGRAPHY,
        MARKET,
        YEAR,
        QUARTER,
        WEEK,
        SUM(QUALIFY_PLUS_AMT) AS QUALIFY_PLUS_CW,
        SUM(CALL_AMT) AS CALL_CW,
        SUM(UPSIDE_AMT) AS UPSIDE_CW
    FROM 
        PROD_MQT_CONSULTING_PIPELINE
    WHERE 
        RELATIVE_QUARTER_MNEUMONIC = 'CQ'
        AND SNAPSHOT_LEVEL = 'W'
        AND WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
    GROUP BY 
        GEOGRAPHY, MARKET, YEAR, QUARTER, WEEK
),
prior_week AS (
    SELECT 
        GEOGRAPHY,
        MARKET,
        YEAR,
        QUARTER,
        WEEK,
        SUM(QUALIFY_PLUS_AMT) AS QUALIFY_PLUS_PW,
        SUM(CALL_AMT) AS CALL_PW,
        SUM(UPSIDE_AMT) AS UPSIDE_PW
    FROM 
        PROD_MQT_CONSULTING_PIPELINE
    WHERE 
        RELATIVE_QUARTER_MNEUMONIC = 'CQ'
        AND SNAPSHOT_LEVEL = 'W'
        AND WEEK = (SELECT MAX(WEEK) - 1 FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
    GROUP BY 
        GEOGRAPHY, MARKET, YEAR, QUARTER, WEEK
)
SELECT 
    cw.GEOGRAPHY,
    cw.MARKET,
    cw.QUALIFY_PLUS_CW,
    pw.QUALIFY_PLUS_PW,
    cw.QUALIFY_PLUS_CW - COALESCE(pw.QUALIFY_PLUS_PW, 0) AS QUALIFY_PLUS_WTW,
    CASE 
        WHEN pw.QUALIFY_PLUS_PW > 0 
        THEN DECIMAL((cw.QUALIFY_PLUS_CW - pw.QUALIFY_PLUS_PW) / pw.QUALIFY_PLUS_PW * 100, 5, 2)
        ELSE NULL 
    END AS QUALIFY_PLUS_WTW_PCT,
    cw.CALL_CW - COALESCE(pw.CALL_PW, 0) AS CALL_WTW,
    cw.UPSIDE_CW - COALESCE(pw.UPSIDE_PW, 0) AS UPSIDE_WTW
FROM 
    current_week cw
LEFT JOIN 
    prior_week pw
    ON cw.GEOGRAPHY = pw.GEOGRAPHY 
    AND cw.MARKET = pw.MARKET
ORDER BY 
    QUALIFY_PLUS_WTW DESC;
```

### 4. Sales Stage Analysis

```sql
-- Pipeline by Sales Stage
SELECT 
    GEOGRAPHY,
    MARKET,
    SALES_STAGE,
    COUNT(DISTINCT CLIENT_NAME) AS CLIENT_COUNT,
    SUM(OPPORTUNITY_VALUE) AS TOTAL_PIPELINE,
    SUM(PPV_AMT) AS TOTAL_PPV,
    AVG(OPPORTUNITY_VALUE) AS AVG_DEAL_SIZE,
    CASE 
        WHEN SALES_STAGE IN ('Closing', 'Negotiate', 'Propose') 
        THEN 'Advanced'
        WHEN SALES_STAGE IN ('Qualify', 'Design') 
        THEN 'Mid-Stage'
        ELSE 'Early-Stage' 
    END AS STAGE_CATEGORY
FROM 
    PROD_MQT_CONSULTING_PIPELINE
WHERE 
    RELATIVE_QUARTER_MNEUMONIC = 'CQ'
    AND SNAPSHOT_LEVEL = 'W'
    AND WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
    AND SALES_STAGE NOT IN ('Won', 'Lost')
GROUP BY 
    GEOGRAPHY, MARKET, SALES_STAGE
ORDER BY 
    GEOGRAPHY, MARKET, 
    CASE SALES_STAGE
        WHEN 'Closing' THEN 1
        WHEN 'Negotiate' THEN 2
        WHEN 'Propose' THEN 3
        WHEN 'Qualify' THEN 4
        WHEN 'Design' THEN 5
        ELSE 6
    END;
```

### 5. UT Hierarchy Performance Analysis

```sql
-- Performance by UT Level 17
SELECT 
    p.UT17_NAME,
    p.GEOGRAPHY,
    SUM(p.QUALIFY_PLUS_AMT) AS QUALIFY_PLUS,
    SUM(p.PPV_AMT) AS PPV,
    SUM(b.REVENUE_BUDGET_AMT) AS BUDGET,
    CASE 
        WHEN SUM(b.REVENUE_BUDGET_AMT) > 0 
        THEN DECIMAL(SUM(p.PPV_AMT) / SUM(b.REVENUE_BUDGET_AMT) * 100, 5, 2)
        ELSE 0 
    END AS PPV_COVERAGE_PCT,
    COUNT(DISTINCT p.CLIENT_NAME) AS ACTIVE_CLIENTS,
    AVG(p.OPPORTUNITY_VALUE) AS AVG_DEAL_SIZE
FROM 
    PROD_MQT_CONSULTING_PIPELINE p
LEFT JOIN 
    PROD_MQT_CONSULTING_BUDGET b
    ON p.GEOGRAPHY = b.GEOGRAPHY 
    AND p.MARKET = b.MARKET
    AND p.UT17_NAME = b.UT17_NAME
    AND p.YEAR = b.YEAR
    AND p.QUARTER = b.QUARTER
WHERE 
    p.RELATIVE_QUARTER_MNEUMONIC = 'CQ'
    AND p.SNAPSHOT_LEVEL = 'W'
    AND p.WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
GROUP BY 
    p.UT17_NAME, p.GEOGRAPHY
HAVING 
    SUM(p.QUALIFY_PLUS_AMT) > 0
ORDER BY 
    PPV_COVERAGE_PCT DESC;
```

### 6. Budget vs Actuals Analysis

```sql
-- Budget vs Actuals with Gap Analysis
SELECT 
    a.GEOGRAPHY,
    a.MARKET,
    a.YEAR,
    a.QUARTER,
    a.MONTH,
    SUM(a.REVENUE_AMT) AS ACTUAL_REVENUE,
    SUM(b.REVENUE_BUDGET_AMT) AS BUDGET_REVENUE,
    SUM(a.REVENUE_AMT) - SUM(b.REVENUE_BUDGET_AMT) AS REVENUE_GAP,
    CASE 
        WHEN SUM(b.REVENUE_BUDGET_AMT) > 0 
        THEN DECIMAL(SUM(a.REVENUE_AMT) / SUM(b.REVENUE_BUDGET_AMT) * 100, 5, 2)
        ELSE 0 
    END AS ATTAINMENT_PCT,
    SUM(a.GROSS_PROFIT_AMT) AS ACTUAL_GP,
    SUM(b.GROSS_PROFIT_BUDGET_AMT) AS BUDGET_GP,
    CASE 
        WHEN SUM(a.REVENUE_AMT) > 0 
        THEN DECIMAL(SUM(a.GROSS_PROFIT_AMT) / SUM(a.REVENUE_AMT) * 100, 5, 2)
        ELSE 0 
    END AS GP_MARGIN_PCT
FROM 
    PROD_MQT_CONSULTING_REVENUE_ACTUALS a
LEFT JOIN 
    PROD_MQT_CONSULTING_BUDGET b
    ON a.GEOGRAPHY = b.GEOGRAPHY 
    AND a.MARKET = b.MARKET
    AND a.YEAR = b.YEAR
    AND a.QUARTER = b.QUARTER
    AND a.MONTH = b.MONTH
WHERE 
    a.YEAR = YEAR(CURRENT DATE)
GROUP BY 
    a.GEOGRAPHY, a.MARKET, a.YEAR, a.QUARTER, a.MONTH
ORDER BY 
    a.GEOGRAPHY, a.MARKET, a.YEAR, a.QUARTER, a.MONTH;
```

### 7. Pipeline Velocity Tracking

```sql
-- Pipeline Velocity - Track progression through stages
WITH stage_progression AS (
    SELECT 
        CLIENT_NAME,
        UT30_NAME,
        GEOGRAPHY,
        MARKET,
        SALES_STAGE,
        WEEK,
        OPPORTUNITY_VALUE,
        LEAD(SALES_STAGE) OVER (PARTITION BY CLIENT_NAME, UT30_NAME ORDER BY WEEK) AS NEXT_STAGE,
        LEAD(WEEK) OVER (PARTITION BY CLIENT_NAME, UT30_NAME ORDER BY WEEK) AS NEXT_WEEK
    FROM 
        PROD_MQT_CONSULTING_PIPELINE
    WHERE 
        YEAR = YEAR(CURRENT DATE)
        AND QUARTER = QUARTER(CURRENT DATE)
)
SELECT 
    GEOGRAPHY,
    MARKET,
    SALES_STAGE AS FROM_STAGE,
    NEXT_STAGE AS TO_STAGE,
    COUNT(*) AS TRANSITION_COUNT,
    AVG(NEXT_WEEK - WEEK) AS AVG_WEEKS_IN_STAGE,
    SUM(OPPORTUNITY_VALUE) AS PIPELINE_VALUE
FROM 
    stage_progression
WHERE 
    NEXT_STAGE IS NOT NULL
    AND SALES_STAGE != NEXT_STAGE
GROUP BY 
    GEOGRAPHY, MARKET, SALES_STAGE, NEXT_STAGE
ORDER BY 
    GEOGRAPHY, MARKET, FROM_STAGE;
```

## Advanced Analytics Queries

### 1. Top Performing Territories

```sql
-- Territory Performance Ranking
WITH territory_metrics AS (
    SELECT 
        p.GEOGRAPHY,
        p.MARKET,
        p.SECTOR,
        SUM(p.QUALIFY_PLUS_AMT) AS QUALIFY_PLUS,
        SUM(p.PPV_AMT) AS PPV,
        SUM(p.WON_AMT) AS WON,
        SUM(b.REVENUE_BUDGET_AMT) AS BUDGET,
        CASE 
            WHEN SUM(b.REVENUE_BUDGET_AMT) > 0 
            THEN DECIMAL(SUM(p.PPV_AMT) / SUM(b.REVENUE_BUDGET_AMT), 5, 2)
            ELSE 0 
        END AS PPV_COVERAGE,
        CASE 
            WHEN SUM(p.QUALIFY_PLUS_AMT_PY) > 0 
            THEN DECIMAL((SUM(p.QUALIFY_PLUS_AMT) - SUM(p.QUALIFY_PLUS_AMT_PY)) / SUM(p.QUALIFY_PLUS_AMT_PY) * 100, 5, 2)
            ELSE NULL 
        END AS YOY_GROWTH
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
    QUALIFY_PLUS,
    PPV,
    BUDGET,
    PPV_COVERAGE,
    YOY_GROWTH,
    RANK() OVER (ORDER BY PPV_COVERAGE DESC) AS PPV_RANK,
    RANK() OVER (ORDER BY YOY_GROWTH DESC) AS GROWTH_RANK,
    RANK() OVER (ORDER BY QUALIFY_PLUS DESC) AS PIPELINE_RANK
FROM 
    territory_metrics
WHERE 
    BUDGET > 0
ORDER BY 
    PPV_COVERAGE DESC;
```

### 2. Client Pipeline Analysis

```sql
-- Top Clients by Pipeline Value
SELECT 
    CLIENT_NAME,
    GEOGRAPHY,
    MARKET,
    COUNT(DISTINCT UT30_NAME) AS PRODUCT_COUNT,
    SUM(QUALIFY_PLUS_AMT) AS TOTAL_QUALIFY_PLUS,
    SUM(CALL_AMT) AS TOTAL_CALL,
    SUM(UPSIDE_AMT) AS TOTAL_UPSIDE,
    SUM(PPV_AMT) AS TOTAL_PPV,
    MAX(OPPORTUNITY_VALUE) AS LARGEST_DEAL,
    AVG(OPPORTUNITY_VALUE) AS AVG_DEAL_SIZE,
    SUM(CASE WHEN SALES_STAGE = 'Closing' THEN OPPORTUNITY_VALUE ELSE 0 END) AS CLOSING_PIPELINE,
    SUM(CASE WHEN IBM_GEN_AI_IND = 1 THEN OPPORTUNITY_VALUE ELSE 0 END) AS GEN_AI_PIPELINE
FROM 
    PROD_MQT_CONSULTING_PIPELINE
WHERE 
    RELATIVE_QUARTER_MNEUMONIC = 'CQ'
    AND SNAPSHOT_LEVEL = 'W'
    AND WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
    AND SALES_STAGE NOT IN ('Won', 'Lost')
GROUP BY 
    CLIENT_NAME, GEOGRAPHY, MARKET
HAVING 
    SUM(QUALIFY_PLUS_AMT) > 1000000  -- Focus on major clients
ORDER BY 
    TOTAL_QUALIFY_PLUS DESC
FETCH FIRST 50 ROWS ONLY;
```

### 3. Pipeline Health Metrics

```sql
-- Pipeline Health Dashboard
WITH pipeline_metrics AS (
    SELECT 
        p.GEOGRAPHY,
        p.MARKET,
        -- Pipeline Stage Distribution
        SUM(CASE WHEN p.SALES_STAGE = 'Closing' THEN p.OPPORTUNITY_VALUE ELSE 0 END) AS CLOSING_AMT,
        SUM(CASE WHEN p.SALES_STAGE = 'Negotiate' THEN p.OPPORTUNITY_VALUE ELSE 0 END) AS NEGOTIATE_AMT,
        SUM(CASE WHEN p.SALES_STAGE = 'Propose' THEN p.OPPORTUNITY_VALUE ELSE 0 END) AS PROPOSE_AMT,
        SUM(CASE WHEN p.SALES_STAGE = 'Qualify' THEN p.OPPORTUNITY_VALUE ELSE 0 END) AS QUALIFY_AMT,
        SUM(p.QUALIFY_PLUS_AMT) AS TOTAL_QUALIFY_PLUS,
        -- Deal Size Distribution
        COUNT(CASE WHEN p.DEAL_SIZE = 'small' THEN 1 END) AS SMALL_DEALS,
        COUNT(CASE WHEN p.DEAL_SIZE = 'medium' THEN 1 END) AS MEDIUM_DEALS,
        COUNT(CASE WHEN p.DEAL_SIZE = 'large' THEN 1 END) AS LARGE_DEALS,
        -- Budget and Coverage
        SUM(b.REVENUE_BUDGET_AMT) AS BUDGET,
        SUM(p.PPV_AMT) AS PPV
    FROM 
        PROD_MQT_CONSULTING_PIPELINE p
    LEFT JOIN 
        PROD_MQT_CONSULTING_BUDGET b
        ON p.GEOGRAPHY = b.GEOGRAPHY 
        AND p.MARKET = b.MARKET
        AND p.YEAR = b.YEAR
        AND p.QUARTER = b.QUARTER
    WHERE 
        p.RELATIVE_QUARTER_MNEUMONIC = 'CQ'
        AND p.SNAPSHOT_LEVEL = 'W'
        AND p.WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
        AND p.SALES_STAGE NOT IN ('Won', 'Lost')
    GROUP BY 
        p.GEOGRAPHY, p.MARKET
)
SELECT 
    GEOGRAPHY,
    MARKET,
    -- Stage Distribution Percentages
    DECIMAL(CLOSING_AMT / NULLIF(TOTAL_QUALIFY_PLUS, 0) * 100, 5, 2) AS CLOSING_PCT,
    DECIMAL(NEGOTIATE_AMT / NULLIF(TOTAL_QUALIFY_PLUS, 0) * 100, 5, 2) AS NEGOTIATE_PCT,
    DECIMAL(PROPOSE_AMT / NULLIF(TOTAL_QUALIFY_PLUS, 0) * 100, 5, 2) AS PROPOSE_PCT,
    DECIMAL(QUALIFY_AMT / NULLIF(TOTAL_QUALIFY_PLUS, 0) * 100, 5, 2) AS QUALIFY_PCT,
    -- Deal Mix
    SMALL_DEALS,
    MEDIUM_DEALS,
    LARGE_DEALS,
    -- Coverage Metrics
    DECIMAL(PPV / NULLIF(BUDGET, 0) * 100, 5, 2) AS PPV_COVERAGE_PCT,
    DECIMAL(TOTAL_QUALIFY_PLUS / NULLIF(BUDGET, 0), 5, 2) AS MULTIPLIER,
    -- Health Score (weighted composite)
    DECIMAL(
        (CLOSING_AMT / NULLIF(TOTAL_QUALIFY_PLUS, 0) * 40) +  -- Weight closing higher
        (PPV / NULLIF(BUDGET, 0) * 100 * 0.3) +               -- PPV coverage
        (CASE WHEN LARGE_DEALS > 0 THEN 20 ELSE 0 END) +      -- Large deal presence
        (CASE WHEN TOTAL_QUALIFY_PLUS / NULLIF(BUDGET, 0) >= 4 THEN 10 ELSE 0 END)  -- Coverage multiplier
    , 5, 2) AS HEALTH_SCORE
FROM 
    pipeline_metrics
ORDER BY 
    HEALTH_SCORE DESC;
```

### 4. Weekly Track Performance

```sql
-- Track Performance vs 4x Target
WITH weekly_tracks AS (
    SELECT 
        p.GEOGRAPHY,
        p.MARKET,
        p.WEEK,
        SUM(p.QUALIFY_PLUS_AMT) AS QUALIFY_PLUS,
        SUM(b.REVENUE_BUDGET_AMT) AS BUDGET,
        -- Calculate 4x track for week 1
        SUM(b.REVENUE_BUDGET_AMT) * 4 AS WEEK1_TARGET,
        -- Linear track calculation
        CASE 
            WHEN p.WEEK = 1 THEN SUM(b.REVENUE_BUDGET_AMT) * 4
            WHEN p.WEEK < 1 THEN 
                -- For weeks before Q start, linear buildup to 4x
                SUM(b.REVENUE_BUDGET_AMT) * 4 * (13 + p.WEEK) / 13
            ELSE SUM(b.REVENUE_BUDGET_AMT) * 4  -- Maintain 4x after week 1
        END AS TRACK_TARGET
    FROM 
        PROD_MQT_CONSULTING_PIPELINE p
    LEFT JOIN 
        PROD_MQT_CONSULTING_BUDGET b
        ON p.GEOGRAPHY = b.GEOGRAPHY 
        AND p.MARKET = b.MARKET
        AND p.YEAR = b.YEAR
        AND p.QUARTER = b.QUARTER
    WHERE 
        p.SNAPSHOT_LEVEL = 'W'
        AND p.YEAR = YEAR(CURRENT DATE)
        AND p.QUARTER = QUARTER(CURRENT DATE)
    GROUP BY 
        p.GEOGRAPHY, p.MARKET, p.WEEK
)
SELECT 
    GEOGRAPHY,
    MARKET,
    WEEK,
    QUALIFY_PLUS,
    TRACK_TARGET,
    QUALIFY_PLUS - TRACK_TARGET AS TRACK_GAP,
    DECIMAL(QUALIFY_PLUS / NULLIF(TRACK_TARGET, 0) * 100, 5, 2) AS TRACK_ATTAINMENT_PCT,
    CASE 
        WHEN QUALIFY_PLUS >= TRACK_TARGET THEN 'On Track'
        WHEN QUALIFY_PLUS >= TRACK_TARGET * 0.9 THEN 'At Risk'
        ELSE 'Off Track'
    END AS TRACK_STATUS
FROM 
    weekly_tracks
WHERE 
    WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
ORDER BY 
    TRACK_ATTAINMENT_PCT DESC;
```

### 5. GenAI Pipeline Analysis

```sql
-- GenAI vs Traditional Pipeline Analysis
SELECT 
    p.GEOGRAPHY,
    p.MARKET,
    p.UT17_NAME,
    -- GenAI Pipeline
    SUM(CASE WHEN p.IBM_GEN_AI_IND = 1 THEN p.QUALIFY_PLUS_AMT ELSE 0 END) AS GENAI_PIPELINE,
    SUM(CASE WHEN p.PARTNER_GEN_AI_IND = 1 THEN p.QUALIFY_PLUS_AMT ELSE 0 END) AS PARTNER_GENAI_PIPELINE,
    -- Traditional Pipeline
    SUM(CASE WHEN p.IBM_GEN_AI_IND = 0 AND p.PARTNER_GEN_AI_IND = 0 THEN p.QUALIFY_PLUS_AMT ELSE 0 END) AS TRADITIONAL_PIPELINE,
    -- Total and Percentages
    SUM(p.QUALIFY_PLUS_AMT) AS TOTAL_PIPELINE,
    DECIMAL(
        SUM(CASE WHEN p.IBM_GEN_AI_IND = 1 OR p.PARTNER_GEN_AI_IND = 1 THEN p.QUALIFY_PLUS_AMT ELSE 0 END) / 
        NULLIF(SUM(p.QUALIFY_PLUS_AMT), 0) * 100
    , 5, 2) AS GENAI_PCT_OF_PIPELINE,
    -- Deal Counts
    COUNT(DISTINCT CASE WHEN p.IBM_GEN_AI_IND = 1 THEN p.CLIENT_NAME END) AS GENAI_CLIENT_COUNT
FROM 
    PROD_MQT_CONSULTING_PIPELINE p
WHERE 
    p.RELATIVE_QUARTER_MNEUMONIC = 'CQ'
    AND p.SNAPSHOT_LEVEL = 'W'
    AND p.WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
    AND p.SALES_STAGE NOT IN ('Won', 'Lost')
GROUP BY 
    p.GEOGRAPHY, p.MARKET, p.UT17_NAME
HAVING 
    SUM(p.QUALIFY_PLUS_AMT) > 0
ORDER BY 
    GENAI_PCT_OF_PIPELINE DESC;
```

## Performance Optimization Tips

### 1. Index Recommendations
```sql
-- Recommended indexes for optimal query performance
CREATE INDEX IX_MQT_PIPELINE_TIME ON PROD_MQT_CONSULTING_PIPELINE (YEAR, QUARTER, WEEK, RELATIVE_QUARTER_MNEUMONIC);
CREATE INDEX IX_MQT_PIPELINE_GEO ON PROD_MQT_CONSULTING_PIPELINE (GEOGRAPHY, MARKET, SECTOR);
CREATE INDEX IX_MQT_PIPELINE_UT ON PROD_MQT_CONSULTING_PIPELINE (UT15_NAME, UT17_NAME, UT20_NAME, UT30_NAME);
CREATE INDEX IX_MQT_PIPELINE_STAGE ON PROD_MQT_CONSULTING_PIPELINE (SALES_STAGE, SNAPSHOT_LEVEL);
```

### 2. Query Optimization Best Practices
- Always filter on `SNAPSHOT_LEVEL` and `RELATIVE_QUARTER_MNEUMONIC` first
- Use proper JOIN conditions on all dimension columns
- Leverage DB2's OLAP functions for complex calculations
- Consider creating summary tables for frequently accessed aggregations
- Use `FETCH FIRST n ROWS ONLY` for large result sets

### 3. Common Performance Patterns
```sql
-- Use CTEs for complex calculations
WITH base_metrics AS (
    -- Base query with filters
),
calculations AS (
    -- Derived calculations
)
SELECT * FROM calculations;

-- Use CASE expressions efficiently
SUM(CASE WHEN condition THEN value ELSE 0 END) 
-- Instead of multiple queries

-- Leverage DB2 analytical functions
RANK() OVER (PARTITION BY ... ORDER BY ...)
LAG/LEAD for time-based comparisons
```

## Notes
- All amounts are typically in millions (M) unless otherwise specified
- PY = Prior Year, PPY = Prior Prior Year
- CQ = Current Quarter, NQ = Next Quarter, PQ = Previous Quarter
- Always validate data freshness by checking MAX(WEEK) values
- Consider data latency when running real-time reports