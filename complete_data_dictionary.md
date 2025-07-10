# IBM Sales Pipeline Analytics - Complete Data Dictionary

## Overview
This document provides a comprehensive reference for all columns in the IBM Sales Pipeline MQT tables, including their definitions, calculations, and business context.

---

## 📊 FINANCIAL METRICS

### Pipeline Values

| Column | Description | Calculation/Formula | Business Use |
|--------|-------------|-------------------|--------------|
| **OPPORTUNITY_VALUE** | Total value of the opportunity by line item | Set by sales team in CRM | Base metric for all pipeline calculations |
| **CALL_AMT** | FLM-committed pipeline value | `OPPORTUNITY_VALUE WHERE FLM_JUDGEMENT_INDICATOR = TRUE` | High-confidence revenue forecast |
| **UPSIDE_AMT** | Non-committed pipeline in advanced stages | `OPPORTUNITY_VALUE WHERE SALES_STAGE IN ('Negotiate', 'Propose') AND FLM_JUDGEMENT_INDICATOR = FALSE` | Additional opportunities beyond committed |
| **QUALIFY_PLUS_AMT** | Advanced stage pipeline value | `SUM(OPPORTUNITY_VALUE WHERE SALES_STAGE IN ('Closing', 'Design', 'Negotiate', 'Propose', 'Qualify'))` | Qualified pipeline metric |
| **PROPOSE_PLUS_AMT** | Late-stage pipeline value | `SUM(OPPORTUNITY_VALUE WHERE SALES_STAGE IN ('Closing', 'Negotiate', 'Propose'))` | Near-term revenue potential |
| **NEGOTIATE_PLUS_AMT** | Final stage pipeline value | `SUM(OPPORTUNITY_VALUE WHERE SALES_STAGE IN ('Closing', 'Negotiate'))` | Imminent closure opportunities |
| **OPEN_PIPELINE_AMT** | All active pipeline value | `SUM(OPPORTUNITY_VALUE WHERE SALES_STAGE NOT IN ('Won', 'Lost'))` | Total active opportunities |
| **WON_AMT** | Closed/won opportunity value | `SUM(OPPORTUNITY_VALUE WHERE SALES_STAGE = 'Won')` | Actual achieved revenue |
| **PPV_AMT** | PERFORM Pipeline Value | AI-generated end-of-quarter assessment by CAO, updated weekly | Most accurate revenue prediction |

### Budget & Targets

| Column | Description | Calculation/Formula | Business Use |
|--------|-------------|-------------------|--------------|
| **REVENUE_BUDGET_AMT** | Revenue target/quota | Set by finance planning | Performance measurement baseline |
| **SIGNINGS_BUDGET_AMT** | Signings target/quota | Set by finance planning | Bookings target for sales teams |
| **GROSS_PROFIT_BUDGET_AMT** | Gross profit target | Set by finance planning | Profitability target |

### Actual Performance

| Column | Description | Calculation/Formula | Business Use |
|--------|-------------|-------------------|--------------|
| **REVENUE_AMT** | Actual recognized revenue | From financial systems | Historical performance tracking |
| **GROSS_PROFIT_AMT** | Actual gross profit | `REVENUE_AMT - COST_OF_GOODS_SOLD` | Profitability analysis |
| **GROSS_PROFIT_WITH_COST_CENTER_AMT** | GP with cost center allocation | GP with internal cost allocations | Detailed profitability view |

### Prior Year Comparisons

| Column | Description | Calculation/Formula | Business Use |
|--------|-------------|-------------------|--------------|
| **[METRIC]_PY** | Prior year value (any metric) | Same metric from previous year | Year-over-year comparison |
| **[METRIC]_PPY** | Prior prior year value | Same metric from 2 years ago | Multi-year trend analysis |

---

## 🎯 CALCULATED METRICS & FORMULAS

### Key Performance Indicators

