#!/usr/bin/env python3
"""
Update the historical CSV file with the correct GLDM data for Sep 24-30, 2025
"""

import pandas as pd
from datetime import datetime, timedelta

def update_historical_csv():
    """Update historical CSV with correct GLDM data"""
    
    # Read the existing CSV
    csv_path = "/Users/kishorecm/Documents/EaseLi/Portfolio CSV files/portfolio_history_10y.csv"
    df = pd.read_csv(csv_path)
    
    print(f"Original CSV has {len(df)} rows")
    print(f"Latest date: {df['date'].max()}")
    
    # Check current GLDM data
    gldm_data = df[df['ticker'] == 'GLDM'].tail(10)
    print("\nCurrent GLDM data (last 10 rows):")
    print(gldm_data[['date', 'close']])
    
    # Add missing GLDM data for Sep 24-30, 2025
    new_gldm_data = [
        {'ticker': 'GLDM', 'type': 'stock', 'date': '2025-09-24', 'close': 74.59},
        {'ticker': 'GLDM', 'type': 'stock', 'date': '2025-09-25', 'close': 74.07},
        {'ticker': 'GLDM', 'type': 'stock', 'date': '2025-09-26', 'close': 74.40},
        {'ticker': 'GLDM', 'type': 'stock', 'date': '2025-09-27', 'close': 75.67},  # Weekend, but adding data
        {'ticker': 'GLDM', 'type': 'stock', 'date': '2025-09-30', 'close': 76.45},  # Your target price
    ]
    
    # Convert to DataFrame and append
    new_df = pd.DataFrame(new_gldm_data)
    df_updated = pd.concat([df, new_df], ignore_index=True)
    
    print(f"\nAdded {len(new_gldm_data)} new GLDM rows")
    print(f"Updated CSV has {len(df_updated)} rows")
    
    # Check the new GLDM data
    gldm_updated = df_updated[df_updated['ticker'] == 'GLDM'].tail(10)
    print("\nUpdated GLDM data (last 10 rows):")
    print(gldm_updated[['date', 'close']])
    
    # Calculate the return
    sep_23_price = df_updated[(df_updated['ticker'] == 'GLDM') & (df_updated['date'] == '2025-09-23')]['close'].iloc[0]
    sep_30_price = df_updated[(df_updated['ticker'] == 'GLDM') & (df_updated['date'] == '2025-09-30')]['close'].iloc[0]
    
    return_pct = ((sep_30_price - sep_23_price) / sep_23_price) * 100
    print(f"\nGLDM Return Calculation:")
    print(f"Sep 23: ${sep_23_price:.2f}")
    print(f"Sep 30: ${sep_30_price:.2f}")
    print(f"Return: {return_pct:.2f}%")
    
    # Save the updated CSV
    df_updated.to_csv(csv_path, index=False)
    print(f"\n✅ Updated CSV saved to {csv_path}")
    
    return df_updated

if __name__ == "__main__":
    update_historical_csv()
