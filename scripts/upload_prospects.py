#!/usr/bin/env python3
"""
Upload prospects from CSV to Supabase
Usage: python scripts/upload_prospects.py prospects.csv
"""

import sys
import csv
import os
from supabase import create_client, Client

def upload_prospects(csv_file):
    supabase: Client = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_SERVICE_KEY')
    )
    
    print(f"📁 Reading {csv_file}...")
    
    prospects = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            prospects.append({
                'email': row['email'].strip().lower(),
                'first_name': row.get('first_name', '').strip(),
                'last_name': row.get('last_name', '').strip(),
                'company': row.get('company', '').strip(),
                'title': row.get('title', '').strip(),
                'revenue_estimate': row.get('revenue_estimate', '$2M-$25M').strip(),
                'industry': row.get('industry', '').strip(),
                'source': row.get('source', 'manual').strip(),
                'uses_quickbooks': True
            })
    
    print(f"✅ Found {len(prospects)} prospects")
    
    uploaded = 0
    batch_size = 100
    
    for i in range(0, len(prospects), batch_size):
        batch = prospects[i:i + batch_size]
        try:
            supabase.table('prospects').upsert(batch, on_conflict='email').execute()
            uploaded += len(batch)
            print(f"✅ Uploaded batch {i//batch_size + 1}: {len(batch)} prospects")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"🎉 Upload complete! {uploaded} prospects")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python scripts/upload_prospects.py prospects.csv")
        sys.exit(1)
    
    upload_prospects(sys.argv[1])