| Metric | Formula | Description | Target Range |
|--------|---------|-------------|--------------|
| **PPV Coverage %** | `(PPV_AMT / BUDGET_AMT) * 100` | Pipeline coverage vs budget | 100%+ (on track) |
| **Budget YoY %** | `((Current_Budget - Prior_Budget) / Prior_Budget) * 100` | Budget growth year-over-year | Positive growth |
| **Qualify+ YoY %** | `((Current_Qualify - Prior_Qualify) / Prior_Qualify) * 100` | Pipeline growth year-over-year | Positive growth |
| **Win Rate %** | `(WON_DEALS / (WON_DEALS + LOST_DEALS)) * 100` | Success rate of closed deals | 30%+ typical |
| **Multiplier** | `QUALIFY_PLUS_AMT / BUDGET_AMT` | Pipeline coverage ratio | 4x recommended |
| **PPV (B/W)** | `PPV_AMT - BUDGET_AMT` | Pipeline gap to budget | Positive = surplus |

### Week-to-Week Tracking

| Metric | Formula | Description | Use Case |
|--------|---------|-------------|----------|
| **Qualify+ WtW** | `Current_Week_Qualify - Prior_Week_Qualify` | Weekly pipeline movement | Pipeline velocity tracking |
| **Weekly Track %** | `(Current_Week_Qualify / Track_Target) * 100` | Performance vs track | Pipeline health assessment |
| **Track Target** | `4x_Budget - ((Week_Number + 13) / 14 * Pipeline_Increment)` | Linear track to 4x budget | Target setting |

### Pipeline Health Scores

| Component | Weight | Formula | Description |
|-----------|--------|---------|-------------|
| **Closing Rate** | 40% | `(CLOSING_AMT / QUALIFY_PLUS_AMT) * 100` | Advanced stage conversion |
| **PPV Ratio** | 30% | `(PPV_AMT / QUALIFY_PLUS_AMT) * 100` | AI confidence score |
| **Client Diversity** | 20% | `COUNT(DISTINCT CLIENT_NAME)` | Risk distribution |
| **Deal Size** | 10% | `AVG(OPPORTUNITY_VALUE)` | Deal quality indicator |

---

## 🗓️ TIME DIMENSIONS

### Time Period Fields

| Column | Description | Values | Business Use |
|--------|-------------|--------|--------------|
| **YEAR** | Calendar year | 2024, 2025, etc. | Annual comparisons |
| **QUARTER** | Quarter number | 1, 2, 3, 4 | Quarterly planning |
| **MONTH** | Month number | 1-12 | Monthly tracking |
| **WEEK** | Week in quarter | -13 to +13 (relative to quarter) | Weekly pipeline management |
| **SALES_WEEK_DESCRIPTION** | Week description | "2025Q1W03" | Human-readable period |

### Relative Time Fields

| Column | Description | Values | Business Use |
|--------|-------------|--------|--------------|
| **RELATIVE_QUARTER_MNEUMONIC** | Quarter relative to current | CQ, NQ, PQ | Current/Next/Previous quarter |
| **SNAPSHOT_LEVEL** | Data aggregation level | W (Weekly), M (Monthly) | Report granularity |
| **FORECAST_MONTH** | Month within quarter | 1, 2, 3 | Intra-quarter planning |

### Date Fields

| Column | Description | Format | Business Use |
|--------|-------------|--------|--------------|
| **OPP_CREATE_DATE** | Opportunity creation date | YYYY-MM-DD | Age calculation |
| **OPP_FORECAST_DATE** | Expected close date | YYYY-MM-DD | Timeline planning |
| **OPP_WIN_LOSS_DATE** | Actual close date | YYYY-MM-DD | Performance tracking |

---

## 🌍 GEOGRAPHIC & TERRITORY DIMENSIONS

### Primary Geography

| Column | Description | Values | Business Use |
|--------|-------------|--------|--------------|
| **GEOGRAPHY** | Major geographic region | Americas, EMEA, APAC | Regional performance |
| **MARKET** | Market segment | US Federal, UK Market, Japan Market | Market-specific analysis |
| **SECTOR** | Industry sector | Financial, Government, Healthcare | Vertical performance |
| **COUNTRY** | Country name | US, UK, Japan, Germany, etc. | Country-level tracking |
| **REGION** | Sub-geographic region | US Northeast, EMEA West | Detailed territory view |
| **BRANCH** | Sales branch | Specific branch identifiers | Local sales management |

