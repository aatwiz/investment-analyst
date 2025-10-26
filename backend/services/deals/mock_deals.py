"""
Mock deal data for MVP - Based on real startup profiles
This replaces web scraping until the scraping infrastructure is ready
"""

from datetime import datetime, timedelta
import random

# Generate realistic dates
def random_date_recent(days_back=90):
    """Generate a random date within the last N days"""
    days = random.randint(0, days_back)
    return (datetime.now() - timedelta(days=days)).isoformat()

# Mock deals based on real startup data
MOCK_DEALS = [
    {
        "id": "deal_001",
        "company_name": "Anthropic",
        "description": "AI safety and research company developing Claude, a next-generation AI assistant focused on helpfulness, harmlessness, and honesty.",
        "industry": "Artificial Intelligence",
        "stage": "Series C",
        "funding_amount": 450000000,
        "valuation": 4500000000,
        "location": "San Francisco, CA",
        "founded_year": 2021,
        "founders": ["Dario Amodei", "Daniela Amodei"],
        "employees": "150-200",
        "website": "https://anthropic.com",
        "revenue_arr": 50000000,
        "growth_rate": 400,
        "burn_rate": 8000000,
        "runway_months": 56,
        "technology": ["Large Language Models", "AI Safety", "Constitutional AI"],
        "customers": ["Fortune 500 companies", "Research institutions"],
        "metrics": {
            "user_growth": "350% YoY",
            "retention_rate": "92%",
            "nrr": "135%"
        },
        "source": "Crunchbase",
        "last_updated": random_date_recent(30),
        "contact_email": "partnerships@anthropic.com"
    },
    {
        "id": "deal_002",
        "company_name": "Databricks",
        "description": "Unified analytics platform built on Apache Spark, providing data engineering, data science, and machine learning capabilities.",
        "industry": "Data Analytics",
        "stage": "Series I",
        "funding_amount": 500000000,
        "valuation": 43000000000,
        "location": "San Francisco, CA",
        "founded_year": 2013,
        "founders": ["Ali Ghodsi", "Matei Zaharia", "Reynold Xin"],
        "employees": "5000+",
        "website": "https://databricks.com",
        "revenue_arr": 1500000000,
        "growth_rate": 75,
        "burn_rate": 15000000,
        "runway_months": 33,
        "technology": ["Apache Spark", "Delta Lake", "MLflow", "Lakehouse Architecture"],
        "customers": ["Shell", "Comcast", "H&M", "Regeneron"],
        "metrics": {
            "user_growth": "80% YoY",
            "retention_rate": "98%",
            "nrr": "160%"
        },
        "source": "PitchBook",
        "last_updated": random_date_recent(45),
        "contact_email": "sales@databricks.com"
    },
    {
        "id": "deal_003",
        "company_name": "Scale AI",
        "description": "Data platform for AI, providing high-quality training data for machine learning applications.",
        "industry": "Machine Learning Infrastructure",
        "stage": "Series E",
        "funding_amount": 325000000,
        "valuation": 7300000000,
        "location": "San Francisco, CA",
        "founded_year": 2016,
        "founders": ["Alexandr Wang", "Lucy Guo"],
        "employees": "800-1000",
        "website": "https://scale.com",
        "revenue_arr": 500000000,
        "growth_rate": 120,
        "burn_rate": 12000000,
        "runway_months": 27,
        "technology": ["Data Labeling", "Computer Vision", "NLP", "Sensor Fusion"],
        "customers": ["OpenAI", "Microsoft", "US Department of Defense"],
        "metrics": {
            "user_growth": "130% YoY",
            "retention_rate": "95%",
            "nrr": "140%"
        },
        "source": "AngelList",
        "last_updated": random_date_recent(20),
        "contact_email": "hello@scale.com"
    },
    {
        "id": "deal_004",
        "company_name": "Notion",
        "description": "All-in-one workspace for notes, tasks, wikis, and databases. Combines note-taking with project management.",
        "industry": "Productivity Software",
        "stage": "Series C",
        "funding_amount": 275000000,
        "valuation": 10000000000,
        "location": "San Francisco, CA",
        "founded_year": 2016,
        "founders": ["Ivan Zhao", "Simon Last"],
        "employees": "400-500",
        "website": "https://notion.so",
        "revenue_arr": 300000000,
        "growth_rate": 150,
        "burn_rate": 6000000,
        "runway_months": 45,
        "technology": ["Collaborative Editing", "Block-based Editor", "API Platform"],
        "customers": ["Figma", "Pixar", "Nike", "Toyota"],
        "metrics": {
            "user_growth": "180% YoY",
            "retention_rate": "88%",
            "nrr": "125%",
            "users": "30M+"
        },
        "source": "Crunchbase",
        "last_updated": random_date_recent(60),
        "contact_email": "team@makenotion.com"
    },
    {
        "id": "deal_005",
        "company_name": "Ramp",
        "description": "Corporate card and spend management platform that helps companies save money and time.",
        "industry": "FinTech",
        "stage": "Series D",
        "funding_amount": 750000000,
        "valuation": 8100000000,
        "location": "New York, NY",
        "founded_year": 2019,
        "founders": ["Eric Glyman", "Karim Atiyeh", "Gene Lee"],
        "employees": "600-700",
        "website": "https://ramp.com",
        "revenue_arr": 200000000,
        "growth_rate": 300,
        "burn_rate": 10000000,
        "runway_months": 75,
        "technology": ["Expense Management", "Corporate Cards", "Financial Automation"],
        "customers": ["Shopify", "Anduril", "Barry's", "Crossbeam"],
        "metrics": {
            "user_growth": "400% YoY",
            "retention_rate": "96%",
            "nrr": "150%",
            "savings_per_customer": "$200K/year"
        },
        "source": "PitchBook",
        "last_updated": random_date_recent(15),
        "contact_email": "sales@ramp.com"
    },
    {
        "id": "deal_006",
        "company_name": "Brex",
        "description": "Financial services platform for startups and enterprises, offering corporate cards and cash management.",
        "industry": "FinTech",
        "stage": "Series D",
        "funding_amount": 425000000,
        "valuation": 12300000000,
        "location": "San Francisco, CA",
        "founded_year": 2017,
        "founders": ["Henrique Dubugras", "Pedro Franceschi"],
        "employees": "1200+",
        "website": "https://brex.com",
        "revenue_arr": 350000000,
        "growth_rate": 180,
        "burn_rate": 15000000,
        "runway_months": 28,
        "technology": ["Embedded Finance", "Expense Management", "Banking APIs"],
        "customers": ["DoorDash", "Robinhood", "Flexport"],
        "metrics": {
            "user_growth": "200% YoY",
            "retention_rate": "94%",
            "nrr": "145%"
        },
        "source": "AngelList",
        "last_updated": random_date_recent(25),
        "contact_email": "hello@brex.com"
    },
    {
        "id": "deal_007",
        "company_name": "Rippling",
        "description": "Workforce management platform handling HR, IT, and Finance operations in one system.",
        "industry": "HR Tech",
        "stage": "Series D",
        "funding_amount": 500000000,
        "valuation": 11250000000,
        "location": "San Francisco, CA",
        "founded_year": 2016,
        "founders": ["Parker Conrad", "Prasanna Sankar"],
        "employees": "2000+",
        "website": "https://rippling.com",
        "revenue_arr": 400000000,
        "growth_rate": 200,
        "burn_rate": 12000000,
        "runway_months": 41,
        "technology": ["Unified Employee Systems", "Workflow Automation", "Global Payroll"],
        "customers": ["Carta", "Loom", "Superhuman"],
        "metrics": {
            "user_growth": "250% YoY",
            "retention_rate": "97%",
            "nrr": "155%"
        },
        "source": "Crunchbase",
        "last_updated": random_date_recent(35),
        "contact_email": "hello@rippling.com"
    },
    {
        "id": "deal_008",
        "company_name": "Anduril Industries",
        "description": "Defense technology company creating autonomous systems for national security.",
        "industry": "Defense Tech",
        "stage": "Series E",
        "funding_amount": 1500000000,
        "valuation": 8500000000,
        "location": "Costa Mesa, CA",
        "founded_year": 2017,
        "founders": ["Palmer Luckey", "Trae Stephens", "Matt Grimm"],
        "employees": "1500+",
        "website": "https://anduril.com",
        "revenue_arr": 500000000,
        "growth_rate": 250,
        "burn_rate": 25000000,
        "runway_months": 60,
        "technology": ["Autonomous Vehicles", "AI", "Sensor Fusion", "Command & Control"],
        "customers": ["US Department of Defense", "UK Ministry of Defence"],
        "metrics": {
            "user_growth": "300% YoY",
            "retention_rate": "100%",
            "contract_value": "$1B+ pipeline"
        },
        "source": "PitchBook",
        "last_updated": random_date_recent(40),
        "contact_email": "info@anduril.com"
    },
    {
        "id": "deal_009",
        "company_name": "Faire",
        "description": "Online wholesale marketplace connecting independent retailers with brands.",
        "industry": "E-commerce",
        "stage": "Series G",
        "funding_amount": 400000000,
        "valuation": 12600000000,
        "location": "San Francisco, CA",
        "founded_year": 2017,
        "founders": ["Max Rhodes", "Marcelo Cortes", "Daniele Perito", "Jeffrey Kolovson"],
        "employees": "1000+",
        "website": "https://faire.com",
        "revenue_arr": 600000000,
        "growth_rate": 140,
        "burn_rate": 18000000,
        "runway_months": 22,
        "technology": ["Marketplace Platform", "Inventory Management", "Payment Solutions"],
        "customers": ["65,000+ retailers", "100,000+ brands"],
        "metrics": {
            "user_growth": "160% YoY",
            "retention_rate": "85%",
            "gmv": "$15B annual"
        },
        "source": "AngelList",
        "last_updated": random_date_recent(50),
        "contact_email": "hello@faire.com"
    },
    {
        "id": "deal_010",
        "company_name": "Figma",
        "description": "Collaborative interface design tool (acquired by Adobe for $20B, deal under review).",
        "industry": "Design Software",
        "stage": "Series E",
        "funding_amount": 200000000,
        "valuation": 20000000000,
        "location": "San Francisco, CA",
        "founded_year": 2012,
        "founders": ["Dylan Field", "Evan Wallace"],
        "employees": "800+",
        "website": "https://figma.com",
        "revenue_arr": 400000000,
        "growth_rate": 100,
        "burn_rate": 5000000,
        "runway_months": 40,
        "technology": ["WebGL", "Collaborative Editing", "Vector Graphics"],
        "customers": ["Microsoft", "Uber", "Airbnb", "Twitter"],
        "metrics": {
            "user_growth": "120% YoY",
            "retention_rate": "99%",
            "users": "4M+"
        },
        "source": "Crunchbase",
        "last_updated": random_date_recent(70),
        "contact_email": "hello@figma.com"
    },
    {
        "id": "deal_011",
        "company_name": "Webflow",
        "description": "Visual web development platform enabling designers to build production-ready websites without code.",
        "industry": "Web Development",
        "stage": "Series C",
        "funding_amount": 140000000,
        "valuation": 4000000000,
        "location": "San Francisco, CA",
        "founded_year": 2013,
        "founders": ["Vlad Magdalin", "Sergie Magdalin", "Bryant Chou"],
        "employees": "700+",
        "website": "https://webflow.com",
        "revenue_arr": 200000000,
        "growth_rate": 120,
        "burn_rate": 8000000,
        "runway_months": 17,
        "technology": ["Visual Development", "CMS", "E-commerce Platform"],
        "customers": ["Dell", "Discord", "Zendesk", "NCAA"],
        "metrics": {
            "user_growth": "150% YoY",
            "retention_rate": "90%",
            "sites_hosted": "3.5M+"
        },
        "source": "PitchBook",
        "last_updated": random_date_recent(55),
        "contact_email": "hello@webflow.com"
    },
    {
        "id": "deal_012",
        "company_name": "Plaid",
        "description": "Financial services API platform connecting applications to users' bank accounts.",
        "industry": "FinTech Infrastructure",
        "stage": "Series D",
        "funding_amount": 425000000,
        "valuation": 13400000000,
        "location": "San Francisco, CA",
        "founded_year": 2013,
        "founders": ["Zach Perret", "William Hockey"],
        "employees": "800+",
        "website": "https://plaid.com",
        "revenue_arr": 450000000,
        "growth_rate": 90,
        "burn_rate": 12000000,
        "runway_months": 35,
        "technology": ["Banking APIs", "Identity Verification", "Payment Initiation"],
        "customers": ["Venmo", "Coinbase", "Robinhood", "Acorns"],
        "metrics": {
            "user_growth": "100% YoY",
            "retention_rate": "98%",
            "api_calls": "6B+ monthly"
        },
        "source": "AngelList",
        "last_updated": random_date_recent(65),
        "contact_email": "hello@plaid.com"
    },
    {
        "id": "deal_013",
        "company_name": "Superhuman",
        "description": "Blazingly fast email client designed for high-performing teams and individuals.",
        "industry": "Productivity Software",
        "stage": "Series C",
        "funding_amount": 75000000,
        "valuation": 825000000,
        "location": "San Francisco, CA",
        "founded_year": 2014,
        "founders": ["Rahul Vohra", "Conrad Irwin"],
        "employees": "100-150",
        "website": "https://superhuman.com",
        "revenue_arr": 35000000,
        "growth_rate": 180,
        "burn_rate": 3000000,
        "runway_months": 25,
        "technology": ["Email Client", "AI-powered Features", "Keyboard Shortcuts"],
        "customers": ["Venture Capitalists", "Founders", "Executives"],
        "metrics": {
            "user_growth": "200% YoY",
            "retention_rate": "92%",
            "nps": "80+",
            "price": "$30/month"
        },
        "source": "Crunchbase",
        "last_updated": random_date_recent(45),
        "contact_email": "hello@superhuman.com"
    },
    {
        "id": "deal_014",
        "company_name": "Retool",
        "description": "Low-code platform for building internal tools and business applications quickly.",
        "industry": "Developer Tools",
        "stage": "Series C",
        "funding_amount": 145000000,
        "valuation": 3200000000,
        "location": "San Francisco, CA",
        "founded_year": 2017,
        "founders": ["David Hsu"],
        "employees": "300-400",
        "website": "https://retool.com",
        "revenue_arr": 120000000,
        "growth_rate": 150,
        "burn_rate": 6000000,
        "runway_months": 24,
        "technology": ["Low-code Platform", "Database Integrations", "Component Library"],
        "customers": ["Amazon", "Mercedes-Benz", "Peloton", "DoorDash"],
        "metrics": {
            "user_growth": "180% YoY",
            "retention_rate": "95%",
            "time_savings": "90% faster development"
        },
        "source": "PitchBook",
        "last_updated": random_date_recent(30),
        "contact_email": "hello@retool.com"
    },
    {
        "id": "deal_015",
        "company_name": "Airtable",
        "description": "Collaborative work management platform combining spreadsheet and database capabilities.",
        "industry": "Productivity Software",
        "stage": "Series F",
        "funding_amount": 735000000,
        "valuation": 11000000000,
        "location": "San Francisco, CA",
        "founded_year": 2012,
        "founders": ["Howie Liu", "Andrew Ofstad", "Emmett Nicholas"],
        "employees": "1000+",
        "website": "https://airtable.com",
        "revenue_arr": 400000000,
        "growth_rate": 110,
        "burn_rate": 15000000,
        "runway_months": 49,
        "technology": ["No-code Platform", "Relational Database", "API", "Automations"],
        "customers": ["Netflix", "Expedia", "Medium", "Time Inc."],
        "metrics": {
            "user_growth": "130% YoY",
            "retention_rate": "93%",
            "users": "300,000+ organizations"
        },
        "source": "AngelList",
        "last_updated": random_date_recent(80),
        "contact_email": "support@airtable.com"
    },
    {
        "id": "deal_016",
        "company_name": "Deel",
        "description": "Global payroll and compliance platform for remote teams and international hiring.",
        "industry": "HR Tech",
        "stage": "Series D",
        "funding_amount": 425000000,
        "valuation": 12000000000,
        "location": "San Francisco, CA",
        "founded_year": 2019,
        "founders": ["Alex Bouaziz", "Shuo Wang"],
        "employees": "2000+",
        "website": "https://deel.com",
        "revenue_arr": 500000000,
        "growth_rate": 450,
        "burn_rate": 18000000,
        "runway_months": 23,
        "technology": ["Global Payroll", "Compliance Automation", "Contractor Management"],
        "customers": ["Shopify", "Nike", "Dropbox", "Airtable"],
        "metrics": {
            "user_growth": "500% YoY",
            "retention_rate": "95%",
            "countries": "150+",
            "users": "20,000+ companies"
        },
        "source": "Crunchbase",
        "last_updated": random_date_recent(20),
        "contact_email": "hello@deel.com"
    },
    {
        "id": "deal_017",
        "company_name": "Vercel",
        "description": "Frontend cloud platform for building and deploying web applications with Next.js.",
        "industry": "Developer Tools",
        "stage": "Series D",
        "funding_amount": 150000000,
        "valuation": 2500000000,
        "location": "San Francisco, CA",
        "founded_year": 2015,
        "founders": ["Guillermo Rauch"],
        "employees": "300-400",
        "website": "https://vercel.com",
        "revenue_arr": 100000000,
        "growth_rate": 200,
        "burn_rate": 7000000,
        "runway_months": 21,
        "technology": ["Next.js", "Edge Functions", "Serverless", "CDN"],
        "customers": ["OpenAI", "HashiCorp", "TikTok", "Under Armour"],
        "metrics": {
            "user_growth": "250% YoY",
            "retention_rate": "94%",
            "deployments": "10M+ weekly"
        },
        "source": "PitchBook",
        "last_updated": random_date_recent(40),
        "contact_email": "sales@vercel.com"
    },
    {
        "id": "deal_018",
        "company_name": "Sourcegraph",
        "description": "Code intelligence platform enabling developers to search, understand, and update code.",
        "industry": "Developer Tools",
        "stage": "Series D",
        "funding_amount": 225000000,
        "valuation": 2625000000,
        "location": "San Francisco, CA",
        "founded_year": 2013,
        "founders": ["Quinn Slack", "Beyang Liu"],
        "employees": "300+",
        "website": "https://sourcegraph.com",
        "revenue_arr": 50000000,
        "growth_rate": 160,
        "burn_rate": 8000000,
        "runway_months": 28,
        "technology": ["Code Search", "Code Intelligence", "Batch Changes", "Code Insights"],
        "customers": ["Uber", "Lyft", "Yelp", "Reddit"],
        "metrics": {
            "user_growth": "180% YoY",
            "retention_rate": "96%",
            "time_saved": "10 hours/dev/month"
        },
        "source": "AngelList",
        "last_updated": random_date_recent(35),
        "contact_email": "hi@sourcegraph.com"
    },
    {
        "id": "deal_019",
        "company_name": "Census",
        "description": "Operational analytics platform syncing data from warehouses to business tools.",
        "industry": "Data Infrastructure",
        "stage": "Series B",
        "funding_amount": 85000000,
        "valuation": 1000000000,
        "location": "San Francisco, CA",
        "founded_year": 2018,
        "founders": ["Boris Jabes", "Brad Miro"],
        "employees": "150-200",
        "website": "https://getcensus.com",
        "revenue_arr": 30000000,
        "growth_rate": 220,
        "burn_rate": 4000000,
        "runway_months": 21,
        "technology": ["Reverse ETL", "Data Activation", "API Integrations"],
        "customers": ["Canva", "Notion", "Clearbit", "Loom"],
        "metrics": {
            "user_growth": "280% YoY",
            "retention_rate": "93%",
            "syncs": "1B+ records monthly"
        },
        "source": "Crunchbase",
        "last_updated": random_date_recent(25),
        "contact_email": "hello@getcensus.com"
    },
    {
        "id": "deal_020",
        "company_name": "Runway",
        "description": "AI video generation platform for content creators and filmmakers.",
        "industry": "Artificial Intelligence",
        "stage": "Series D",
        "funding_amount": 141000000,
        "valuation": 1500000000,
        "location": "New York, NY",
        "founded_year": 2018,
        "founders": ["Cristóbal Valenzuela", "Alejandro Matamala", "Anastasis Germanidis"],
        "employees": "100-150",
        "website": "https://runwayml.com",
        "revenue_arr": 40000000,
        "growth_rate": 350,
        "burn_rate": 6000000,
        "runway_months": 23,
        "technology": ["Generative AI", "Video Synthesis", "Image Generation", "AI Models"],
        "customers": ["Content Creators", "Film Studios", "Marketing Agencies"],
        "metrics": {
            "user_growth": "400% YoY",
            "retention_rate": "87%",
            "videos_generated": "10M+"
        },
        "source": "PitchBook",
        "last_updated": random_date_recent(15),
        "contact_email": "hello@runwayml.com"
    },
    {
        "id": "deal_021",
        "company_name": "Hex",
        "description": "Collaborative data workspace for analysts, engineers, and business users.",
        "industry": "Data Analytics",
        "stage": "Series B",
        "funding_amount": 52000000,
        "valuation": 600000000,
        "location": "San Francisco, CA",
        "founded_year": 2019,
        "founders": ["Barry McCardel", "Glen Coates"],
        "employees": "100-150",
        "website": "https://hex.tech",
        "revenue_arr": 20000000,
        "growth_rate": 280,
        "burn_rate": 3000000,
        "runway_months": 17,
        "technology": ["Notebook Environment", "SQL", "Python", "Data Apps"],
        "customers": ["BuzzFeed", "Anthropic", "Lucid", "Clearbit"],
        "metrics": {
            "user_growth": "320% YoY",
            "retention_rate": "91%",
            "queries": "100M+ monthly"
        },
        "source": "AngelList",
        "last_updated": random_date_recent(30),
        "contact_email": "hello@hex.tech"
    },
    {
        "id": "deal_022",
        "company_name": "Temporal",
        "description": "Open-source workflow orchestration platform for building reliable distributed applications.",
        "industry": "Developer Tools",
        "stage": "Series B",
        "funding_amount": 103000000,
        "valuation": 1500000000,
        "location": "Seattle, WA",
        "founded_year": 2019,
        "founders": ["Maxim Fateev", "Samar Abbas"],
        "employees": "150-200",
        "website": "https://temporal.io",
        "revenue_arr": 35000000,
        "growth_rate": 190,
        "burn_rate": 5000000,
        "runway_months": 20,
        "technology": ["Workflow Engine", "Distributed Systems", "Microservices"],
        "customers": ["Netflix", "Snap", "Stripe", "Coinbase"],
        "metrics": {
            "user_growth": "230% YoY",
            "retention_rate": "97%",
            "workflows": "1B+ executions"
        },
        "source": "Crunchbase",
        "last_updated": random_date_recent(50),
        "contact_email": "hello@temporal.io"
    },
    {
        "id": "deal_023",
        "company_name": "Clearbit",
        "description": "Marketing data engine providing real-time B2B intelligence and enrichment.",
        "industry": "Marketing Tech",
        "stage": "Series C",
        "funding_amount": 100000000,
        "valuation": 1200000000,
        "location": "San Francisco, CA",
        "founded_year": 2015,
        "founders": ["Alex MacCaw", "Matt Sornson"],
        "employees": "200-250",
        "website": "https://clearbit.com",
        "revenue_arr": 80000000,
        "growth_rate": 140,
        "burn_rate": 6000000,
        "runway_months": 16,
        "technology": ["Data Enrichment", "Lead Scoring", "Company Intelligence"],
        "customers": ["Segment", "Stripe", "Asana", "MongoDB"],
        "metrics": {
            "user_growth": "160% YoY",
            "retention_rate": "94%",
            "data_points": "100+ per company"
        },
        "source": "PitchBook",
        "last_updated": random_date_recent(60),
        "contact_email": "hello@clearbit.com"
    },
    {
        "id": "deal_024",
        "company_name": "Mux",
        "description": "Video infrastructure platform for developers to build video streaming applications.",
        "industry": "Developer Tools",
        "stage": "Series C",
        "funding_amount": 105000000,
        "valuation": 1050000000,
        "location": "San Francisco, CA",
        "founded_year": 2016,
        "founders": ["Jon Dahl", "Matt McClure", "Adam Brown"],
        "employees": "150-200",
        "website": "https://mux.com",
        "revenue_arr": 60000000,
        "growth_rate": 170,
        "burn_rate": 5000000,
        "runway_months": 21,
        "technology": ["Video API", "Live Streaming", "Video Analytics", "CDN"],
        "customers": ["PBS", "Vimeo", "Coursera", "Equinox"],
        "metrics": {
            "user_growth": "200% YoY",
            "retention_rate": "95%",
            "video_hours": "1B+ monthly"
        },
        "source": "AngelList",
        "last_updated": random_date_recent(40),
        "contact_email": "hello@mux.com"
    },
    {
        "id": "deal_025",
        "company_name": "Hightouch",
        "description": "Data activation platform syncing customer data from warehouses to business tools.",
        "industry": "Data Infrastructure",
        "stage": "Series B",
        "funding_amount": 54000000,
        "valuation": 800000000,
        "location": "San Francisco, CA",
        "founded_year": 2018,
        "founders": ["Kashish Gupta", "Tejas Manohar"],
        "employees": "100-150",
        "website": "https://hightouch.com",
        "revenue_arr": 25000000,
        "growth_rate": 250,
        "burn_rate": 3500000,
        "runway_months": 15,
        "technology": ["Reverse ETL", "Customer Data Platform", "Data Sync"],
        "customers": ["Spotify", "NBA", "Plaid", "PetSmart"],
        "metrics": {
            "user_growth": "300% YoY",
            "retention_rate": "92%",
            "integrations": "125+"
        },
        "source": "Crunchbase",
        "last_updated": random_date_recent(35),
        "contact_email": "hello@hightouch.com"
    },
    {
        "id": "deal_026",
        "company_name": "Loom",
        "description": "Async video messaging platform for work communication and collaboration.",
        "industry": "Productivity Software",
        "stage": "Series C",
        "funding_amount": 203000000,
        "valuation": 1530000000,
        "location": "San Francisco, CA",
        "founded_year": 2015,
        "founders": ["Joe Thomas", "Vinay Hiremath", "Shahed Khan"],
        "employees": "300-400",
        "website": "https://loom.com",
        "revenue_arr": 100000000,
        "growth_rate": 180,
        "burn_rate": 8000000,
        "runway_months": 25,
        "technology": ["Screen Recording", "Video Messaging", "Transcription", "AI"],
        "customers": ["HubSpot", "Atlassian", "Brex", "LaunchDarkly"],
        "metrics": {
            "user_growth": "220% YoY",
            "retention_rate": "89%",
            "videos_created": "200M+",
            "users": "21M+"
        },
        "source": "PitchBook",
        "last_updated": random_date_recent(55),
        "contact_email": "hello@loom.com"
    },
    {
        "id": "deal_027",
        "company_name": "Linear",
        "description": "Issue tracking tool built for modern software teams with speed and design.",
        "industry": "Developer Tools",
        "stage": "Series B",
        "funding_amount": 52000000,
        "valuation": 550000000,
        "location": "San Francisco, CA",
        "founded_year": 2019,
        "founders": ["Karri Saarinen", "Tuomas Artman", "Jori Lallo"],
        "employees": "50-75",
        "website": "https://linear.app",
        "revenue_arr": 30000000,
        "growth_rate": 200,
        "burn_rate": 2500000,
        "runway_months": 20,
        "technology": ["Issue Tracking", "Project Management", "Keyboard-first UI"],
        "customers": ["Vercel", "Ramp", "Cash App", "Zapier"],
        "metrics": {
            "user_growth": "280% YoY",
            "retention_rate": "96%",
            "nps": "78",
            "teams": "10,000+"
        },
        "source": "AngelList",
        "last_updated": random_date_recent(45),
        "contact_email": "hello@linear.app"
    },
    {
        "id": "deal_028",
        "company_name": "Cal.com",
        "description": "Open-source scheduling platform as alternative to Calendly.",
        "industry": "Productivity Software",
        "stage": "Series A",
        "funding_amount": 25000000,
        "valuation": 250000000,
        "location": "Remote",
        "founded_year": 2021,
        "founders": ["Bailey Pumfleet", "Peer Richelsen", "Ciarán Hanrahan"],
        "employees": "30-50",
        "website": "https://cal.com",
        "revenue_arr": 8000000,
        "growth_rate": 400,
        "burn_rate": 1500000,
        "runway_months": 16,
        "technology": ["Open Source", "Calendar Scheduling", "Integrations", "APIs"],
        "customers": ["Vercel", "Supabase", "GitLab", "Remote"],
        "metrics": {
            "user_growth": "500% YoY",
            "retention_rate": "88%",
            "bookings": "10M+",
            "github_stars": "25,000+"
        },
        "source": "Crunchbase",
        "last_updated": random_date_recent(20),
        "contact_email": "hello@cal.com"
    },
    {
        "id": "deal_029",
        "company_name": "Sweep",
        "description": "AI-powered code assistant that turns GitHub issues into pull requests.",
        "industry": "Developer Tools",
        "stage": "Seed",
        "funding_amount": 5000000,
        "valuation": 40000000,
        "location": "San Francisco, CA",
        "founded_year": 2023,
        "founders": ["William Zeng", "Kevin Lu"],
        "employees": "10-15",
        "website": "https://sweep.dev",
        "revenue_arr": 1200000,
        "growth_rate": 600,
        "burn_rate": 400000,
        "runway_months": 12,
        "technology": ["Large Language Models", "Code Generation", "GitHub Integration"],
        "customers": ["Early-stage startups", "Developer tools companies"],
        "metrics": {
            "user_growth": "800% YoY",
            "retention_rate": "85%",
            "prs_generated": "50,000+",
            "github_stars": "6,000+"
        },
        "source": "Y Combinator",
        "last_updated": random_date_recent(10),
        "contact_email": "founders@sweep.dev"
    },
    {
        "id": "deal_030",
        "company_name": "Mintlify",
        "description": "AI-powered documentation platform that automatically generates and maintains code docs.",
        "industry": "Developer Tools",
        "stage": "Series A",
        "funding_amount": 14000000,
        "valuation": 100000000,
        "location": "San Francisco, CA",
        "founded_year": 2021,
        "founders": ["Han Wang", "Hahnbee Lee"],
        "employees": "20-30",
        "website": "https://mintlify.com",
        "revenue_arr": 5000000,
        "growth_rate": 450,
        "burn_rate": 800000,
        "runway_months": 17,
        "technology": ["AI Documentation", "MDX", "API Reference", "Search"],
        "customers": ["Anthropic", "Ramp", "Vanta", "Merge"],
        "metrics": {
            "user_growth": "550% YoY",
            "retention_rate": "90%",
            "docs_hosted": "5,000+",
            "search_queries": "10M+ monthly"
        },
        "source": "Y Combinator",
        "last_updated": random_date_recent(15),
        "contact_email": "hello@mintlify.com"
    }
]

