#!/usr/bin/env python3
"""
Create comprehensive Excel data dictionary for IBM Sales Pipeline Analytics
"""

import pandas as pd
from datetime import datetime

def create_excel_dictionary():
    """Create comprehensive Excel file with all columns and explanations"""
    
    # Comprehensive data dictionary with all discovered columns
    data_dict = [
        # FINANCIAL METRICS - PIPELINE VALUES
        {
            'Category': 'Financial - Pipeline Values',
            'Column': 'OPPORTUNITY_VALUE',
            'Description': 'Total value of the opportunity by line item as set by sales team in CRM',
            'Slovak_Description': 'Celková hodnota príležitosti podľa položky, ako ju nastavil predajný tím v CRM systéme',
            'Calculation': 'Set by sales team in CRM',
            'Business_Use': 'Base metric for all pipeline calculations',
            'Example_Values': '500000, 1200000, 250000',
            'Data_Type': 'Decimal',
            'Table_Source': 'PIPELINE'
        },
        {
            'Category': 'Financial - Pipeline Values',
            'Column': 'CALL_AMT',
            'Description': 'FLM-committed pipeline value - opportunities that FLM has committed to close within the quarter',
            'Slovak_Description': 'Hodnota pipeline, ktorú FLM (First Line Manager) sa zaviazal uzavrieť v rámci štvrťroka',
            'Calculation': 'OPPORTUNITY_VALUE WHERE FLM_JUDGEMENT_INDICATOR = TRUE',
            'Business_Use': 'High-confidence revenue forecast for quarterly planning',
            'Example_Values': '100000, 250000, 0 (if not committed)',
            'Data_Type': 'Decimal',
            'Table_Source': 'PIPELINE'
        },
        {
            'Category': 'Financial - Pipeline Values',
            'Column': 'UPSIDE_AMT',
            'Description': 'Non-committed pipeline in advanced stages (Negotiate/Propose) without FLM commitment',
            'Slovak_Description': 'Nezaviazaný pipeline v pokročilých fázach (Vyjednávanie/Návrh) bez záväzku FLM',
            'Calculation': 'OPPORTUNITY_VALUE WHERE SALES_STAGE IN (Negotiate, Propose) AND FLM_JUDGEMENT_INDICATOR = FALSE',
            'Business_Use': 'Additional opportunities beyond committed pipeline',
            'Example_Values': '150000, 0, 300000',
            'Data_Type': 'Decimal',
            'Table_Source': 'PIPELINE'
        },
        {
            'Category': 'Financial - Pipeline Values',
            'Column': 'QUALIFY_PLUS_AMT',
            'Description': 'Advanced stage pipeline value - sum of opportunities in qualified stages',
            'Slovak_Description': 'Hodnota pipeline v pokročilých fázach - súčet príležitostí v kvalifikovaných štádiách',
            'Calculation': 'SUM(OPPORTUNITY_VALUE WHERE SALES_STAGE IN (Closing, Design, Negotiate, Propose, Qualify))',
            'Business_Use': 'Standard qualified pipeline health metric',
            'Example_Values': '2500000, 1800000, 900000',
            'Data_Type': 'Decimal',
            'Table_Source': 'PIPELINE'
        },
        {
            'Category': 'Financial - Pipeline Values',
            'Column': 'PPV_AMT',
            'Description': 'PERFORM Pipeline Value - AI-generated end-of-quarter revenue assessment by IBM Chief Analytics Office',
            'Slovak_Description': 'PERFORM Pipeline Value - AI-generované posúdenie príjmov na konci štvrťroka od IBM Chief Analytics Office',
            'Calculation': 'AI algorithm by CAO, updated weekly on Mondays',
            'Business_Use': 'Most accurate revenue prediction for forecasting',
            'Example_Values': '1200000, 890000, 450000',
            'Data_Type': 'Decimal',
            'Table_Source': 'PIPELINE'
        },
        {
            'Category': 'Financial - Pipeline Values',
            'Column': 'WON_AMT',
            'Description': 'Value of opportunities that have been closed and won',
            'Slovak_Description': 'Hodnota príležitostí, ktoré boli uzavreté a vyhrané',
            'Calculation': 'SUM(OPPORTUNITY_VALUE WHERE SALES_STAGE = Won)',
            'Business_Use': 'Actual achieved revenue tracking',
            'Example_Values': '500000, 0, 1200000',
            'Data_Type': 'Decimal',
            'Table_Source': 'PIPELINE'
        },
        
        # BUDGET & TARGETS
        {
            'Category': 'Financial - Budget & Targets',
            'Column': 'REVENUE_BUDGET_AMT',
            'Description': 'Revenue target/quota set by finance planning for specific geography/market/time period',
            'Slovak_Description': 'Cieľ príjmov/kvóta stanovená finančným plánovaním pre konkrétnu geografiu/trh/časové obdobie',
            'Calculation': 'Set by finance planning team',
            'Business_Use': 'Performance measurement baseline for sales teams',
            'Example_Values': '5000000, 2500000, 1200000',
            'Data_Type': 'Decimal',
            'Table_Source': 'BUDGET'
        },
        {
            'Category': 'Financial - Budget & Targets',
            'Column': 'SIGNINGS_BUDGET_AMT',
            'Description': 'Signings target/quota for new bookings and contract signings',
            'Slovak_Description': 'Cieľ podpisov/kvóta pre nové rezervácie a podpisy zmlúv',
            'Calculation': 'Set by finance planning team',
            'Business_Use': 'Bookings target for sales teams to measure new business acquisition',
            'Example_Values': '6000000, 3000000, 1500000',
            'Data_Type': 'Decimal',
            'Table_Source': 'BUDGET'
        },
        
        # TIME DIMENSIONS
        {
            'Category': 'Time Dimensions',
            'Column': 'YEAR',
            'Description': 'Calendar year for the data record',
            'Slovak_Description': 'Kalendárny rok pre záznam údajov',
            'Calculation': 'Calendar year',
            'Business_Use': 'Annual comparisons and year-over-year analysis',
            'Example_Values': '2024, 2025, 2026',
            'Data_Type': 'Integer',
            'Table_Source': 'ALL'
        },
        {
            'Category': 'Time Dimensions',
            'Column': 'QUARTER',
            'Description': 'Quarter number within the year (1-4)',
            'Slovak_Description': 'Číslo štvrťroka v rámci roka (1-4)',
            'Calculation': 'Quarter number',
            'Business_Use': 'Quarterly planning and performance tracking',
            'Example_Values': '1, 2, 3, 4',
            'Data_Type': 'Integer',
            'Table_Source': 'ALL'
        },
        {
            'Category': 'Time Dimensions',
            'Column': 'WEEK',
            'Description': 'Week number relative to quarter start (-13 to +13)',
            'Slovak_Description': 'Číslo týždňa relatívne k začiatku štvrťroka (-13 až +13)',
            'Calculation': 'Week offset from quarter start',
            'Business_Use': 'Weekly pipeline tracking and velocity management',
            'Example_Values': '-13, -1, 0, 1, 3, 13',
            'Data_Type': 'Integer',
            'Table_Source': 'PIPELINE'
        },
        {
            'Category': 'Time Dimensions',
            'Column': 'RELATIVE_QUARTER_MNEUMONIC',
            'Description': 'Quarter relative to current date - Current Quarter, Next Quarter, Previous Quarter',
            'Slovak_Description': 'Štvrťrok relatívny k aktuálnemu dátumu - Aktuálny štvrťrok, Ďalší štvrťrok, Predchádzajúci štvrťrok',
            'Calculation': 'Based on current date',
            'Business_Use': 'Time-relative filtering for reports',
            'Example_Values': 'CQ, NQ, PQ',
            'Data_Type': 'String',
            'Table_Source': 'PIPELINE'
        },
        
        # GEOGRAPHY & TERRITORY
        {
            'Category': 'Geography & Territory',
            'Column': 'GEOGRAPHY',
            'Description': 'Major geographic region for IBM sales operations',
            'Slovak_Description': 'Hlavná geografická oblasť pre predajné operácie IBM',
            'Calculation': 'Mapped from customer location',
            'Business_Use': 'Regional performance analysis and management',
            'Example_Values': 'Americas, EMEA, APAC',
            'Data_Type': 'String',
            'Table_Source': 'ALL'
        },
        {
            'Category': 'Geography & Territory',
            'Column': 'MARKET',
            'Description': 'Specific market segment within geography',
            'Slovak_Description': 'Špecifický trhový segment v rámci geografie',
            'Calculation': 'Market segmentation based on business rules',
            'Business_Use': 'Market-specific analysis and strategy development',
            'Example_Values': 'US Federal, UK Market, Japan Market, US Commercial',
            'Data_Type': 'String',
            'Table_Source': 'ALL'
        },
        {
            'Category': 'Geography & Territory',
            'Column': 'SECTOR',
            'Description': 'Industry sector classification for the customer',
            'Slovak_Description': 'Klasifikácia priemyselného sektora pre zákazníka',
            'Calculation': 'Industry classification mapping',
            'Business_Use': 'Vertical market performance tracking',
            'Example_Values': 'Financial, Government, Healthcare, Manufacturing',
            'Data_Type': 'String',
            'Table_Source': 'ALL'
        },
        
        # CLIENT & CUSTOMER
        {
            'Category': 'Client & Customer',
            'Column': 'CLIENT_NAME',
            'Description': 'Name of the customer/client organization',
            'Slovak_Description': 'Názov zákazníckej/klientskej organizácie',
            'Calculation': 'From CRM customer master record',
            'Business_Use': 'Client identification and relationship management',
            'Example_Values': 'Federal Agency A, Corp B, UK Corporation',
            'Data_Type': 'String',
            'Table_Source': 'ALL'
        },
        {
            'Category': 'Client & Customer',
            'Column': 'CLIENT_TYPE',
            'Description': 'Client segmentation category based on IBM GTM strategy',
            'Slovak_Description': 'Kategória segmentácie klientov na základe GTM stratégie IBM',
            'Calculation': 'Based on local coverage type and business rules',
            'Business_Use': 'Account strategy and resource allocation',
            'Example_Values': 'TARGET ENTERPRISE, ENTERPRISE, PREMIER',
            'Data_Type': 'String',
            'Table_Source': 'ALL'
        },
        {
            'Category': 'Client & Customer',
            'Column': 'INDUSTRY',
            'Description': 'Industry vertical classification of the customer',
            'Slovak_Description': 'Klasifikácia priemyselného vertikálu zákazníka',
            'Calculation': 'Industry mapping from customer data',
            'Business_Use': 'Vertical market analysis and specialization',
            'Example_Values': 'Government, Financial Services, Healthcare, Technology',
            'Data_Type': 'String',
            'Table_Source': 'ALL'
        },
        
        # PRODUCT & SERVICES
        {
            'Category': 'Product & Services',
            'Column': 'UT15_NAME',
            'Description': 'Unified Taxonomy Level 15 - Major service line grouping',
            'Slovak_Description': 'Unified Taxonomy Úroveň 15 - Hlavné zoskupenie servisných línií',
            'Calculation': 'From Fedcat taxonomy based on product selection',
            'Business_Use': 'Service line performance analysis',
            'Example_Values': 'Strategy & Technology, Intelligent Operations, Business Applications',
            'Data_Type': 'String',
            'Table_Source': 'ALL'
        },
        {
            'Category': 'Product & Services',
            'Column': 'UT17_NAME',
            'Description': 'Unified Taxonomy Level 17 - Detailed service category',
            'Slovak_Description': 'Unified Taxonomy Úroveň 17 - Podrobná kategória služieb',
            'Calculation': 'From Fedcat taxonomy hierarchy',
            'Business_Use': 'Specific service offering analysis',
            'Example_Values': 'Cybersecurity, Hybrid Cloud & Data, Strategy & Transformation',
            'Data_Type': 'String',
            'Table_Source': 'ALL'
        },
        {
            'Category': 'Product & Services',
            'Column': 'UT30_NAME',
            'Description': 'Unified Taxonomy Level 30 - Specific product/service offering',
            'Slovak_Description': 'Unified Taxonomy Úroveň 30 - Špecifická ponuka produktov/služieb',
            'Calculation': 'Most granular level from Fedcat taxonomy',
            'Business_Use': 'Detailed product tracking and analysis',
            'Example_Values': 'IBM Cyber Strategy and Risk, Application Migration Services',
            'Data_Type': 'String',
            'Table_Source': 'ALL'
        },
        {
            'Category': 'Product & Services',
            'Column': 'PRACTICE',
            'Description': 'Service practice area for consulting delivery',
            'Slovak_Description': 'Oblasť servisnej praxe pre konzultačné dodávky',
            'Calculation': 'Practice mapping from service offering',
            'Business_Use': 'Practice performance and resource management',
            'Example_Values': 'Cybersecurity, Cloud Advisory, AI & Analytics',
            'Data_Type': 'String',
            'Table_Source': 'CONSULTING'
        },
        
        # SALES PROCESS
        {
            'Category': 'Sales Process',
            'Column': 'SALES_STAGE',
            'Description': 'Current stage of the opportunity in the sales cycle',
            'Slovak_Description': 'Aktuálna fáza príležitosti v predajnom cykle',
            'Calculation': 'Updated by opportunity owner as deal progresses',
            'Business_Use': 'Pipeline management and conversion tracking',
            'Example_Values': 'Engage, Qualify, Propose, Negotiate, Closing, Won, Lost',
            'Data_Type': 'String',
            'Table_Source': 'PIPELINE'
        },
        {
            'Category': 'Sales Process',
            'Column': 'DEAL_SIZE',
            'Description': 'Categorization of deal size for resource allocation',
            'Slovak_Description': 'Kategorizácia veľkosti obchodu pre alokáciu zdrojov',
            'Calculation': 'Based on opportunity value thresholds',
            'Business_Use': 'Resource allocation and sales strategy',
            'Example_Values': 'small, medium, large',
            'Data_Type': 'String',
            'Table_Source': 'PIPELINE'
        },
        
        # AI & TECHNOLOGY INDICATORS
        {
            'Category': 'AI & Technology',
            'Column': 'IBM_GEN_AI_IND',
            'Description': 'Indicator if the opportunity involves IBM Generative AI solutions',
            'Slovak_Description': 'Indikátor, či príležitosť zahŕňa riešenia IBM Generative AI',
            'Calculation': 'Binary flag based on solution components',
            'Business_Use': 'AI solution tracking and performance analysis',
            'Example_Values': '0, 1',
            'Data_Type': 'Integer',
            'Table_Source': 'PIPELINE'
        },
        {
            'Category': 'AI & Technology',
            'Column': 'PARTNER_GEN_AI_IND',
            'Description': 'Indicator if the opportunity involves Partner Generative AI solutions',
            'Slovak_Description': 'Indikátor, či príležitosť zahŕňa partnerské riešenia Generative AI',
            'Calculation': 'Binary flag for partner AI involvement',
            'Business_Use': 'Ecosystem AI solution tracking',
            'Example_Values': '0, 1',
            'Data_Type': 'Integer',
            'Table_Source': 'PIPELINE'
        },
        
        # CALCULATED METRICS
        {
            'Category': 'Calculated Metrics',
            'Column': 'PPV_COVERAGE_PCT',
            'Description': 'Pipeline coverage percentage vs budget target',
            'Slovak_Description': 'Percentuálne pokrytie pipeline oproti rozpočtovému cieľu',
            'Calculation': '(PPV_AMT / REVENUE_BUDGET_AMT) * 100',
            'Business_Use': 'Measuring sales effectiveness and pipeline health',
            'Example_Values': '85.5, 120.0, 67.8',
            'Data_Type': 'Decimal',
            'Table_Source': 'CALCULATED'
        },
        {
            'Category': 'Calculated Metrics',
            'Column': 'MULTIPLIER',
            'Description': 'Pipeline coverage multiplier - how many times budget is covered by pipeline',
            'Slovak_Description': 'Násobiteľ pokrytia pipeline - koľkokrát je rozpočet pokrytý pipeline',
            'Calculation': 'QUALIFY_PLUS_AMT / REVENUE_BUDGET_AMT',
            'Business_Use': 'Pipeline health assessment (4x is recommended)',
            'Example_Values': '2.5, 4.2, 1.8',
            'Data_Type': 'Decimal',
            'Table_Source': 'CALCULATED'
        },
        {
            'Category': 'Calculated Metrics',
            'Column': 'YOY_GROWTH_PCT',
            'Description': 'Year-over-year growth percentage for any metric',
            'Slovak_Description': 'Percentuálny rast rok za rokom pre akýkoľvek ukazovateľ',
            'Calculation': '((Current_Year - Prior_Year) / Prior_Year) * 100',
            'Business_Use': 'Growth trend analysis and performance tracking',
            'Example_Values': '15.5, -8.2, 0.0',
            'Data_Type': 'Decimal',
            'Table_Source': 'CALCULATED'
        },
        
        # REVENUE ACTUALS
        {
            'Category': 'Financial - Revenue Actuals',
            'Column': 'REVENUE_AMT',
            'Description': 'Actual recognized revenue amount from financial systems',
            'Slovak_Description': 'Skutočná uznaná výška príjmov z finančných systémov',
            'Calculation': 'From financial/accounting systems',
            'Business_Use': 'Historical performance tracking and variance analysis',
            'Example_Values': '1250000, 890000, 2100000',
            'Data_Type': 'Decimal',
            'Table_Source': 'REVENUE_ACTUALS'
        },
        {
            'Category': 'Financial - Revenue Actuals',
            'Column': 'GROSS_PROFIT_AMT',
            'Description': 'Actual gross profit amount (revenue minus cost of goods sold)',
            'Slovak_Description': 'Skutočná výška hrubého zisku (príjmy mínus náklady na predané tovary)',
            'Calculation': 'REVENUE_AMT - COST_OF_GOODS_SOLD',
            'Business_Use': 'Profitability analysis and margin tracking',
            'Example_Values': '625000, 445000, 1050000',
            'Data_Type': 'Decimal',
            'Table_Source': 'REVENUE_ACTUALS'
        }
    ]
    
    # Create DataFrame
    df = pd.DataFrame(data_dict)
    
    # Create additional sheet with business context
    business_context = [
        {
            'Concept': 'Pipeline',
            'English_Definition': 'Sales pipeline represents all potential revenue opportunities that sales teams are actively pursuing. It includes deals in various stages from initial engagement to final closing.',
            'Slovak_Definition': 'Sales pipeline predstavuje všetky potenciálne príležitosti príjmov, ktoré predajné tímy aktívne sledujú. Zahŕňa obchody v rôznych fázach od počiatočného zapojenia až po konečné uzavretie.',
            'Business_Importance': 'Critical for revenue forecasting, resource planning, and performance management',
            'Key_Metrics': 'OPPORTUNITY_VALUE, PPV_AMT, QUALIFY_PLUS_AMT, CALL_AMT'
        },
        {
            'Concept': 'Budget/Quota',
            'English_Definition': 'Budget represents the revenue and profit targets set by finance and leadership for specific territories, time periods, and product lines. These serve as performance benchmarks.',
            'Slovak_Definition': 'Rozpočet predstavuje ciele príjmov a zisku stanovené financiami a vedením pre konkrétne územia, časové obdobia a produktové línie. Slúžia ako benchmarky výkonnosti.',
            'Business_Importance': 'Essential for goal setting, performance measurement, and compensation planning',
            'Key_Metrics': 'REVENUE_BUDGET_AMT, SIGNINGS_BUDGET_AMT, GROSS_PROFIT_BUDGET_AMT'
        },
        {
            'Concept': 'SaaS Tables',
            'English_Definition': 'Software-as-a-Service tables track subscription-based software sales, including recurring revenue, subscription terms, and customer lifecycle metrics.',
            'Slovak_Definition': 'SaaS tabuľky sledujú predaj softvéru na báze predplatného, vrátane opakujúcich sa príjmov, podmienok predplatného a metrík životného cyklu zákazníka.',
            'Business_Importance': 'Critical for subscription business model tracking and customer retention analysis',
            'Key_Metrics': 'Subscription revenue, annual contracts, customer retention rates'
        },
        {
            'Concept': 'PPV (PERFORM Pipeline Value)',
            'English_Definition': 'IBM proprietary AI-based algorithm that predicts end-of-quarter revenue by analyzing historical patterns, deal characteristics, and market conditions.',
            'Slovak_Definition': 'IBM proprietárny AI algoritmus, ktorý predpovedá príjmy na konci štvrťroka analýzou historických vzorov, charakteristík obchodov a trhových podmienok.',
            'Business_Importance': 'Most accurate revenue forecasting tool for strategic planning',
            'Key_Metrics': 'PPV_AMT, PPV_COVERAGE_PCT'
        },
        {
            'Concept': 'Unified Taxonomy (UT)',
            'English_Definition': 'Hierarchical product classification system used across IBM to categorize all products and services from high-level (UT10) to specific offerings (UT30).',
            'Slovak_Definition': 'Hierarchický systém klasifikácie produktov používaný v celom IBM na kategorizáciu všetkých produktov a služieb od vysokej úrovne (UT10) po špecifické ponuky (UT30).',
            'Business_Importance': 'Enables consistent product performance tracking and portfolio analysis',
            'Key_Metrics': 'UT15_NAME, UT17_NAME, UT20_NAME, UT30_NAME'
        },
        {
            'Concept': 'Sales Stages',
            'English_Definition': 'Standardized phases that opportunities progress through: Engage → Design → Qualify → Propose → Negotiate → Closing → Won/Lost',
            'Slovak_Definition': 'Štandardizované fázy, ktorými prechádzajú príležitosti: Engage → Design → Qualify → Propose → Negotiate → Closing → Won/Lost',
            'Business_Importance': 'Essential for pipeline management, conversion tracking, and process optimization',
            'Key_Metrics': 'SALES_STAGE, conversion rates between stages'
        }
    ]
    
    # Create business context DataFrame
    context_df = pd.DataFrame(business_context)
    
    # Create Excel file with multiple sheets
    filename = f'/Volumes/DATA/Python/IBM_analyza/IBM_Sales_Pipeline_Data_Dictionary_{datetime.now().strftime("%Y%m%d")}.xlsx'
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Main data dictionary
        df.to_excel(writer, sheet_name='Data Dictionary', index=False)
        
        # Business context
        context_df.to_excel(writer, sheet_name='Business Context', index=False)
        
        # Summary statistics
        summary_stats = [
            {'Metric': 'Total Columns Documented', 'Count': len(df)},
            {'Metric': 'Categories Covered', 'Count': df['Category'].nunique()},
            {'Metric': 'Financial Metrics', 'Count': len(df[df['Category'].str.contains('Financial')])},
            {'Metric': 'Time Dimensions', 'Count': len(df[df['Category'] == 'Time Dimensions'])},
            {'Metric': 'Geographic Fields', 'Count': len(df[df['Category'] == 'Geography & Territory'])},
            {'Metric': 'Product Fields', 'Count': len(df[df['Category'] == 'Product & Services'])},
        ]
        summary_df = pd.DataFrame(summary_stats)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Column categories breakdown
        category_breakdown = df['Category'].value_counts().reset_index()
        category_breakdown.columns = ['Category', 'Column_Count']
        category_breakdown.to_excel(writer, sheet_name='Categories', index=False)
    
    return filename

if __name__ == "__main__":
    filename = create_excel_dictionary()
    print(f"✅ Excel data dictionary created: {filename}")
    print("📊 Sheets included:")
    print("   - Data Dictionary: Complete column reference")
    print("   - Business Context: Pipeline, Budget, SaaS explanations")
    print("   - Summary: Statistics and overview")
    print("   - Categories: Column breakdown by category")