### Client Classification

| Column | Description | Values | Business Use |
|--------|-------------|--------|--------------|
| **CLIENT_TYPE** | Client segmentation | TARGET ENTERPRISE, ENTERPRISE, etc. | Account strategy |
| **CLIENT_SUB_TYPE** | Detailed client type | Select Clients, Select TSR, etc. | Refined segmentation |
| **ACCOUNT_TYPE** | Account classification | FOUNDATION, PREMIER, etc. | Account management |

---

## 🏢 CLIENT & CUSTOMER DIMENSIONS

### Client Identification

| Column | Description | Format | Business Use |
|--------|-------------|--------|--------------|
| **CLIENT_NAME** | Customer name | Text | Client identification |
| **CUSTOMER_NAME** | Same as CLIENT_NAME | Text | Legacy field |
| **CUSTOMER_NUMBER** | IBM Customer Number (ICN) | Alphanumeric | Unique customer ID |
| **GLOBAL_CLIENT** | Global client grouping | Text | Worldwide account view |
| **DOMESTIC_CLIENT** | Country-level client name | Text | Local account management |
| **GLOBAL_BUYING_GROUP** | Buying group classification | Text | Procurement strategy |

### Industry Classification

| Column | Description | Values | Business Use |
|--------|-------------|--------|--------------|
| **INDUSTRY** | Industry vertical | Government, Financial, Manufacturing | Vertical analysis |
| **GLOBAL_INDUSTRY_GROUP** | IBM industry grouping | Signature/Strategic groupings | Strategic account focus |
| **TRADITIONAL_INDUSTRY** | Sector classification | Technology, Healthcare, Energy | GTM structure alignment |

---

## 📦 PRODUCT & SERVICE DIMENSIONS

### Unified Taxonomy (UT) Hierarchy

| Column | Description | Level | Business Use |
|--------|-------------|-------|--------------|
| **UT10_NAME** | Top-level product category | L10 | Highest product grouping |
| **UT15_NAME** | Service line grouping | L15 | Major service lines |
| **UT17_NAME** | Detailed service category | L17 | Specific service offerings |
| **UT20_NAME** | Product family | L20 | Product family analysis |
| **UT30_NAME** | Specific product/service | L30 | Detailed product tracking |
| **UT30_CODE** | Product code | L30 | System integration |

### Service Classifications

| Column | Description | Values | Business Use |
|--------|-------------|--------|--------------|
| **PRACTICE** | Service practice area | Cybersecurity, Cloud, AI, etc. | Practice performance |
| **PRODUCT_FAMILY_NAME** | Broad product classification | Software, Services, Hardware | Portfolio analysis |
| **CLASSIFICATION** | Contract type | Professional Services, Software | Delivery model |
| **TERM** | Contract duration | 1 year, 3 years, etc. | Revenue recognition |

---

## 📈 SALES PROCESS DIMENSIONS

### Sales Stage Progression

| Column | Description | Values | Business Use |
|--------|-------------|--------|--------------|
| **SALES_STAGE** | Current opportunity stage | Engage, Design, Qualify, Propose, Negotiate, Closing, Won, Lost | Pipeline management |
| **ISC_SALES_STAGE** | Full sales stage name | Detailed stage descriptions | Process adherence |
| **SALES_FORECAST_CATEGORY** | Likelihood category | Based on sales stage | Probability assessment |

### Deal Characteristics

| Column | Description | Values | Business Use |
|--------|-------------|--------|--------------|
| **DEAL_SIZE** | Deal size category | small, medium, large | Resource allocation |
| **REVENUE_TYPE** | Revenue recognition type | Transactional, Signings TCV, Signings ACV | Financial planning |
| **FLM_JUDGEMENT_INDICATOR** | FLM commitment flag | TRUE/FALSE | Management commitment |

### Opportunity Tracking