def get_mock_deals(industry=None, stage=None, min_funding=None, location=None, limit=30):
    """
    Get filtered mock deals
    
    Args:
        industry: Filter by industry
        stage: Filter by funding stage
        min_funding: Minimum funding amount
        location: Filter by location
        limit: Maximum number of deals to return
    
    Returns:
        List of filtered deals
    """
    filtered_deals = MOCK_DEALS.copy()
    
    # Apply filters
    if industry:
        filtered_deals = [d for d in filtered_deals if industry.lower() in d['industry'].lower()]
    
    if stage:
        filtered_deals = [d for d in filtered_deals if stage.lower() in d['stage'].lower()]
    
    if min_funding:
        filtered_deals = [d for d in filtered_deals if d['funding_amount'] >= min_funding]
    
    if location:
        filtered_deals = [d for d in filtered_deals if location.lower() in d['location'].lower()]
    
    # Add 'name' field for compatibility with deal sourcing manager
    for deal in filtered_deals:
        if 'name' not in deal:
            deal['name'] = deal['company_name']
    
    # Return limited results
    return filtered_deals[:limit]

def get_deal_by_id(deal_id):
    """Get a specific deal by ID"""
    for deal in MOCK_DEALS:
        if deal['id'] == deal_id:
            return deal
    return None

