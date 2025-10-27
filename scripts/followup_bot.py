#!/usr/bin/env python3
"""
I AM CFO - Follow-up Email Bot
Automatically sends follow-up emails to prospects who didn't reply
Author: Greg Pober
"""

import os
from datetime import datetime, timedelta
from supabase import create_client, Client
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import anthropic

# Initialize clients
supabase: Client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_KEY')
)
sendgrid = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
claude = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

SENDER_EMAIL = 'gpober@iamcfo.com'
SENDER_NAME = 'Greg Pober - I AM CFO'

# Follow-up templates
FOLLOWUP_2 = """Subject: Re: QB showing -$28K... but why?

{first_name},

Quick question:

How long does it take you to answer:
"Can I afford to hire right now?"

QuickBooks: Export to Excel → 2-3 hours
I AM CFO: Ask AI → 3 seconds

Worth a 15-min demo?

https://calendly.com/greg-iamcfo/demo

- Greg
CFO, I AM CFO"""

FOLLOWUP_3 = """Subject: Last one from me

{first_name},

I'll stop after this.

But if you're still pulling QuickBooks into Excel for cash flow...

There's a better way.

5 businesses switched this week.
All QB users like you.

15-min demo: https://calendly.com/greg-iamcfo/demo

Or ignore and I'll leave you alone.

- Greg"""

def get_prospects_for_followup(step):
    """Get prospects who need follow-up"""
    try:
        # Get prospects at previous step who haven't replied
        days_ago = 2 if step == 2 else 3  # 2 days for step 2, 3 days for step 3
        cutoff_date = (datetime.now() - timedelta(days=days_ago)).isoformat()
        
        response = supabase.table('prospects')\
            .select('*')\
            .eq('sequence_step', step - 1)\
            .eq('replied', False)\
            .lte('last_followup_at', cutoff_date)\
            .execute()
        
        return response.data
    except Exception as e:
        print(f"❌ Error fetching prospects: {e}")
        return []

def send_followup(prospect, template, step):
    """Send follow-up email"""
    try:
        # Format template
        first_name = prospect.get('first_name', 'there')
        body = template.format(first_name=first_name)
        
        # Extract subject
        lines = body.split('\n', 1)
        subject = lines[0].replace('Subject:', '').strip()
        email_body = lines[1].strip() if len(lines) > 1 else body
        
        # Send email
        message = Mail(
            from_email=(SENDER_EMAIL, SENDER_NAME),
            to_emails=prospect['email'],
            subject=subject,
            plain_text_content=email_body
        )
        
        response = sendgrid.send(message)
        
        # Update database
        supabase.table('prospects').update({
            'sequence_step': step,
            'last_followup_at': datetime.now().isoformat()
        }).eq('id', prospect['id']).execute()
        
        print(f"✅ Follow-up #{step} sent to {prospect['email']}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send follow-up to {prospect['email']}: {e}")
        return False

def main():
    """Main execution"""
    print("=" * 60)
    print("🔄 I AM CFO FOLLOW-UP BOT")
    print("=" * 60)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    total_sent = 0
    
    # Process follow-up 2 (4 days after initial)
    print("\n📧 Processing Follow-up #2 (4 days after initial)...")
    prospects_step2 = get_prospects_for_followup(2)
    print(f"   Found {len(prospects_step2)} prospects")
    
    for prospect in prospects_step2:
        if send_followup(prospect, FOLLOWUP_2, 2):
            total_sent += 1
    
    # Process follow-up 3 (7 days after follow-up 2)
    print("\n📧 Processing Follow-up #3 (7 days after follow-up #2)...")
    prospects_step3 = get_prospects_for_followup(3)
    print(f"   Found {len(prospects_step3)} prospects")
    
    for prospect in prospects_step3:
        if send_followup(prospect, FOLLOWUP_3, 3):
            total_sent += 1
    
    print("\n" + "=" * 60)
    print("✅ FOLLOW-UP COMPLETE!")
    print("=" * 60)
    print(f"   Total sent: {total_sent}")
    print("=" * 60)

if __name__ == '__main__':
    main()