| Column | Description | Calculation | Business Use |
|--------|-------------|-------------|--------------|
| **OPP_AGE** | Days in pipeline | `CURRENT_DATE - OPP_CREATE_DATE` | Velocity tracking |
| **OPPORTUNITY_SOURCE_NAME** | Lead source | From CRM | Source effectiveness |
| **OPP_OWNER** | Opportunity owner | Sales rep name | Performance tracking |
| **OPP_OWNER_EMAIL** | Owner email | Email address | Contact management |

---

## 🤖 AI & TECHNOLOGY INDICATORS

### GenAI Classification

| Column | Description | Values | Business Use |
|--------|-------------|--------|--------------|
| **IBM_GEN_AI_IND** | IBM GenAI involvement | 0, 1 | AI solution tracking |
| **PARTNER_GEN_AI_IND** | Partner GenAI involvement | 0, 1 | Ecosystem AI tracking |

---

## 💰 REVENUE BREAKDOWN

### Monthly Revenue Split

| Column | Description | Business Use |
|--------|-------------|--------------|
| **MON1_SIGNINGS_REV** | Month 1 revenue split | Intra-quarter revenue planning |
| **MON2_SIGNINGS_REV** | Month 2 revenue split | Monthly revenue forecasting |
| **MON3_SIGNINGS_REV** | Month 3 revenue split | Quarter-end revenue prediction |
| **IQR** | In Quarter Revenue | Revenue expected within quarter |

---

## 🎯 SPECIAL PIPELINE METRICS

### PWP (Pipeline with Purpose) Metrics

| Column | Description | Calculation | Business Use |
|--------|-------------|-------------|--------------|
| **HIGH_PWP_OUT_CALL** | High PWP outside call | Advanced algorithm | Risk assessment |
| **LOW_PWP_IN_CALL** | Low PWP inside call | Advanced algorithm | Opportunity quality |

---

## 📋 BUSINESS RULES & CALCULATIONS

### Key Business Logic

1. **Qualify+ Definition**: Opportunities in stages: Closing, Design, Negotiate, Propose, Qualify
2. **Call Amount**: Only opportunities with FLM Judgement Indicator = TRUE
3. **Upside Amount**: Negotiate/Propose stage opportunities WITHOUT FLM commitment
4. **PPV Updates**: Refreshed weekly on Mondays with Saturday CoB data
5. **Track Logic**: 4x budget target by Week 1 of quarter, linear buildup from Week -13

### Data Quality Rules

1. **PPV Scaling**: Not recommended at individual opportunity level
2. **Historical Comparison**: Prior year fields enable YoY analysis
3. **Time Dimensions**: Week numbers are relative to quarter start
4. **Geographic Hierarchy**: Country → Region → Market → Geography
5. **Product Hierarchy**: UT30 → UT20 → UT17 → UT15 → UT10

---

## 🔍 USAGE GUIDELINES

### When to Use Each Metric

- **OPPORTUNITY_VALUE**: Raw pipeline analysis
- **PPV_AMT**: Most accurate revenue forecasting
- **CALL_AMT**: High-confidence committed pipeline
- **QUALIFY_PLUS_AMT**: Standard pipeline health metric
- **REVENUE_BUDGET_AMT**: Target setting and gap analysis

### Aggregation Best Practices

- **PPV**: Aggregate at UT15 x Market level or higher
- **Win Rates**: Calculate at geography/market level
- **Pipeline Coverage**: Use PPV vs Budget for accuracy
- **YoY Growth**: Compare same time periods
- **Weekly Tracking**: Use Qualify+ for velocity analysis

### Common Calculations

```sql
-- PPV Coverage
PPV_AMT / REVENUE_BUDGET_AMT * 100

-- Win Rate
WON_DEALS / (WON_DEALS + LOST_DEALS) * 100

-- YoY Growth
(CURRENT_YEAR - PRIOR_YEAR) / PRIOR_YEAR * 100

-- Pipeline Multiplier
QUALIFY_PLUS_AMT / REVENUE_BUDGET_AMT

-- Weekly Movement
CURRENT_WEEK_VALUE - PRIOR_WEEK_VALUE
```

---

*This data dictionary serves as the definitive reference for IBM Sales Pipeline Analytics. All calculations and business rules are based on official IBM documentation and data dictionary specifications.*