def get_qualified_mock_deals(min_score=70):
    """
    Get mock deals with simulated qualification scores
    
    Args:
        min_score: Minimum qualification score
    
    Returns:
        List of deals with qualification data
    """
    qualified_deals = []
    
    for deal in MOCK_DEALS:
        # Simulate qualification score based on metrics
        score = calculate_mock_score(deal)
        
        if score >= min_score:
            qualified_deal = deal.copy()
            qualified_deal['qualification_score'] = score
            qualified_deal['recommendation'] = get_recommendation(score)
            qualified_deal['qualified_at'] = datetime.now().isoformat()
            qualified_deals.append(qualified_deal)
    
    # Sort by score descending
    qualified_deals.sort(key=lambda x: x['qualification_score'], reverse=True)
    return qualified_deals

def calculate_mock_score(deal):
    """Calculate a mock qualification score based on deal metrics"""
    score = 50  # Base score
    
    # Growth rate bonus (up to 20 points)
    if deal['growth_rate'] >= 200:
        score += 20
    elif deal['growth_rate'] >= 100:
        score += 15
    elif deal['growth_rate'] >= 50:
        score += 10
    
    # Funding stage bonus (up to 15 points)
    stage_scores = {
        'Seed': 5,
        'Series A': 8,
        'Series B': 10,
        'Series C': 12,
        'Series D': 15,
        'Series E': 15,
        'Series F': 15,
        'Series G': 15,
        'Series I': 15
    }
    score += stage_scores.get(deal['stage'], 5)
    
    # Revenue bonus (up to 15 points)
    if deal['revenue_arr'] >= 500_000_000:
        score += 15
    elif deal['revenue_arr'] >= 100_000_000:
        score += 12
    elif deal['revenue_arr'] >= 50_000_000:
        score += 10
    elif deal['revenue_arr'] >= 10_000_000:
        score += 7
    
    # Runway bonus (up to 10 points)
    if deal['runway_months'] >= 36:
        score += 10
    elif deal['runway_months'] >= 24:
        score += 7
    elif deal['runway_months'] >= 18:
        score += 5
    
    return min(score, 100)

def get_recommendation(score):
    """Get investment recommendation based on score"""
    if score >= 85:
        return "Strong Buy"
    elif score >= 75:
        return "Buy"
    elif score >= 65:
        return "Consider"
    elif score >= 50:
        return "Hold"
    else:
        return "Pass"

def get_deal_statistics():
    """Get statistics about mock deals"""
    return {
        "total_deals": len(MOCK_DEALS),
        "total_funding": sum(d['funding_amount'] for d in MOCK_DEALS),
        "avg_valuation": sum(d['valuation'] for d in MOCK_DEALS) / len(MOCK_DEALS),
        "industries": len(set(d['industry'] for d in MOCK_DEALS)),
        "stages": list(set(d['stage'] for d in MOCK_DEALS)),
        "locations": list(set(d['location'] for d in MOCK_DEALS)),
        "avg_growth_rate": sum(d['growth_rate'] for d in MOCK_DEALS) / len(MOCK_DEALS),
        "total_arr": sum(d['revenue_arr'] for d in MOCK_DEALS)
    }
