import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)

# --- 1. GENERATE DIM_USERS ---
num_users = 1500
plans = ['Basic (Free)', 'Premium ($9.99/mo)', 'Metal ($19.99/mo)']
plan_weights = [0.70, 0.20, 0.10]
kyc_statuses = ['Verified', 'Verified', 'Verified', 'Pending', 'Rejected']
cities = ['Johannesburg', 'Cape Town', 'Durban', 'Pretoria', 'Gqeberha']
acq_channels = ['Meta Ads', 'Google Search', 'Organic App Store', 'Referral Program', 'Fintech Influencers']

users = []
for i in range(1, num_users + 1):
    signup_dt = datetime(2025, 1, 1) + timedelta(days=int(np.random.randint(0, 365)))
    income = float(np.random.choice([15000, 25000, 45000, 75000, 120000], p=[0.35, 0.30, 0.20, 0.10, 0.05]))
    credit_score = int(np.clip(np.random.normal(650, 85, 1)[0], 300, 850))
    
    users.append({
        'user_id': f'USR_{i:05d}',
        'signup_date': signup_dt.strftime('%Y-%m-%d'),
        'plan_tier': np.random.choice(plans, p=plan_weights),
        'kyc_status': np.random.choice(kyc_statuses),
        'city': np.random.choice(cities, p=[0.35, 0.30, 0.15, 0.12, 0.08]),
        'acquisition_channel': np.random.choice(acq_channels, p=[0.25, 0.25, 0.20, 0.20, 0.10]),
        'monthly_income': income,
        'credit_score': credit_score,
        'cac_cost': float(round(np.random.uniform(15, 85), 2))
    })

df_users = pd.DataFrame(users)

# --- 2. GENERATE DIM_PRODUCTS ---
products_data = {
    'product_id': ['PROD_01', 'PROD_02', 'PROD_03', 'PROD_04', 'PROD_05'],
    'product_name': ['Digital Checking Account', 'Savings Vault', 'Micro-Credit Loan', 'Crypto & Stock Trading', 'International FX Transfer'],
    'product_category': ['Core Banking', 'Savings', 'Lending', 'Investments', 'Payments'],
    'fee_structure': ['Free / Monthly Subscription', '0.5% Yield Fee', '18.5% APR Interest', '1.2% Transaction Fee', '1.5% FX Spread']
}
df_products = pd.DataFrame(products_data)

# --- 3. GENERATE FACT_LOANS (MICRO-CREDIT PORTFOLIO) ---
num_loans = 1200
loans = []

for i in range(1, num_loans + 1):
    user = df_users.sample(1).iloc[0]
    disbursed_dt = datetime.strptime(user['signup_date'], '%Y-%m-%d') + timedelta(days=int(np.random.randint(1, 180)))
    if disbursed_dt > datetime(2025, 12, 31):
        disbursed_dt = datetime(2025, 12, 15)
        
    term_months = int(np.random.choice([3, 6, 12], p=[0.5, 0.3, 0.2]))
    principal = float(round(np.random.uniform(500, 15000), 2))
    interest_rate = 0.185
    total_interest = float(round(principal * interest_rate * (term_months / 12), 2))
    
    # Risk calculation based on credit score
    if user['credit_score'] < 580:
        status = np.random.choice(['On-Time', '30-Day Late', '90-Day Default'], p=[0.40, 0.25, 0.35])
    elif user['credit_score'] < 670:
        status = np.random.choice(['On-Time', '30-Day Late', '90-Day Default'], p=[0.70, 0.18, 0.12])
    else:
        status = np.random.choice(['On-Time', '30-Day Late', '90-Day Default'], p=[0.92, 0.06, 0.02])
        
    loans.append({
        'loan_id': f'LN_{i:05d}',
        'user_id': user['user_id'],
        'disbursement_date': disbursed_dt.strftime('%Y-%m-%d'),
        'term_months': term_months,
        'principal_amount': principal,
        'expected_interest': total_interest,
        'repayment_status': status,
        'is_defaulted': 1 if status == '90-Day Default' else 0
    })

df_loans = pd.DataFrame(loans)

# --- 4. GENERATE FACT_TRANSACTIONS ---
num_txns = 12000
txns = []

txn_types = ['P2P Transfer', 'Merchant Card Payment', 'Savings Deposit', 'Loan Repayment', 'Crypto Buy/Sell']
device_types = ['iOS', 'Android', 'Web']
merchants = ['Supermarket', 'Electronics Store', 'Ride Share', 'Online Marketplace', 'Utilities & Bills']

for i in range(1, num_txns + 1):
    user = df_users.sample(1).iloc[0]
    prod = df_products.sample(1).iloc[0]
    
    txn_dt = datetime(2025, 1, 1) + timedelta(days=int(np.random.randint(0, 365)), minutes=int(np.random.randint(0, 1440)))
    amount = float(round(np.random.exponential(scale=250) + 10, 2))
    
    # Fraud flag logic
    is_high_amount = amount > 2500
    is_rejected_kyc = user['kyc_status'] == 'Rejected'
    is_flagged = 1 if (is_high_amount and np.random.rand() > 0.4) or (is_rejected_kyc and np.random.rand() > 0.2) else 0
    
    txns.append({
        'transaction_id': f'TXN_{i:07d}',
        'transaction_date': txn_dt.strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': user['user_id'],
        'product_id': prod['product_id'],
        'transaction_type': np.random.choice(txn_types),
        'merchant_category': np.random.choice(merchants),
        'device_type': np.random.choice(device_types, p=[0.55, 0.40, 0.05]),
        'amount': amount,
        'fee_earned': float(round(amount * 0.015, 2)),
        'is_flagged_fraud': is_flagged
    })

df_txns = pd.DataFrame(txns)

# --- 5. EXPORT TO EXCEL ---
file_name = "Project_51_Fintech_Analytics_Dataset.xlsx"
with pd.ExcelWriter(file_name, engine='xlsxwriter') as writer:
    df_txns.to_excel(writer, sheet_name='Fact_Transactions', index=False)
    df_loans.to_excel(writer, sheet_name='Fact_Loans', index=False)
    df_users.to_excel(writer, sheet_name='Dim_Users', index=False)
    df_products.to_excel(writer, sheet_name='Dim_Products', index=False)

print(f"Project 51 Fintech Dataset successfully generated and exported to '{file_name}'!")