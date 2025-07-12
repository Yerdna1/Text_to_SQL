# Comprehensive Sales Analytics Query Analysis
## All Business Domains: Consulting, Software, SaaS, Cloud, Service Management

### Table of Contents
1. [Pipeline Overview Queries](#pipeline-overview)
2. [Deal Progress & Status Queries](#deal-progress-status)
3. [Rep-Level Performance Queries](#rep-level-performance)
4. [Velocity & Efficiency Queries](#velocity-efficiency)
5. [Conversion & Funnel Analysis Queries](#conversion-funnel)
6. [Predictive & Prescriptive Insights Queries](#predictive-prescriptive)
7. [Activity & Follow-up Queries](#activity-followup)
8. [Real-Time Alerts Queries](#real-time-alerts)

---

## Pipeline Overview

### 1. "What is the total value of deals currently in the pipeline?"

#### **Deep Analysis:**
**Primary Table Choice:** MQT Pipeline tables (PROD_MQT_CONSULTING_PIPELINE, PROD_MQT_SOFTWARE_TRANSACTIONAL_PIPELINE, PROD_MQT_SW_SAAS_PIPELINE)

**Why MQT over Base Tables:**
- Pre-aggregated data for faster performance
- Consistent business logic already applied
- Week-over-week snapshots for trending
- Standardized measure definitions across domains

**Alternative Options:**
- Base tables (PROD_CONSULTING_PIPELINE) for real-time updates
- Opportunity tables for deal-level granularity
- Revenue forecast tables for forward-looking views

#### **Consulting Domain Query:**
```sql
-- CONSULTING: Current Pipeline Value
SELECT 
    'Consulting' AS BUSINESS_DOMAIN,
    p.GEOGRAPHY,
    p.MARKET,
    p.SECTOR,
    -- Multiple pipeline definitions for different use cases
    SUM(p.OPEN_PIPELINE_AMT) AS TOTAL_OPEN_PIPELINE,
    SUM(p.QUALIFY_PLUS_AMT) AS QUALIFY_PLUS_PIPELINE,
    SUM(p.PPV_AMT) AS PPV_PIPELINE,
    SUM(p.CALL_AMT) AS COMMITTED_PIPELINE,
    SUM(p.UPSIDE_AMT) AS UPSIDE_PIPELINE,
    -- Stage breakdown
    SUM(CASE WHEN p.SALES_STAGE = 'Qualify' THEN p.OPPORTUNITY_VALUE ELSE 0 END) AS QUALIFY_STAGE,
    SUM(CASE WHEN p.SALES_STAGE = 'Propose' THEN p.OPPORTUNITY_VALUE ELSE 0 END) AS PROPOSE_STAGE,
    SUM(CASE WHEN p.SALES_STAGE = 'Negotiate' THEN p.OPPORTUNITY_VALUE ELSE 0 END) AS NEGOTIATE_STAGE,
    SUM(CASE WHEN p.SALES_STAGE = 'Closing' THEN p.OPPORTUNITY_VALUE ELSE 0 END) AS CLOSING_STAGE,
    -- Counts
    COUNT(DISTINCT p.CLIENT_NAME) AS ACTIVE_CLIENTS,
    COUNT(*) AS OPPORTUNITY_COUNT
FROM 
    PROD_MQT_CONSULTING_PIPELINE p
WHERE 
    p.RELATIVE_QUARTER_MNEUMONIC = 'CQ'
    AND p.SNAPSHOT_LEVEL = 'W'
    AND p.WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
    AND p.SALES_STAGE NOT IN ('Won', 'Lost')
GROUP BY 
    p.GEOGRAPHY, p.MARKET, p.SECTOR
ORDER BY 
    TOTAL_OPEN_PIPELINE DESC;
```

**Why This SELECT Strategy:**
1. **Multiple Pipeline Metrics:** Different stakeholders need different views (OPEN_PIPELINE for total view, PPV for realistic assessment, CALL_AMT for committed pipeline)
2. **Stage Breakdown:** Enables funnel analysis and stage-specific insights
3. **Geographic Segmentation:** Critical for territory management and resource allocation
4. **Client Count:** Indicates pipeline concentration/diversification
5. **Current Quarter Filter:** Most relevant for active management

#### **Software Transactional Domain Query:**
```sql
-- SOFTWARE TRANSACTIONAL: Current Pipeline Value
SELECT 
    'Software Transactional' AS BUSINESS_DOMAIN,
    p.GEOGRAPHY,
    p.MARKET,
    p.BRAND,
    -- Software-specific pipeline measures
    SUM(p.LICENSE_PIPELINE_AMT) AS LICENSE_PIPELINE,
    SUM(p.MAINTENANCE_PIPELINE_AMT) AS MAINTENANCE_PIPELINE,
    SUM(p.TOTAL_CONTRACT_VALUE) AS TOTAL_CONTRACT_VALUE,
    SUM(p.ANNUAL_CONTRACT_VALUE) AS ANNUAL_CONTRACT_VALUE,
    -- Deal type breakdown
    SUM(CASE WHEN p.DEAL_TYPE = 'New' THEN p.OPPORTUNITY_VALUE ELSE 0 END) AS NEW_BUSINESS,
    SUM(CASE WHEN p.DEAL_TYPE = 'Renewal' THEN p.OPPORTUNITY_VALUE ELSE 0 END) AS RENEWAL_BUSINESS,
    SUM(CASE WHEN p.DEAL_TYPE = 'Expansion' THEN p.OPPORTUNITY_VALUE ELSE 0 END) AS EXPANSION_BUSINESS,
    -- Product mix
    SUM(CASE WHEN p.PRODUCT_FAMILY = 'Red Hat' THEN p.OPPORTUNITY_VALUE ELSE 0 END) AS REDHAT_PIPELINE,
    SUM(CASE WHEN p.PRODUCT_FAMILY = 'IBM Software' THEN p.OPPORTUNITY_VALUE ELSE 0 END) AS IBM_SOFTWARE_PIPELINE
FROM 
    PROD_MQT_SOFTWARE_TRANSACTIONAL_PIPELINE p
WHERE 
    p.RELATIVE_QUARTER_MNEUMONIC = 'CQ'
    AND p.SNAPSHOT_LEVEL = 'W'
    AND p.WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_SOFTWARE_TRANSACTIONAL_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
    AND p.SALES_STAGE NOT IN ('Won', 'Lost')
GROUP BY 
    p.GEOGRAPHY, p.MARKET, p.BRAND
ORDER BY 
    TOTAL_CONTRACT_VALUE DESC;
```

**Software Domain Differences:**
- **License vs Maintenance:** Critical distinction for software business model
- **TCV vs ACV:** Different value perspectives for subscription vs perpetual models
- **Deal Types:** New/Renewal/Expansion critical for growth analysis
- **Brand Segmentation:** Red Hat vs IBM Software have different dynamics

#### **SaaS Domain Query:**
```sql
-- SOFTWARE SAAS: Current Pipeline Value
SELECT 
    'SaaS' AS BUSINESS_DOMAIN,
    p.GEOGRAPHY,
    p.MARKET,
    -- SaaS-specific metrics
    SUM(p.ARR_PIPELINE_AMT) AS ARR_PIPELINE,
    SUM(p.MRR_PIPELINE_AMT) AS MRR_PIPELINE,
    SUM(p.EXPANSION_ARR_AMT) AS EXPANSION_ARR,
    SUM(p.CHURN_RISK_ARR_AMT) AS CHURN_RISK_ARR,
    -- Subscription metrics
    AVG(p.CONTRACT_LENGTH_MONTHS) AS AVG_CONTRACT_LENGTH,
    SUM(p.SEATS_COUNT) AS TOTAL_SEATS,
    AVG(p.PRICE_PER_SEAT) AS AVG_PRICE_PER_SEAT,
    -- Customer segments
    SUM(CASE WHEN p.CUSTOMER_SEGMENT = 'Enterprise' THEN p.ARR_PIPELINE_AMT ELSE 0 END) AS ENTERPRISE_ARR,
    SUM(CASE WHEN p.CUSTOMER_SEGMENT = 'Mid-Market' THEN p.ARR_PIPELINE_AMT ELSE 0 END) AS MIDMARKET_ARR,
    SUM(CASE WHEN p.CUSTOMER_SEGMENT = 'SMB' THEN p.ARR_PIPELINE_AMT ELSE 0 END) AS SMB_ARR
FROM 
    PROD_MQT_SW_SAAS_PIPELINE p
WHERE 
    p.RELATIVE_QUARTER_MNEUMONIC = 'CQ'
    AND p.SNAPSHOT_LEVEL = 'W'
    AND p.WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_SW_SAAS_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
    AND p.SALES_STAGE NOT IN ('Won', 'Lost')
GROUP BY 
    p.GEOGRAPHY, p.MARKET
ORDER BY 
    ARR_PIPELINE DESC;
```

**SaaS Domain Differences:**
- **ARR/MRR Focus:** Recurring revenue is the primary metric
- **Seat-Based Pricing:** Common SaaS model consideration
- **Churn Risk:** Critical for subscription business health
- **Customer Segmentation:** Different strategies by customer size

### 2. "Show me pipeline by region / industry / lead source / deal size"

#### **Deep Analysis:**
**Why Dimensional Analysis Approach:**
- Leverages star schema design for optimal performance
- Enables drill-down capabilities across hierarchies
- Supports dynamic filtering and grouping
- Consistent dimensional attributes across all domains

#### **Consulting Domain - Multi-Dimensional Pipeline View:**
```sql
-- CONSULTING: Pipeline by Multiple Dimensions
WITH pipeline_base AS (
    SELECT 
        p.GEOGRAPHY,
        p.MARKET,
        p.SECTOR,
        p.INDUSTRY,
        p.UT15_NAME,
        p.UT17_NAME,
        p.UT20_NAME,
        p.UT30_NAME,
        p.DEAL_SIZE,
        p.LEAD_SOURCE,
        p.CLIENT_NAME,
        p.SALES_STAGE,
        p.OPPORTUNITY_VALUE,
        p.QUALIFY_PLUS_AMT,
        p.PPV_AMT,
        -- Deal size categorization
        CASE 
            WHEN p.OPPORTUNITY_VALUE >= 10000000 THEN 'Mega (>$10M)'
            WHEN p.OPPORTUNITY_VALUE >= 5000000 THEN 'Large ($5M-$10M)'
            WHEN p.OPPORTUNITY_VALUE >= 1000000 THEN 'Medium ($1M-$5M)'
            ELSE 'Small (<$1M)'
        END AS DEAL_SIZE_CATEGORY,
        -- Lead source categorization  
        CASE 
            WHEN p.LEAD_SOURCE IN ('Inbound Marketing', 'Website', 'Content Marketing') THEN 'Digital Inbound'
            WHEN p.LEAD_SOURCE IN ('Partner Referral', 'Channel Partner') THEN 'Partner Channel'
            WHEN p.LEAD_SOURCE IN ('Sales Outreach', 'Cold Call', 'Sales Email') THEN 'Outbound Sales'
            WHEN p.LEAD_SOURCE IN ('Event', 'Trade Show', 'Conference') THEN 'Events'
            ELSE 'Other/Unknown'
        END AS LEAD_SOURCE_CATEGORY
    FROM 
        PROD_MQT_CONSULTING_PIPELINE p
    WHERE 
        p.RELATIVE_QUARTER_MNEUMONIC = 'CQ'
        AND p.SNAPSHOT_LEVEL = 'W'
        AND p.WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
        AND p.SALES_STAGE NOT IN ('Won', 'Lost')
)
-- Region Analysis
SELECT 
    'BY_REGION' AS ANALYSIS_TYPE,
    GEOGRAPHY AS DIMENSION_VALUE,
    MARKET AS SUB_DIMENSION,
    COUNT(*) AS OPPORTUNITY_COUNT,
    SUM(OPPORTUNITY_VALUE) AS TOTAL_PIPELINE,
    SUM(QUALIFY_PLUS_AMT) AS QUALIFY_PLUS_PIPELINE,
    AVG(OPPORTUNITY_VALUE) AS AVG_DEAL_SIZE,
    COUNT(DISTINCT CLIENT_NAME) AS UNIQUE_CLIENTS
FROM pipeline_base
GROUP BY GEOGRAPHY, MARKET

UNION ALL

-- Industry Analysis
SELECT 
    'BY_INDUSTRY' AS ANALYSIS_TYPE,
    INDUSTRY AS DIMENSION_VALUE,
    SECTOR AS SUB_DIMENSION,
    COUNT(*) AS OPPORTUNITY_COUNT,
    SUM(OPPORTUNITY_VALUE) AS TOTAL_PIPELINE,
    SUM(QUALIFY_PLUS_AMT) AS QUALIFY_PLUS_PIPELINE,
    AVG(OPPORTUNITY_VALUE) AS AVG_DEAL_SIZE,
    COUNT(DISTINCT CLIENT_NAME) AS UNIQUE_CLIENTS
FROM pipeline_base
GROUP BY INDUSTRY, SECTOR

UNION ALL

-- Lead Source Analysis
SELECT 
    'BY_LEAD_SOURCE' AS ANALYSIS_TYPE,
    LEAD_SOURCE_CATEGORY AS DIMENSION_VALUE,
    LEAD_SOURCE AS SUB_DIMENSION,
    COUNT(*) AS OPPORTUNITY_COUNT,
    SUM(OPPORTUNITY_VALUE) AS TOTAL_PIPELINE,
    SUM(QUALIFY_PLUS_AMT) AS QUALIFY_PLUS_PIPELINE,
    AVG(OPPORTUNITY_VALUE) AS AVG_DEAL_SIZE,
    COUNT(DISTINCT CLIENT_NAME) AS UNIQUE_CLIENTS
FROM pipeline_base
GROUP BY LEAD_SOURCE_CATEGORY, LEAD_SOURCE

UNION ALL

-- Deal Size Analysis
SELECT 
    'BY_DEAL_SIZE' AS ANALYSIS_TYPE,
    DEAL_SIZE_CATEGORY AS DIMENSION_VALUE,
    CAST(NULL AS VARCHAR(100)) AS SUB_DIMENSION,
    COUNT(*) AS OPPORTUNITY_COUNT,
    SUM(OPPORTUNITY_VALUE) AS TOTAL_PIPELINE,
    SUM(QUALIFY_PLUS_AMT) AS QUALIFY_PLUS_PIPELINE,
    AVG(OPPORTUNITY_VALUE) AS AVG_DEAL_SIZE,
    COUNT(DISTINCT CLIENT_NAME) AS UNIQUE_CLIENTS
FROM pipeline_base
GROUP BY DEAL_SIZE_CATEGORY

ORDER BY ANALYSIS_TYPE, TOTAL_PIPELINE DESC;
```

**Why This Complex UNION Approach:**
1. **Single Query Efficiency:** Returns all dimensional views in one result set
2. **Consistent Metrics:** Same calculations across all dimensions
3. **Flexible Categorization:** Business-relevant groupings beyond raw data
4. **Scalable Pattern:** Easy to add new dimensions

**Alternative Table Considerations:**
- **PROD_MQT_CONSULTING_OPPORTUNITY:** More granular deal-level details but slower aggregation
- **PROD_CONSULTING_PIPELINE:** Real-time data but requires custom business logic
- **PROD_MQT_CONSULTING_REVENUE_FORECAST:** Forward-looking view but less current state

### 3. "How many deals are in each sales stage?"

#### **Deep Analysis:**
**Table Choice Rationale:** MQT Pipeline tables provide consistent stage definitions and optimized aggregations.

**Critical Considerations:**
- Stage definitions may vary across business domains
- Stage progression rules differ (consulting vs software vs SaaS)
- Historical stage movement tracking requires time-series analysis

#### **Multi-Domain Stage Analysis:**
```sql
-- COMPREHENSIVE: Stage Analysis Across All Domains
WITH consulting_stages AS (
    SELECT 
        'Consulting' AS BUSINESS_DOMAIN,
        p.SALES_STAGE,
        COUNT(*) AS DEAL_COUNT,
        SUM(p.OPPORTUNITY_VALUE) AS STAGE_VALUE,
        AVG(p.OPPORTUNITY_VALUE) AS AVG_DEAL_SIZE,
        -- Stage groupings for funnel analysis
        CASE 
            WHEN p.SALES_STAGE IN ('Qualify', 'Design') THEN 'Early Stage'
            WHEN p.SALES_STAGE IN ('Propose', 'Negotiate') THEN 'Mid Stage'
            WHEN p.SALES_STAGE = 'Closing' THEN 'Late Stage'
            ELSE 'Other'
        END AS STAGE_GROUP,
        -- Stage velocity indicators
        AVG(p.DAYS_IN_STAGE) AS AVG_DAYS_IN_STAGE,
        COUNT(CASE WHEN p.DAYS_IN_STAGE > 60 THEN 1 END) AS STALLED_DEALS
    FROM 
        PROD_MQT_CONSULTING_PIPELINE p
    WHERE 
        p.RELATIVE_QUARTER_MNEUMONIC = 'CQ'
        AND p.SNAPSHOT_LEVEL = 'W'
        AND p.WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
        AND p.SALES_STAGE NOT IN ('Won', 'Lost')
    GROUP BY p.SALES_STAGE
),
software_stages AS (
    SELECT 
        'Software Transactional' AS BUSINESS_DOMAIN,
        p.SALES_STAGE,
        COUNT(*) AS DEAL_COUNT,
        SUM(p.TOTAL_CONTRACT_VALUE) AS STAGE_VALUE,
        AVG(p.TOTAL_CONTRACT_VALUE) AS AVG_DEAL_SIZE,
        -- Software-specific stage groupings
        CASE 
            WHEN p.SALES_STAGE IN ('Lead', 'Qualified') THEN 'Early Stage'
            WHEN p.SALES_STAGE IN ('Proposal', 'Negotiation') THEN 'Mid Stage'
            WHEN p.SALES_STAGE IN ('Verbal Commit', 'Contracting') THEN 'Late Stage'
            ELSE 'Other'
        END AS STAGE_GROUP,
        AVG(p.DAYS_IN_STAGE) AS AVG_DAYS_IN_STAGE,
        COUNT(CASE WHEN p.DAYS_IN_STAGE > 90 THEN 1 END) AS STALLED_DEALS
    FROM 
        PROD_MQT_SOFTWARE_TRANSACTIONAL_PIPELINE p
    WHERE 
        p.RELATIVE_QUARTER_MNEUMONIC = 'CQ'
        AND p.SNAPSHOT_LEVEL = 'W'
        AND p.WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_SOFTWARE_TRANSACTIONAL_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
        AND p.SALES_STAGE NOT IN ('Won', 'Lost')
    GROUP BY p.SALES_STAGE
),
saas_stages AS (
    SELECT 
        'SaaS' AS BUSINESS_DOMAIN,
        p.SALES_STAGE,
        COUNT(*) AS DEAL_COUNT,
        SUM(p.ARR_PIPELINE_AMT) AS STAGE_VALUE,
        AVG(p.ARR_PIPELINE_AMT) AS AVG_DEAL_SIZE,
        -- SaaS-specific stage groupings (typically faster cycle)
        CASE 
            WHEN p.SALES_STAGE IN ('Lead', 'Demo Scheduled') THEN 'Early Stage'
            WHEN p.SALES_STAGE IN ('Trial', 'Proposal') THEN 'Mid Stage'
            WHEN p.SALES_STAGE IN ('Contract Review', 'Closing') THEN 'Late Stage'
            ELSE 'Other'
        END AS STAGE_GROUP,
        AVG(p.DAYS_IN_STAGE) AS AVG_DAYS_IN_STAGE,
        COUNT(CASE WHEN p.DAYS_IN_STAGE > 30 THEN 1 END) AS STALLED_DEALS
    FROM 
        PROD_MQT_SW_SAAS_PIPELINE p
    WHERE 
        p.RELATIVE_QUARTER_MNEUMONIC = 'CQ'
        AND p.SNAPSHOT_LEVEL = 'W'
        AND p.WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_SW_SAAS_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
        AND p.SALES_STAGE NOT IN ('Won', 'Lost')
    GROUP BY p.SALES_STAGE
)
-- Combine all domains
SELECT * FROM consulting_stages
UNION ALL
SELECT * FROM software_stages  
UNION ALL
SELECT * FROM saas_stages
ORDER BY BUSINESS_DOMAIN, STAGE_VALUE DESC;
```

**Why Domain-Specific CTEs:**
1. **Different Stage Definitions:** Each business has unique sales processes
2. **Different Value Metrics:** Consulting uses OPPORTUNITY_VALUE, Software uses TCV, SaaS uses ARR
3. **Different Cycle Times:** SaaS cycles are typically shorter, requiring different stall thresholds
4. **Specialized Analytics:** Each domain needs specific insights (e.g., ARR for SaaS)

### 4. "What's the average deal size this quarter?"

#### **Deep Analysis:**
**Calculation Complexity:** "Average" can mean different things:
- Simple average (sum/count)
- Weighted average by probability
- Median to avoid outlier skew
- Average by stage/geography/product

**Table Choice:** MQT tables for consistent deal size calculations across time periods.

#### **Comprehensive Deal Size Analysis:**
```sql
-- MULTI-DOMAIN: Average Deal Size Analysis
WITH deal_size_metrics AS (
    SELECT 
        'Consulting' AS BUSINESS_DOMAIN,
        p.GEOGRAPHY,
        p.MARKET,
        p.QUARTER,
        p.YEAR,
        -- Multiple average calculations
        AVG(p.OPPORTUNITY_VALUE) AS SIMPLE_AVERAGE,
        MEDIAN(p.OPPORTUNITY_VALUE) AS MEDIAN_DEAL_SIZE,
        -- Weighted average by stage probability
        SUM(p.OPPORTUNITY_VALUE * 
            CASE p.SALES_STAGE
                WHEN 'Qualify' THEN 0.10
                WHEN 'Design' THEN 0.25
                WHEN 'Propose' THEN 0.50
                WHEN 'Negotiate' THEN 0.75
                WHEN 'Closing' THEN 0.90
                ELSE 0.05
            END
        ) / COUNT(*) AS PROBABILITY_WEIGHTED_AVG,
        -- Deal size distribution
        COUNT(CASE WHEN p.OPPORTUNITY_VALUE >= 10000000 THEN 1 END) AS MEGA_DEALS,
        COUNT(CASE WHEN p.OPPORTUNITY_VALUE BETWEEN 5000000 AND 9999999 THEN 1 END) AS LARGE_DEALS,
        COUNT(CASE WHEN p.OPPORTUNITY_VALUE BETWEEN 1000000 AND 4999999 THEN 1 END) AS MEDIUM_DEALS,
        COUNT(CASE WHEN p.OPPORTUNITY_VALUE < 1000000 THEN 1 END) AS SMALL_DEALS,
        COUNT(*) AS TOTAL_DEALS,
        -- Comparison metrics
        AVG(p.OPPORTUNITY_VALUE_PY) AS SIMPLE_AVERAGE_PY,
        STDDEV(p.OPPORTUNITY_VALUE) AS DEAL_SIZE_STDDEV
    FROM 
        PROD_MQT_CONSULTING_PIPELINE p
    WHERE 
        p.RELATIVE_QUARTER_MNEUMONIC = 'CQ'
        AND p.SNAPSHOT_LEVEL = 'W'
        AND p.WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
        AND p.SALES_STAGE NOT IN ('Won', 'Lost')
    GROUP BY p.GEOGRAPHY, p.MARKET, p.QUARTER, p.YEAR
    
    UNION ALL
    
    SELECT 
        'Software Transactional' AS BUSINESS_DOMAIN,
        p.GEOGRAPHY,
        p.MARKET,
        p.QUARTER,
        p.YEAR,
        AVG(p.TOTAL_CONTRACT_VALUE) AS SIMPLE_AVERAGE,
        MEDIAN(p.TOTAL_CONTRACT_VALUE) AS MEDIAN_DEAL_SIZE,
        -- Software-specific probability weighting
        SUM(p.TOTAL_CONTRACT_VALUE * 
            CASE p.SALES_STAGE
                WHEN 'Lead' THEN 0.05
                WHEN 'Qualified' THEN 0.15
                WHEN 'Proposal' THEN 0.40
                WHEN 'Negotiation' THEN 0.70
                WHEN 'Verbal Commit' THEN 0.85
                WHEN 'Contracting' THEN 0.95
                ELSE 0.05
            END
        ) / COUNT(*) AS PROBABILITY_WEIGHTED_AVG,
        COUNT(CASE WHEN p.TOTAL_CONTRACT_VALUE >= 5000000 THEN 1 END) AS MEGA_DEALS,
        COUNT(CASE WHEN p.TOTAL_CONTRACT_VALUE BETWEEN 1000000 AND 4999999 THEN 1 END) AS LARGE_DEALS,
        COUNT(CASE WHEN p.TOTAL_CONTRACT_VALUE BETWEEN 250000 AND 999999 THEN 1 END) AS MEDIUM_DEALS,
        COUNT(CASE WHEN p.TOTAL_CONTRACT_VALUE < 250000 THEN 1 END) AS SMALL_DEALS,
        COUNT(*) AS TOTAL_DEALS,
        AVG(p.TOTAL_CONTRACT_VALUE_PY) AS SIMPLE_AVERAGE_PY,
        STDDEV(p.TOTAL_CONTRACT_VALUE) AS DEAL_SIZE_STDDEV
    FROM 
        PROD_MQT_SOFTWARE_TRANSACTIONAL_PIPELINE p
    WHERE 
        p.RELATIVE_QUARTER_MNEUMONIC = 'CQ'
        AND p.SNAPSHOT_LEVEL = 'W'
        AND p.WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_SOFTWARE_TRANSACTIONAL_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
        AND p.SALES_STAGE NOT IN ('Won', 'Lost')
    GROUP BY p.GEOGRAPHY, p.MARKET, p.QUARTER, p.YEAR
    
    UNION ALL
    
    SELECT 
        'SaaS' AS BUSINESS_DOMAIN,
        p.GEOGRAPHY,
        p.MARKET,
        p.QUARTER,
        p.YEAR,
        AVG(p.ARR_PIPELINE_AMT) AS SIMPLE_AVERAGE,
        MEDIAN(p.ARR_PIPELINE_AMT) AS MEDIAN_DEAL_SIZE,
        -- SaaS typically has higher probability progression
        SUM(p.ARR_PIPELINE_AMT * 
            CASE p.SALES_STAGE
                WHEN 'Lead' THEN 0.08
                WHEN 'Demo Scheduled' THEN 0.20
                WHEN 'Trial' THEN 0.45
                WHEN 'Proposal' THEN 0.65
                WHEN 'Contract Review' THEN 0.85
                WHEN 'Closing' THEN 0.95
                ELSE 0.05
            END
        ) / COUNT(*) AS PROBABILITY_WEIGHTED_AVG,
        COUNT(CASE WHEN p.ARR_PIPELINE_AMT >= 1000000 THEN 1 END) AS MEGA_DEALS,
        COUNT(CASE WHEN p.ARR_PIPELINE_AMT BETWEEN 250000 AND 999999 THEN 1 END) AS LARGE_DEALS,
        COUNT(CASE WHEN p.ARR_PIPELINE_AMT BETWEEN 50000 AND 249999 THEN 1 END) AS MEDIUM_DEALS,
        COUNT(CASE WHEN p.ARR_PIPELINE_AMT < 50000 THEN 1 END) AS SMALL_DEALS,
        COUNT(*) AS TOTAL_DEALS,
        AVG(p.ARR_PIPELINE_AMT_PY) AS SIMPLE_AVERAGE_PY,
        STDDEV(p.ARR_PIPELINE_AMT) AS DEAL_SIZE_STDDEV
    FROM 
        PROD_MQT_SW_SAAS_PIPELINE p
    WHERE 
        p.RELATIVE_QUARTER_MNEUMONIC = 'CQ'
        AND p.SNAPSHOT_LEVEL = 'W'
        AND p.WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_SW_SAAS_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
        AND p.SALES_STAGE NOT IN ('Won', 'Lost')
    GROUP BY p.GEOGRAPHY, p.MARKET, p.QUARTER, p.YEAR
)
SELECT 
    BUSINESS_DOMAIN,
    GEOGRAPHY,
    MARKET,
    SIMPLE_AVERAGE,
    MEDIAN_DEAL_SIZE,
    PROBABILITY_WEIGHTED_AVG,
    -- Deal mix percentages
    DECIMAL(MEGA_DEALS * 100.0 / TOTAL_DEALS, 5, 2) AS MEGA_DEAL_PCT,
    DECIMAL(LARGE_DEALS * 100.0 / TOTAL_DEALS, 5, 2) AS LARGE_DEAL_PCT,
    DECIMAL(MEDIUM_DEALS * 100.0 / TOTAL_DEALS, 5, 2) AS MEDIUM_DEAL_PCT,
    DECIMAL(SMALL_DEALS * 100.0 / TOTAL_DEALS, 5, 2) AS SMALL_DEAL_PCT,
    -- Year over year comparison
    CASE 
        WHEN SIMPLE_AVERAGE_PY > 0 
        THEN DECIMAL((SIMPLE_AVERAGE - SIMPLE_AVERAGE_PY) / SIMPLE_AVERAGE_PY * 100, 5, 2)
        ELSE NULL 
    END AS YOY_DEAL_SIZE_CHANGE_PCT,
    -- Statistical insights
    DECIMAL(DEAL_SIZE_STDDEV / SIMPLE_AVERAGE, 5, 2) AS COEFFICIENT_OF_VARIATION
FROM deal_size_metrics
ORDER BY BUSINESS_DOMAIN, GEOGRAPHY, SIMPLE_AVERAGE DESC;
```

**Advanced Analytical Approaches:**
1. **Probability-Weighted Average:** More realistic view of expected value
2. **Median vs Mean:** Handles outlier deals better
3. **Deal Size Distribution:** Shows portfolio balance
4. **Coefficient of Variation:** Indicates deal size consistency
5. **YoY Comparison:** Trend analysis for deal sizing

### 5. "What is the win rate across the team?"

#### **Deep Analysis:**
**Table Choice Complexity:** Win rate calculation requires both won deals and total closed deals (won + lost). This requires careful handling of:
- Historical data for accurate win rates
- Deal lifecycle completion
- Attribution to teams/territories
- Time period normalization

**Primary Tables:** MQT Pipeline for current state, potentially Revenue Actuals for historical wins

#### **Multi-Domain Win Rate Analysis:**
```sql
-- COMPREHENSIVE: Win Rate Analysis Across All Domains
WITH win_rate_calculations AS (
    -- Consulting Win Rates
    SELECT 
        'Consulting' AS BUSINESS_DOMAIN,
        p.GEOGRAPHY,
        p.MARKET,
        p.SECTOR,
        p.YEAR,
        p.QUARTER,
        -- Current period metrics
        SUM(p.WON_AMT) AS WON_REVENUE,
        SUM(CASE WHEN p.SALES_STAGE = 'Won' THEN p.OPPORTUNITY_VALUE ELSE 0 END) AS WON_OPPORTUNITY_VALUE,
        SUM(CASE WHEN p.SALES_STAGE = 'Lost' THEN p.OPPORTUNITY_VALUE ELSE 0 END) AS LOST_OPPORTUNITY_VALUE,
        COUNT(CASE WHEN p.SALES_STAGE = 'Won' THEN 1 END) AS DEALS_WON,
        COUNT(CASE WHEN p.SALES_STAGE = 'Lost' THEN 1 END) AS DEALS_LOST,
        COUNT(CASE WHEN p.SALES_STAGE IN ('Won', 'Lost') THEN 1 END) AS TOTAL_CLOSED_DEALS,
        -- Prior year comparison
        SUM(p.WON_AMT_PY) AS WON_REVENUE_PY,
        COUNT(CASE WHEN p.SALES_STAGE_PY = 'Won' THEN 1 END) AS DEALS_WON_PY,
        COUNT(CASE WHEN p.SALES_STAGE_PY IN ('Won', 'Lost') THEN 1 END) AS TOTAL_CLOSED_DEALS_PY,
        -- Team composition
        COUNT(DISTINCT p.SALES_REP_NAME) AS UNIQUE_REPS,
        COUNT(DISTINCT p.CLIENT_NAME) AS UNIQUE_CLIENTS
    FROM 
        PROD_MQT_CONSULTING_PIPELINE p
    WHERE 
        p.RELATIVE_QUARTER_MNEUMONIC IN ('CQ', 'PQ')  -- Current and previous quarters for trend
        AND p.SNAPSHOT_LEVEL = 'W'
        AND p.WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
    GROUP BY p.GEOGRAPHY, p.MARKET, p.SECTOR, p.YEAR, p.QUARTER
    
    UNION ALL
    
    -- Software Transactional Win Rates
    SELECT 
        'Software Transactional' AS BUSINESS_DOMAIN,
        p.GEOGRAPHY,
        p.MARKET,
        p.BRAND AS SECTOR,
        p.YEAR,
        p.QUARTER,
        SUM(CASE WHEN p.SALES_STAGE = 'Won' THEN p.TOTAL_CONTRACT_VALUE ELSE 0 END) AS WON_REVENUE,
        SUM(CASE WHEN p.SALES_STAGE = 'Won' THEN p.TOTAL_CONTRACT_VALUE ELSE 0 END) AS WON_OPPORTUNITY_VALUE,
        SUM(CASE WHEN p.SALES_STAGE = 'Lost' THEN p.TOTAL_CONTRACT_VALUE ELSE 0 END) AS LOST_OPPORTUNITY_VALUE,
        COUNT(CASE WHEN p.SALES_STAGE = 'Won' THEN 1 END) AS DEALS_WON,
        COUNT(CASE WHEN p.SALES_STAGE = 'Lost' THEN 1 END) AS DEALS_LOST,
        COUNT(CASE WHEN p.SALES_STAGE IN ('Won', 'Lost') THEN 1 END) AS TOTAL_CLOSED_DEALS,
        SUM(CASE WHEN p.SALES_STAGE_PY = 'Won' THEN p.TOTAL_CONTRACT_VALUE_PY ELSE 0 END) AS WON_REVENUE_PY,
        COUNT(CASE WHEN p.SALES_STAGE_PY = 'Won' THEN 1 END) AS DEALS_WON_PY,
        COUNT(CASE WHEN p.SALES_STAGE_PY IN ('Won', 'Lost') THEN 1 END) AS TOTAL_CLOSED_DEALS_PY,
        COUNT(DISTINCT p.SALES_REP_NAME) AS UNIQUE_REPS,
        COUNT(DISTINCT p.CLIENT_NAME) AS UNIQUE_CLIENTS
    FROM 
        PROD_MQT_SOFTWARE_TRANSACTIONAL_PIPELINE p
    WHERE 
        p.RELATIVE_QUARTER_MNEUMONIC IN ('CQ', 'PQ')
        AND p.SNAPSHOT_LEVEL = 'W'
        AND p.WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_SOFTWARE_TRANSACTIONAL_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
    GROUP BY p.GEOGRAPHY, p.MARKET, p.BRAND, p.YEAR, p.QUARTER
    
    UNION ALL
    
    -- SaaS Win Rates
    SELECT 
        'SaaS' AS BUSINESS_DOMAIN,
        p.GEOGRAPHY,
        p.MARKET,
        p.CUSTOMER_SEGMENT AS SECTOR,
        p.YEAR,
        p.QUARTER,
        SUM(CASE WHEN p.SALES_STAGE = 'Won' THEN p.ARR_PIPELINE_AMT ELSE 0 END) AS WON_REVENUE,
        SUM(CASE WHEN p.SALES_STAGE = 'Won' THEN p.ARR_PIPELINE_AMT ELSE 0 END) AS WON_OPPORTUNITY_VALUE,
        SUM(CASE WHEN p.SALES_STAGE = 'Lost' THEN p.ARR_PIPELINE_AMT ELSE 0 END) AS LOST_OPPORTUNITY_VALUE,
        COUNT(CASE WHEN p.SALES_STAGE = 'Won' THEN 1 END) AS DEALS_WON,
        COUNT(CASE WHEN p.SALES_STAGE = 'Lost' THEN 1 END) AS DEALS_LOST,
        COUNT(CASE WHEN p.SALES_STAGE IN ('Won', 'Lost') THEN 1 END) AS TOTAL_CLOSED_DEALS,
        SUM(CASE WHEN p.SALES_STAGE_PY = 'Won' THEN p.ARR_PIPELINE_AMT_PY ELSE 0 END) AS WON_REVENUE_PY,
        COUNT(CASE WHEN p.SALES_STAGE_PY = 'Won' THEN 1 END) AS DEALS_WON_PY,
        COUNT(CASE WHEN p.SALES_STAGE_PY IN ('Won', 'Lost') THEN 1 END) AS TOTAL_CLOSED_DEALS_PY,
        COUNT(DISTINCT p.SALES_REP_NAME) AS UNIQUE_REPS,
        COUNT(DISTINCT p.CLIENT_NAME) AS UNIQUE_CLIENTS
    FROM 
        PROD_MQT_SW_SAAS_PIPELINE p
    WHERE 
        p.RELATIVE_QUARTER_MNEUMONIC IN ('CQ', 'PQ')
        AND p.SNAPSHOT_LEVEL = 'W'
        AND p.WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_SW_SAAS_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
    GROUP BY p.GEOGRAPHY, p.MARKET, p.CUSTOMER_SEGMENT, p.YEAR, p.QUARTER
)
SELECT 
    BUSINESS_DOMAIN,
    GEOGRAPHY,
    MARKET,
    SECTOR,
    UNIQUE_REPS AS TEAM_SIZE,
    -- Win Rate by Count
    CASE 
        WHEN TOTAL_CLOSED_DEALS > 0 
        THEN DECIMAL(DEALS_WON * 100.0 / TOTAL_CLOSED_DEALS, 5, 2)
        ELSE 0 
    END AS WIN_RATE_BY_COUNT_PCT,
    -- Win Rate by Value
    CASE 
        WHEN (WON_OPPORTUNITY_VALUE + LOST_OPPORTUNITY_VALUE) > 0 
        THEN DECIMAL(WON_OPPORTUNITY_VALUE * 100.0 / (WON_OPPORTUNITY_VALUE + LOST_OPPORTUNITY_VALUE), 5, 2)
        ELSE 0 
    END AS WIN_RATE_BY_VALUE_PCT,
    -- Prior Year Comparison
    CASE 
        WHEN TOTAL_CLOSED_DEALS_PY > 0 
        THEN DECIMAL(DEALS_WON_PY * 100.0 / TOTAL_CLOSED_DEALS_PY, 5, 2)
        ELSE 0 
    END AS WIN_RATE_BY_COUNT_PCT_PY,
    -- Performance metrics
    DECIMAL(WON_REVENUE / NULLIF(UNIQUE_REPS, 0), 10, 2) AS REVENUE_PER_REP,
    DECIMAL(DEALS_WON * 1.0 / NULLIF(UNIQUE_REPS, 0), 5, 2) AS WINS_PER_REP,
    DECIMAL(WON_OPPORTUNITY_VALUE / NULLIF(DEALS_WON, 0), 10, 2) AS AVG_WIN_SIZE,
    -- Deal metrics
    DEALS_WON,
    DEALS_LOST,
    TOTAL_CLOSED_DEALS,
    WON_REVENUE,
    UNIQUE_CLIENTS AS CLIENTS_WON
FROM win_rate_calculations
WHERE TOTAL_CLOSED_DEALS > 0  -- Only show teams with closed deals
ORDER BY BUSINESS_DOMAIN, WIN_RATE_BY_VALUE_PCT DESC;
```

**Why This Comprehensive Approach:**
1. **Multiple Win Rate Definitions:** Count-based vs value-based provide different insights
2. **Team Performance Context:** Revenue per rep and wins per rep show team efficiency
3. **Historical Comparison:** PY comparison shows trend direction
4. **Domain-Specific Metrics:** Each business uses appropriate value measure (Revenue/TCV/ARR)

**Alternative Table Considerations:**
- **Revenue Actuals Tables:** More definitive for historical wins but may lag pipeline updates
- **Opportunity Tables:** More granular but requires complex aggregation
- **Signings Actuals Tables:** Contract-based wins vs revenue recognition timing

### 6. "What's the forecasted revenue this month/quarter/year?"

#### **Deep Analysis:**
**Table Choice Strategy:** Revenue forecast tables are purpose-built for forward-looking projections, while pipeline tables show current state. The choice depends on forecast methodology:

**Primary Tables:** 
- `PROD_MQT_CONSULTING_REVENUE_FORECAST` - Dedicated forecast models
- `PROD_MQT_CONSULTING_PIPELINE` - Pipeline-driven forecasts using PPV_AMT
- `PROD_MQT_CONSULTING_BUDGET` - Target comparison

#### **Multi-Domain Revenue Forecasting:**
```sql
-- COMPREHENSIVE: Revenue Forecasting Across All Domains
WITH forecast_data AS (
    -- Consulting Revenue Forecast
    SELECT 
        'Consulting' AS BUSINESS_DOMAIN,
        f.GEOGRAPHY,
        f.MARKET,
        f.YEAR,
        f.QUARTER,
        f.MONTH,
        -- Forecast Methods
        SUM(f.STATISTICAL_FORECAST_AMT) AS STATISTICAL_FORECAST,
        SUM(f.PIPELINE_BASED_FORECAST_AMT) AS PIPELINE_FORECAST,
        SUM(f.MANAGEMENT_FORECAST_AMT) AS MANAGEMENT_FORECAST,
        SUM(f.CONSENSUS_FORECAST_AMT) AS CONSENSUS_FORECAST,
        -- Confidence intervals
        SUM(f.FORECAST_LOW_AMT) AS FORECAST_LOW,
        SUM(f.FORECAST_HIGH_AMT) AS FORECAST_HIGH,
        -- Forecast components
        SUM(f.BASE_BUSINESS_FORECAST_AMT) AS BASE_BUSINESS,
        SUM(f.NEW_BUSINESS_FORECAST_AMT) AS NEW_BUSINESS,
        SUM(f.RENEWAL_FORECAST_AMT) AS RENEWAL_BUSINESS,
        -- Historical accuracy
        AVG(f.FORECAST_ACCURACY_PCT) AS AVG_FORECAST_ACCURACY,
        COUNT(*) AS FORECAST_RECORDS
    FROM 
        PROD_MQT_CONSULTING_REVENUE_FORECAST f
    WHERE 
        f.FORECAST_DATE = (SELECT MAX(FORECAST_DATE) FROM PROD_MQT_CONSULTING_REVENUE_FORECAST)
        AND f.FORECAST_PERIOD_TYPE IN ('Month', 'Quarter', 'Year')
    GROUP BY f.GEOGRAPHY, f.MARKET, f.YEAR, f.QUARTER, f.MONTH
    
    UNION ALL
    
    -- Software Transactional Revenue Forecast  
    SELECT 
        'Software Transactional' AS BUSINESS_DOMAIN,
        f.GEOGRAPHY,
        f.MARKET,
        f.YEAR,
        f.QUARTER,
        f.MONTH,
        SUM(f.LICENSE_FORECAST_AMT) AS STATISTICAL_FORECAST,
        SUM(f.MAINTENANCE_FORECAST_AMT) AS PIPELINE_FORECAST,
        SUM(f.TOTAL_FORECAST_AMT) AS MANAGEMENT_FORECAST,
        SUM(f.WEIGHTED_PIPELINE_FORECAST_AMT) AS CONSENSUS_FORECAST,
        SUM(f.CONSERVATIVE_FORECAST_AMT) AS FORECAST_LOW,
        SUM(f.OPTIMISTIC_FORECAST_AMT) AS FORECAST_HIGH,
        SUM(f.EXISTING_CUSTOMER_FORECAST_AMT) AS BASE_BUSINESS,
        SUM(f.NEW_CUSTOMER_FORECAST_AMT) AS NEW_BUSINESS,
        SUM(f.RENEWAL_FORECAST_AMT) AS RENEWAL_BUSINESS,
        AVG(f.FORECAST_ACCURACY_PCT) AS AVG_FORECAST_ACCURACY,
        COUNT(*) AS FORECAST_RECORDS
    FROM 
        PROD_MQT_SOFTWARE_TRANSACTIONAL_REVENUE_FORECAST f
    WHERE 
        f.FORECAST_DATE = (SELECT MAX(FORECAST_DATE) FROM PROD_MQT_SOFTWARE_TRANSACTIONAL_REVENUE_FORECAST)
        AND f.FORECAST_PERIOD_TYPE IN ('Month', 'Quarter', 'Year')
    GROUP BY f.GEOGRAPHY, f.MARKET, f.YEAR, f.QUARTER, f.MONTH
    
    UNION ALL
    
    -- SaaS Revenue Forecast (typically more predictable)
    SELECT 
        'SaaS' AS BUSINESS_DOMAIN,
        f.GEOGRAPHY,
        f.MARKET,
        f.YEAR,
        f.QUARTER,
        f.MONTH,
        SUM(f.ARR_FORECAST_AMT) AS STATISTICAL_FORECAST,
        SUM(f.MRR_FORECAST_AMT * 12) AS PIPELINE_FORECAST,  -- Annualized MRR
        SUM(f.MANAGEMENT_ARR_FORECAST_AMT) AS MANAGEMENT_FORECAST,
        SUM(f.WEIGHTED_ARR_FORECAST_AMT) AS CONSENSUS_FORECAST,
        SUM(f.CONSERVATIVE_ARR_FORECAST_AMT) AS FORECAST_LOW,
        SUM(f.STRETCH_ARR_FORECAST_AMT) AS FORECAST_HIGH,
        SUM(f.EXISTING_ARR_FORECAST_AMT) AS BASE_BUSINESS,
        SUM(f.NEW_ARR_FORECAST_AMT) AS NEW_BUSINESS,
        SUM(f.RENEWAL_ARR_FORECAST_AMT) AS RENEWAL_BUSINESS,
        AVG(f.FORECAST_ACCURACY_PCT) AS AVG_FORECAST_ACCURACY,
        COUNT(*) AS FORECAST_RECORDS
    FROM 
        PROD_MQT_SW_SAAS_REVENUE_FORECAST f
    WHERE 
        f.FORECAST_DATE = (SELECT MAX(FORECAST_DATE) FROM PROD_MQT_SW_SAAS_REVENUE_FORECAST)
        AND f.FORECAST_PERIOD_TYPE IN ('Month', 'Quarter', 'Year')
    GROUP BY f.GEOGRAPHY, f.MARKET, f.YEAR, f.QUARTER, f.MONTH
),
-- Pipeline-based forecasts as alternative/validation
pipeline_forecasts AS (
    SELECT 
        'Consulting' AS BUSINESS_DOMAIN,
        p.GEOGRAPHY,
        p.MARKET,
        p.YEAR,
        p.QUARTER,
        CAST(NULL AS INTEGER) AS MONTH,
        -- Pipeline-driven forecast using PPV
        SUM(p.PPV_AMT) AS PPV_FORECAST,
        -- Stage-based probability forecast
        SUM(p.OPPORTUNITY_VALUE * 
            CASE p.SALES_STAGE
                WHEN 'Qualify' THEN 0.10
                WHEN 'Design' THEN 0.25
                WHEN 'Propose' THEN 0.50
                WHEN 'Negotiate' THEN 0.75
                WHEN 'Closing' THEN 0.90
                ELSE 0.05
            END
        ) AS STAGE_PROBABILITY_FORECAST,
        -- Committed pipeline
        SUM(p.CALL_AMT) AS COMMITTED_FORECAST
    FROM 
        PROD_MQT_CONSULTING_PIPELINE p
    WHERE 
        p.RELATIVE_QUARTER_MNEUMONIC = 'CQ'
        AND p.SNAPSHOT_LEVEL = 'W'
        AND p.WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
        AND p.SALES_STAGE NOT IN ('Won', 'Lost')
    GROUP BY p.GEOGRAPHY, p.MARKET, p.YEAR, p.QUARTER
)
-- Combine forecast methods with budget comparison
SELECT 
    f.BUSINESS_DOMAIN,
    f.GEOGRAPHY,
    f.MARKET,
    f.YEAR,
    f.QUARTER,
    f.MONTH,
    -- Multiple forecast scenarios
    f.STATISTICAL_FORECAST,
    f.PIPELINE_FORECAST,
    f.MANAGEMENT_FORECAST,
    f.CONSENSUS_FORECAST,
    -- Confidence bands
    f.FORECAST_LOW,
    f.FORECAST_HIGH,
    f.FORECAST_HIGH - f.FORECAST_LOW AS FORECAST_RANGE,
    -- Business composition
    f.BASE_BUSINESS,
    f.NEW_BUSINESS,
    f.RENEWAL_BUSINESS,
    DECIMAL(f.NEW_BUSINESS * 100.0 / NULLIF(f.CONSENSUS_FORECAST, 0), 5, 2) AS NEW_BUSINESS_PCT,
    -- Forecast reliability
    f.AVG_FORECAST_ACCURACY,
    CASE 
        WHEN f.AVG_FORECAST_ACCURACY >= 90 THEN 'High Confidence'
        WHEN f.AVG_FORECAST_ACCURACY >= 75 THEN 'Medium Confidence'
        ELSE 'Low Confidence'
    END AS CONFIDENCE_LEVEL,
    -- Pipeline validation (where available)
    pf.PPV_FORECAST AS PIPELINE_PPV_FORECAST,
    pf.STAGE_PROBABILITY_FORECAST,
    pf.COMMITTED_FORECAST,
    -- Variance analysis
    CASE 
        WHEN pf.PPV_FORECAST > 0 
        THEN DECIMAL((f.CONSENSUS_FORECAST - pf.PPV_FORECAST) * 100.0 / pf.PPV_FORECAST, 5, 2)
        ELSE NULL 
    END AS FORECAST_VS_PPV_VARIANCE_PCT
FROM forecast_data f
LEFT JOIN pipeline_forecasts pf 
    ON f.BUSINESS_DOMAIN = pf.BUSINESS_DOMAIN
    AND f.GEOGRAPHY = pf.GEOGRAPHY
    AND f.MARKET = pf.MARKET
    AND f.YEAR = pf.YEAR
    AND f.QUARTER = pf.QUARTER
ORDER BY f.BUSINESS_DOMAIN, f.GEOGRAPHY, f.CONSENSUS_FORECAST DESC;
```

**Why Multiple Forecast Methods:**
1. **Statistical Models:** Based on historical patterns and trends
2. **Pipeline-Based:** Bottom-up from current opportunities
3. **Management Judgment:** Incorporates market intelligence and strategic initiatives
4. **Consensus:** Weighted combination of multiple approaches
5. **Confidence Bands:** Risk assessment and scenario planning

**Alternative Data Sources:**
- **Actuals Tables:** For baseline trending
- **Budget Tables:** For target comparison
- **External Economic Indicators:** For market-driven adjustments

---

## Deal Progress & Status

### 7. "Which deals are stuck or overdue in the pipeline?" (Aged Pipeline)

#### **Deep Analysis:**
**Complexity Factors:**
- Stage-specific aging thresholds vary by business domain
- "Stuck" vs "overdue" have different implications
- Need historical progression data to identify stagnation
- Different urgency levels based on deal size and strategic importance

**Primary Table:** MQT Pipeline with time-based filtering and stage analysis

#### **Aged Pipeline Analysis:**
```sql
-- COMPREHENSIVE: Aged Pipeline Analysis Across All Domains
WITH aged_pipeline_analysis AS (
    -- Consulting Aged Pipeline
    SELECT 
        'Consulting' AS BUSINESS_DOMAIN,
        p.GEOGRAPHY,
        p.MARKET,
        p.CLIENT_NAME,
        p.OPPORTUNITY_NAME,
        p.SALES_STAGE,
        p.OPPORTUNITY_VALUE,
        p.PPV_AMT,
        p.DAYS_IN_STAGE,
        p.DAYS_IN_PIPELINE,
        p.SALES_REP_NAME,
        p.EXPECTED_CLOSE_DATE,
        CURRENT_DATE - p.EXPECTED_CLOSE_DATE AS DAYS_OVERDUE,
        -- Age categorization based on consulting sales cycle
        CASE 
            WHEN p.SALES_STAGE = 'Qualify' AND p.DAYS_IN_STAGE > 45 THEN 'Aged'
            WHEN p.SALES_STAGE = 'Design' AND p.DAYS_IN_STAGE > 60 THEN 'Aged'
            WHEN p.SALES_STAGE = 'Propose' AND p.DAYS_IN_STAGE > 30 THEN 'Aged'
            WHEN p.SALES_STAGE = 'Negotiate' AND p.DAYS_IN_STAGE > 21 THEN 'Aged'
            WHEN p.SALES_STAGE = 'Closing' AND p.DAYS_IN_STAGE > 14 THEN 'Aged'
            ELSE 'Current'
        END AS AGE_STATUS,
        -- Risk categorization
        CASE 
            WHEN p.EXPECTED_CLOSE_DATE < CURRENT_DATE - 30 THEN 'High Risk'
            WHEN p.EXPECTED_CLOSE_DATE < CURRENT_DATE THEN 'Medium Risk'
            WHEN p.DAYS_IN_STAGE > 90 THEN 'Medium Risk'
            ELSE 'Low Risk'
        END AS RISK_LEVEL,
        -- Strategic importance
        CASE 
            WHEN p.OPPORTUNITY_VALUE >= 5000000 THEN 'Strategic'
            WHEN p.OPPORTUNITY_VALUE >= 1000000 THEN 'Major'
            ELSE 'Standard'
        END AS DEAL_IMPORTANCE,
        p.LAST_ACTIVITY_DATE,
        CURRENT_DATE - p.LAST_ACTIVITY_DATE AS DAYS_SINCE_ACTIVITY
    FROM 
        PROD_MQT_CONSULTING_PIPELINE p
    WHERE 
        p.RELATIVE_QUARTER_MNEUMONIC = 'CQ'
        AND p.SNAPSHOT_LEVEL = 'W'
        AND p.WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
        AND p.SALES_STAGE NOT IN ('Won', 'Lost')
        AND (
            (p.SALES_STAGE = 'Qualify' AND p.DAYS_IN_STAGE > 45) OR
            (p.SALES_STAGE = 'Design' AND p.DAYS_IN_STAGE > 60) OR
            (p.SALES_STAGE = 'Propose' AND p.DAYS_IN_STAGE > 30) OR
            (p.SALES_STAGE = 'Negotiate' AND p.DAYS_IN_STAGE > 21) OR
            (p.SALES_STAGE = 'Closing' AND p.DAYS_IN_STAGE > 14) OR
            p.EXPECTED_CLOSE_DATE < CURRENT_DATE
        )
    
    UNION ALL
    
    -- Software Transactional Aged Pipeline
    SELECT 
        'Software Transactional' AS BUSINESS_DOMAIN,
        p.GEOGRAPHY,
        p.MARKET,
        p.CLIENT_NAME,
        p.OPPORTUNITY_NAME,
        p.SALES_STAGE,
        p.TOTAL_CONTRACT_VALUE AS OPPORTUNITY_VALUE,
        p.WEIGHTED_PIPELINE_AMT AS PPV_AMT,
        p.DAYS_IN_STAGE,
        p.DAYS_IN_PIPELINE,
        p.SALES_REP_NAME,
        p.EXPECTED_CLOSE_DATE,
        CURRENT_DATE - p.EXPECTED_CLOSE_DATE AS DAYS_OVERDUE,
        -- Software-specific aging thresholds (typically longer cycles)
        CASE 
            WHEN p.SALES_STAGE = 'Lead' AND p.DAYS_IN_STAGE > 30 THEN 'Aged'
            WHEN p.SALES_STAGE = 'Qualified' AND p.DAYS_IN_STAGE > 60 THEN 'Aged'
            WHEN p.SALES_STAGE = 'Proposal' AND p.DAYS_IN_STAGE > 45 THEN 'Aged'
            WHEN p.SALES_STAGE = 'Negotiation' AND p.DAYS_IN_STAGE > 60 THEN 'Aged'
            WHEN p.SALES_STAGE = 'Verbal Commit' AND p.DAYS_IN_STAGE > 30 THEN 'Aged'
            WHEN p.SALES_STAGE = 'Contracting' AND p.DAYS_IN_STAGE > 21 THEN 'Aged'
            ELSE 'Current'
        END AS AGE_STATUS,
        CASE 
            WHEN p.EXPECTED_CLOSE_DATE < CURRENT_DATE - 45 THEN 'High Risk'
            WHEN p.EXPECTED_CLOSE_DATE < CURRENT_DATE THEN 'Medium Risk'
            WHEN p.DAYS_IN_STAGE > 120 THEN 'Medium Risk'
            ELSE 'Low Risk'
        END AS RISK_LEVEL,
        CASE 
            WHEN p.TOTAL_CONTRACT_VALUE >= 2000000 THEN 'Strategic'
            WHEN p.TOTAL_CONTRACT_VALUE >= 500000 THEN 'Major'
            ELSE 'Standard'
        END AS DEAL_IMPORTANCE,
        p.LAST_ACTIVITY_DATE,
        CURRENT_DATE - p.LAST_ACTIVITY_DATE AS DAYS_SINCE_ACTIVITY
    FROM 
        PROD_MQT_SOFTWARE_TRANSACTIONAL_PIPELINE p
    WHERE 
        p.RELATIVE_QUARTER_MNEUMONIC = 'CQ'
        AND p.SNAPSHOT_LEVEL = 'W'
        AND p.WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_SOFTWARE_TRANSACTIONAL_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
        AND p.SALES_STAGE NOT IN ('Won', 'Lost')
        AND (
            (p.SALES_STAGE = 'Lead' AND p.DAYS_IN_STAGE > 30) OR
            (p.SALES_STAGE = 'Qualified' AND p.DAYS_IN_STAGE > 60) OR
            (p.SALES_STAGE = 'Proposal' AND p.DAYS_IN_STAGE > 45) OR
            (p.SALES_STAGE = 'Negotiation' AND p.DAYS_IN_STAGE > 60) OR
            (p.SALES_STAGE = 'Verbal Commit' AND p.DAYS_IN_STAGE > 30) OR
            (p.SALES_STAGE = 'Contracting' AND p.DAYS_IN_STAGE > 21) OR
            p.EXPECTED_CLOSE_DATE < CURRENT_DATE
        )
    
    UNION ALL
    
    -- SaaS Aged Pipeline (faster cycles)
    SELECT 
        'SaaS' AS BUSINESS_DOMAIN,
        p.GEOGRAPHY,
        p.MARKET,
        p.CLIENT_NAME,
        p.OPPORTUNITY_NAME,
        p.SALES_STAGE,
        p.ARR_PIPELINE_AMT AS OPPORTUNITY_VALUE,
        p.WEIGHTED_ARR_AMT AS PPV_AMT,
        p.DAYS_IN_STAGE,
        p.DAYS_IN_PIPELINE,
        p.SALES_REP_NAME,
        p.EXPECTED_CLOSE_DATE,
        CURRENT_DATE - p.EXPECTED_CLOSE_DATE AS DAYS_OVERDUE,
        -- SaaS-specific aging (shorter cycles)
        CASE 
            WHEN p.SALES_STAGE = 'Lead' AND p.DAYS_IN_STAGE > 14 THEN 'Aged'
            WHEN p.SALES_STAGE = 'Demo Scheduled' AND p.DAYS_IN_STAGE > 21 THEN 'Aged'
            WHEN p.SALES_STAGE = 'Trial' AND p.DAYS_IN_STAGE > 30 THEN 'Aged'
            WHEN p.SALES_STAGE = 'Proposal' AND p.DAYS_IN_STAGE > 14 THEN 'Aged'
            WHEN p.SALES_STAGE = 'Contract Review' AND p.DAYS_IN_STAGE > 10 THEN 'Aged'
            WHEN p.SALES_STAGE = 'Closing' AND p.DAYS_IN_STAGE > 7 THEN 'Aged'
            ELSE 'Current'
        END AS AGE_STATUS,
        CASE 
            WHEN p.EXPECTED_CLOSE_DATE < CURRENT_DATE - 14 THEN 'High Risk'
            WHEN p.EXPECTED_CLOSE_DATE < CURRENT_DATE THEN 'Medium Risk'
            WHEN p.DAYS_IN_STAGE > 45 THEN 'Medium Risk'
            ELSE 'Low Risk'
        END AS RISK_LEVEL,
        CASE 
            WHEN p.ARR_PIPELINE_AMT >= 500000 THEN 'Strategic'
            WHEN p.ARR_PIPELINE_AMT >= 100000 THEN 'Major'
            ELSE 'Standard'
        END AS DEAL_IMPORTANCE,
        p.LAST_ACTIVITY_DATE,
        CURRENT_DATE - p.LAST_ACTIVITY_DATE AS DAYS_SINCE_ACTIVITY
    FROM 
        PROD_MQT_SW_SAAS_PIPELINE p
    WHERE 
        p.RELATIVE_QUARTER_MNEUMONIC = 'CQ'
        AND p.SNAPSHOT_LEVEL = 'W'
        AND p.WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_SW_SAAS_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
        AND p.SALES_STAGE NOT IN ('Won', 'Lost')
        AND (
            (p.SALES_STAGE = 'Lead' AND p.DAYS_IN_STAGE > 14) OR
            (p.SALES_STAGE = 'Demo Scheduled' AND p.DAYS_IN_STAGE > 21) OR
            (p.SALES_STAGE = 'Trial' AND p.DAYS_IN_STAGE > 30) OR
            (p.SALES_STAGE = 'Proposal' AND p.DAYS_IN_STAGE > 14) OR
            (p.SALES_STAGE = 'Contract Review' AND p.DAYS_IN_STAGE > 10) OR
            (p.SALES_STAGE = 'Closing' AND p.DAYS_IN_STAGE > 7) OR
            p.EXPECTED_CLOSE_DATE < CURRENT_DATE
        )
)
SELECT 
    BUSINESS_DOMAIN,
    GEOGRAPHY,
    MARKET,
    CLIENT_NAME,
    OPPORTUNITY_NAME,
    SALES_STAGE,
    OPPORTUNITY_VALUE,
    PPV_AMT,
    DAYS_IN_STAGE,
    DAYS_IN_PIPELINE,
    DAYS_OVERDUE,
    AGE_STATUS,
    RISK_LEVEL,
    DEAL_IMPORTANCE,
    SALES_REP_NAME,
    EXPECTED_CLOSE_DATE,
    DAYS_SINCE_ACTIVITY,
    -- Action priority scoring
    CASE 
        WHEN RISK_LEVEL = 'High Risk' AND DEAL_IMPORTANCE = 'Strategic' THEN 1
        WHEN RISK_LEVEL = 'High Risk' AND DEAL_IMPORTANCE = 'Major' THEN 2
        WHEN RISK_LEVEL = 'Medium Risk' AND DEAL_IMPORTANCE = 'Strategic' THEN 3
        WHEN RISK_LEVEL = 'High Risk' AND DEAL_IMPORTANCE = 'Standard' THEN 4
        WHEN RISK_LEVEL = 'Medium Risk' AND DEAL_IMPORTANCE = 'Major' THEN 5
        ELSE 6
    END AS ACTION_PRIORITY,
    -- Recommended actions
    CASE 
        WHEN DAYS_SINCE_ACTIVITY > 14 THEN 'URGENT: Schedule client contact'
        WHEN DAYS_OVERDUE > 30 THEN 'URGENT: Re-qualify opportunity'
        WHEN DAYS_IN_STAGE > 60 AND SALES_STAGE IN ('Propose', 'Proposal') THEN 'ACTION: Follow up on proposal'
        WHEN DAYS_IN_STAGE > 30 AND SALES_STAGE IN ('Negotiate', 'Negotiation') THEN 'ACTION: Escalate negotiation'
        WHEN DAYS_IN_STAGE > 14 AND SALES_STAGE = 'Closing' THEN 'ACTION: Remove close barriers'
        ELSE 'MONITOR: Regular cadence'
    END AS RECOMMENDED_ACTION
FROM aged_pipeline_analysis
ORDER BY ACTION_PRIORITY, OPPORTUNITY_VALUE DESC;
```

**Why Domain-Specific Aging Thresholds:**
1. **Business Cycle Differences:** SaaS cycles are typically 30-90 days, software can be 6-18 months, consulting varies widely
2. **Stage Expectations:** Each stage has natural duration based on complexity
3. **Risk Calibration:** What constitutes "stuck" varies by deal complexity and average cycle time
4. **Action Urgency:** Priority scoring enables focused intervention

### 8. "Which opportunities have gone the longest without activity?"

#### **Deep Analysis:**
**Data Availability Challenge:** Activity tracking requires either:
- Activity timestamps in pipeline tables
- Separate activity/engagement tables
- CRM integration data

**Assumptions:** Using LAST_ACTIVITY_DATE field in pipeline tables as primary source

#### **Inactive Opportunities Analysis:**
```sql
-- COMPREHENSIVE: Inactive Opportunities Across All Domains
WITH activity_analysis AS (
    -- Consulting Inactive Opportunities
    SELECT 
        'Consulting' AS BUSINESS_DOMAIN,
        p.GEOGRAPHY,
        p.MARKET,
        p.CLIENT_NAME,
        p.OPPORTUNITY_NAME,
        p.SALES_STAGE,
        p.OPPORTUNITY_VALUE,
        p.SALES_REP_NAME,
        p.LAST_ACTIVITY_DATE,
        p.EXPECTED_CLOSE_DATE,
        CURRENT_DATE - p.LAST_ACTIVITY_DATE AS DAYS_WITHOUT_ACTIVITY,
        p.DAYS_IN_STAGE,
        -- Activity pattern analysis
        CASE 
            WHEN p.LAST_ACTIVITY_DATE IS NULL THEN 'No Activity Recorded'
            WHEN CURRENT_DATE - p.LAST_ACTIVITY_DATE > 30 THEN 'Inactive (30+ days)'
            WHEN CURRENT_DATE - p.LAST_ACTIVITY_DATE > 14 THEN 'Low Activity (14+ days)'
            WHEN CURRENT_DATE - p.LAST_ACTIVITY_DATE > 7 THEN 'Moderate Activity (7+ days)'
            ELSE 'Recent Activity'
        END AS ACTIVITY_STATUS,
        -- Risk assessment based on stage and inactivity
        CASE 
            WHEN p.LAST_ACTIVITY_DATE IS NULL THEN 'Critical'
            WHEN CURRENT_DATE - p.LAST_ACTIVITY_DATE > 45 THEN 'High Risk'
            WHEN CURRENT_DATE - p.LAST_ACTIVITY_DATE > 21 AND p.SALES_STAGE IN ('Negotiate', 'Closing') THEN 'High Risk'
            WHEN CURRENT_DATE - p.LAST_ACTIVITY_DATE > 30 THEN 'Medium Risk'
            ELSE 'Low Risk'
        END AS INACTIVITY_RISK,
        -- Business impact
        CASE 
            WHEN p.OPPORTUNITY_VALUE >= 5000000 THEN 'High Impact'
            WHEN p.OPPORTUNITY_VALUE >= 1000000 THEN 'Medium Impact'
            ELSE 'Low Impact'
        END AS BUSINESS_IMPACT
    FROM 
        PROD_MQT_CONSULTING_PIPELINE p
    WHERE 
        p.RELATIVE_QUARTER_MNEUMONIC = 'CQ'
        AND p.SNAPSHOT_LEVEL = 'W'
        AND p.WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_CONSULTING_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
        AND p.SALES_STAGE NOT IN ('Won', 'Lost')
        AND (
            p.LAST_ACTIVITY_DATE IS NULL OR
            CURRENT_DATE - p.LAST_ACTIVITY_DATE > 7
        )
    
    UNION ALL
    
    -- Software Transactional Inactive Opportunities
    SELECT 
        'Software Transactional' AS BUSINESS_DOMAIN,
        p.GEOGRAPHY,
        p.MARKET,
        p.CLIENT_NAME,
        p.OPPORTUNITY_NAME,
        p.SALES_STAGE,
        p.TOTAL_CONTRACT_VALUE AS OPPORTUNITY_VALUE,
        p.SALES_REP_NAME,
        p.LAST_ACTIVITY_DATE,
        p.EXPECTED_CLOSE_DATE,
        CURRENT_DATE - p.LAST_ACTIVITY_DATE AS DAYS_WITHOUT_ACTIVITY,
        p.DAYS_IN_STAGE,
        CASE 
            WHEN p.LAST_ACTIVITY_DATE IS NULL THEN 'No Activity Recorded'
            WHEN CURRENT_DATE - p.LAST_ACTIVITY_DATE > 45 THEN 'Inactive (45+ days)'
            WHEN CURRENT_DATE - p.LAST_ACTIVITY_DATE > 21 THEN 'Low Activity (21+ days)'
            WHEN CURRENT_DATE - p.LAST_ACTIVITY_DATE > 10 THEN 'Moderate Activity (10+ days)'
            ELSE 'Recent Activity'
        END AS ACTIVITY_STATUS,
        CASE 
            WHEN p.LAST_ACTIVITY_DATE IS NULL THEN 'Critical'
            WHEN CURRENT_DATE - p.LAST_ACTIVITY_DATE > 60 THEN 'High Risk'
            WHEN CURRENT_DATE - p.LAST_ACTIVITY_DATE > 30 AND p.SALES_STAGE IN ('Negotiation', 'Contracting') THEN 'High Risk'
            WHEN CURRENT_DATE - p.LAST_ACTIVITY_DATE > 45 THEN 'Medium Risk'
            ELSE 'Low Risk'
        END AS INACTIVITY_RISK,
        CASE 
            WHEN p.TOTAL_CONTRACT_VALUE >= 2000000 THEN 'High Impact'
            WHEN p.TOTAL_CONTRACT_VALUE >= 500000 THEN 'Medium Impact'
            ELSE 'Low Impact'
        END AS BUSINESS_IMPACT
    FROM 
        PROD_MQT_SOFTWARE_TRANSACTIONAL_PIPELINE p
    WHERE 
        p.RELATIVE_QUARTER_MNEUMONIC = 'CQ'
        AND p.SNAPSHOT_LEVEL = 'W'
        AND p.WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_SOFTWARE_TRANSACTIONAL_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
        AND p.SALES_STAGE NOT IN ('Won', 'Lost')
        AND (
            p.LAST_ACTIVITY_DATE IS NULL OR
            CURRENT_DATE - p.LAST_ACTIVITY_DATE > 10
        )
    
    UNION ALL
    
    -- SaaS Inactive Opportunities (faster cadence expected)
    SELECT 
        'SaaS' AS BUSINESS_DOMAIN,
        p.GEOGRAPHY,
        p.MARKET,
        p.CLIENT_NAME,
        p.OPPORTUNITY_NAME,
        p.SALES_STAGE,
        p.ARR_PIPELINE_AMT AS OPPORTUNITY_VALUE,
        p.SALES_REP_NAME,
        p.LAST_ACTIVITY_DATE,
        p.EXPECTED_CLOSE_DATE,
        CURRENT_DATE - p.LAST_ACTIVITY_DATE AS DAYS_WITHOUT_ACTIVITY,
        p.DAYS_IN_STAGE,
        CASE 
            WHEN p.LAST_ACTIVITY_DATE IS NULL THEN 'No Activity Recorded'
            WHEN CURRENT_DATE - p.LAST_ACTIVITY_DATE > 14 THEN 'Inactive (14+ days)'
            WHEN CURRENT_DATE - p.LAST_ACTIVITY_DATE > 7 THEN 'Low Activity (7+ days)'
            WHEN CURRENT_DATE - p.LAST_ACTIVITY_DATE > 3 THEN 'Moderate Activity (3+ days)'
            ELSE 'Recent Activity'
        END AS ACTIVITY_STATUS,
        CASE 
            WHEN p.LAST_ACTIVITY_DATE IS NULL THEN 'Critical'
            WHEN CURRENT_DATE - p.LAST_ACTIVITY_DATE > 21 THEN 'High Risk'
            WHEN CURRENT_DATE - p.LAST_ACTIVITY_DATE > 10 AND p.SALES_STAGE IN ('Contract Review', 'Closing') THEN 'High Risk'
            WHEN CURRENT_DATE - p.LAST_ACTIVITY_DATE > 14 THEN 'Medium Risk'
            ELSE 'Low Risk'
        END AS INACTIVITY_RISK,
        CASE 
            WHEN p.ARR_PIPELINE_AMT >= 500000 THEN 'High Impact'
            WHEN p.ARR_PIPELINE_AMT >= 100000 THEN 'Medium Impact'
            ELSE 'Low Impact'
        END AS BUSINESS_IMPACT
    FROM 
        PROD_MQT_SW_SAAS_PIPELINE p
    WHERE 
        p.RELATIVE_QUARTER_MNEUMONIC = 'CQ'
        AND p.SNAPSHOT_LEVEL = 'W'
        AND p.WEEK = (SELECT MAX(WEEK) FROM PROD_MQT_SW_SAAS_PIPELINE WHERE RELATIVE_QUARTER_MNEUMONIC = 'CQ')
        AND p.SALES_STAGE NOT IN ('Won', 'Lost')
        AND (
            p.LAST_ACTIVITY_DATE IS NULL OR
            CURRENT_DATE - p.LAST_ACTIVITY_DATE > 3
        )
),
-- Activity summary by rep and territory
rep_activity_summary AS (
    SELECT 
        BUSINESS_DOMAIN,
        GEOGRAPHY,
        SALES_REP_NAME,
        COUNT(*) AS INACTIVE_OPPORTUNITIES,
        SUM(OPPORTUNITY_VALUE) AS INACTIVE_PIPELINE_VALUE,
        AVG(DAYS_WITHOUT_ACTIVITY) AS AVG_DAYS_INACTIVE,
        MAX(DAYS_WITHOUT_ACTIVITY) AS MAX_DAYS_INACTIVE,
        COUNT(CASE WHEN INACTIVITY_RISK = 'Critical' THEN 1 END) AS CRITICAL_OPPORTUNITIES,
        COUNT(CASE WHEN INACTIVITY_RISK = 'High Risk' THEN 1 END) AS HIGH_RISK_OPPORTUNITIES
    FROM activity_analysis
    GROUP BY BUSINESS_DOMAIN, GEOGRAPHY, SALES_REP_NAME
)
-- Main results with rep performance context
SELECT 
    a.BUSINESS_DOMAIN,
    a.GEOGRAPHY,
    a.MARKET,
    a.CLIENT_NAME,
    a.OPPORTUNITY_NAME,
    a.SALES_STAGE,
    a.OPPORTUNITY_VALUE,
    a.SALES_REP_NAME,
    a.LAST_ACTIVITY_DATE,
    a.DAYS_WITHOUT_ACTIVITY,
    a.ACTIVITY_STATUS,
    a.INACTIVITY_RISK,
    a.BUSINESS_IMPACT,
    a.EXPECTED_CLOSE_DATE,
    -- Rep context
    r.INACTIVE_OPPORTUNITIES AS REP_TOTAL_INACTIVE,
    r.AVG_DAYS_INACTIVE AS REP_AVG_DAYS_INACTIVE,
    -- Priority scoring
    CASE 
        WHEN a.INACTIVITY_RISK = 'Critical' AND a.BUSINESS_IMPACT = 'High Impact' THEN 1
        WHEN a.INACTIVITY_RISK = 'Critical' THEN 2
        WHEN a.INACTIVITY_RISK = 'High Risk' AND a.BUSINESS_IMPACT = 'High Impact' THEN 3
        WHEN a.INACTIVITY_RISK = 'High Risk' THEN 4
        ELSE 5
    END AS PRIORITY_SCORE,
    -- Recommended actions
    CASE 
        WHEN a.LAST_ACTIVITY_DATE IS NULL THEN 'CRITICAL: Contact immediately - no activity on record'
        WHEN a.DAYS_WITHOUT_ACTIVITY > 60 THEN 'URGENT: Re-qualify opportunity'
        WHEN a.DAYS_WITHOUT_ACTIVITY > 30 AND a.SALES_STAGE IN ('Closing', 'Contracting') THEN 'URGENT: Unblock close barriers'
        WHEN a.DAYS_WITHOUT_ACTIVITY > 21 THEN 'HIGH: Schedule stakeholder meeting'
        WHEN a.DAYS_WITHOUT_ACTIVITY > 14 THEN 'MEDIUM: Follow up on proposal/demo'
        ELSE 'LOW: Regular cadence check'
    END AS RECOMMENDED_ACTION
FROM activity_analysis a
LEFT JOIN rep_activity_summary r
    ON a.BUSINESS_DOMAIN = r.BUSINESS_DOMAIN
    AND a.GEOGRAPHY = r.GEOGRAPHY
    AND a.SALES_REP_NAME = r.SALES_REP_NAME
ORDER BY PRIORITY_SCORE, DAYS_WITHOUT_ACTIVITY DESC;
```

**Why Domain-Specific Activity Thresholds:**
1. **Sales Velocity Differences:** SaaS requires more frequent touchpoints than enterprise software
2. **Customer Engagement Patterns:** Different industries have different communication norms  
3. **Deal Complexity:** Complex deals naturally have longer gaps between activities
4. **Sales Process Requirements:** Some stages require waiting periods (legal review, approvals)

---

*[Continuing with remaining categories due to length limits...]*