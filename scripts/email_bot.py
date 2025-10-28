#!/usr/bin/env python3
"""
I AM CFO - Email Campaign Bot
Sends personalized cold emails to QuickBooks users using Claude API
Author: Greg Pober
"""

import os
import sys
import time
from datetime import datetime
from supabase import create_client, Client
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, TrackingSettings, ClickTracking, OpenTracking
import anthropic

# Initialize clients
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# Validate environment variables
if not SUPABASE_URL:
    print("❌ ERROR: SUPABASE_URL environment variable is not set!")
    print("   Check your GitHub secrets at:")
    print("   https://github.com/gpober/iamcfo-marketing-automation/settings/secrets/actions")
    sys.exit(1)

if not SUPABASE_SERVICE_KEY:
    print("❌ ERROR: SUPABASE_SERVICE_KEY environment variable is not set!")
    sys.exit(1)

if not SENDGRID_API_KEY:
    print("❌ ERROR: SENDGRID_API_KEY environment variable is not set!")
    sys.exit(1)

if not ANTHROPIC_API_KEY:
    print("❌ ERROR: ANTHROPIC_API_KEY environment variable is not set!")
    sys.exit(1)

print(f"✅ SUPABASE_URL: {SUPABASE_URL}")
print(f"✅ Environment variables loaded successfully")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
sendgrid = SendGridAPIClient(SENDGRID_API_KEY)
claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

BATCH_SIZE = int(os.getenv('BATCH_SIZE', 100))
SENDER_EMAIL = 'gpober@iamcfo.com'
SENDER_NAME = 'Greg Pober - I AM CFO'

# Email template
EMAIL_TEMPLATE_1 = """Subject: Your QuickBooks says cash dropped $28K — but why?

Hi {first_name},

QuickBooks shows your cash down $28K last month.

But why?

Most owners spend hours exporting data and sifting through spreadsheets trying to find the answer.

I AM CFO gives you real-time dashboards that turn QuickBooks data into insights you can act on — instantly.

No more guesswork. Just clarity.

👉 Worth a 15-minute look? https://info.iamcfo.com

— 
Greg Pober
CEO | I AM CFO • 954-684-9011

P.S. We just helped a $2-5M company find $4K a month in hidden vendor costs — in 10 minutes."""

def get_prospects_to_email(batch_size=100):
    """Get next batch of prospects who haven't been emailed"""
    try:
        response = supabase.table('prospects')\
            .select('*')\
            .eq('email_sent', False)\
            .eq('uses_quickbooks', True)\
            .limit(batch_size)\
            .execute()
        
        return response.data
    except Exception as e:
        print(f"❌ Error fetching prospects: {e}")
        return []

def personalize_with_claude(template, prospect):
    """Use Claude to personalize the email based on prospect data"""
    try:
        # Get first name or use "there" as fallback
        first_name = prospect.get('first_name', 'there').strip()
        if not first_name:
            first_name = 'there'
        
        # Get company info
        company = prospect.get('company', 'your company')
        revenue = prospect.get('revenue_estimate', '$2M-$25M')
        title = prospect.get('title', 'business owner')
        
        message = claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": f"""Personalize this cold email for a QuickBooks user.

Prospect info:
- Name: {first_name}
- Company: {company}
- Title: {title}
- Revenue: {revenue}

Email template:
{template}

Instructions:
1. Use their first name naturally (if "there", keep it casual)
2. Keep the EXACT same structure and message
3. If you mention "a {revenue_estimate} company", use their actual revenue range
4. Stay SHORT and DIRECT
5. Maintain the casual, confident tone
6. Don't be overly formal or salesy
7. Return ONLY the personalized email with subject line, no explanations

Personalized email:"""
            }]
        )
        
        personalized = message.content[0].text.strip()
        
        # Extract subject and body
        if personalized.startswith('Subject:'):
            lines = personalized.split('\n', 1)
            subject = lines[0].replace('Subject:', '').strip()
            body = lines[1].strip() if len(lines) > 1 else personalized
        else:
            subject = 'QB showing -$28K... but why?'
            body = personalized
        
        return subject, body
        
    except Exception as e:
        print(f"⚠️ Claude personalization failed for {prospect['email']}: {e}")
        # Fallback to basic template
        subject = 'QB showing -$28K... but why?'
        body = template.format(
            first_name=prospect.get('first_name', 'there'),
            revenue_estimate=prospect.get('revenue_estimate', '$2M-$25M')
        )
        return subject, body

def send_email(prospect, subject, email_body):
    """Send email via SendGrid with tracking"""
    try:
        message = Mail(
            from_email=(SENDER_EMAIL, SENDER_NAME),
            to_emails=prospect['email'],
            subject=subject,
            plain_text_content=email_body
        )
        
        # Enable tracking
        message.tracking_settings = TrackingSettings()
        message.tracking_settings.click_tracking = ClickTracking(True, True)
        message.tracking_settings.open_tracking = OpenTracking(True)
        
        # Send email
        response = sendgrid.send(message)
        
        # Update database
        supabase.table('prospects').update({
            'email_sent': True,
            'email_sent_at': datetime.now().isoformat(),
            'sequence_step': 1
        }).eq('id', prospect['id']).execute()
        
        print(f"✅ Sent to {prospect['email']} ({prospect.get('company', 'Unknown')})")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send to {prospect['email']}: {e}")
        return False

def main():
    """Main execution"""
    print("=" * 60)
    print("🚀 I AM CFO EMAIL CAMPAIGN BOT")
    print("=" * 60)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📧 Batch size: {BATCH_SIZE}")
    print(f"👤 Sender: {SENDER_NAME} <{SENDER_EMAIL}>")
    print("-" * 60)
    
    # Get prospects
    prospects = get_prospects_to_email(BATCH_SIZE)
    
    if not prospects:
        print("ℹ️ No prospects to email. Add more to the database!")
        print("\nTo add prospects:")
        print("  python scripts/upload_prospects.py prospects.csv")
        return
    
    print(f"📧 Found {len(prospects)} prospects to email")
    print("-" * 60)
    
    sent_count = 0
    failed_count = 0
    
    for i, prospect in enumerate(prospects, 1):
        print(f"\n[{i}/{len(prospects)}] Processing {prospect['email']}...")
        
        # Personalize email with Claude
        print("  🤖 Personalizing with Claude AI...")
        subject, personalized_email = personalize_with_claude(EMAIL_TEMPLATE_1, prospect)
        
        # Send email
        print(f"  📤 Sending: {subject}")
        if send_email(prospect, subject, personalized_email):
            sent_count += 1
        else:
            failed_count += 1
        
        # Rate limiting: 10 seconds between emails
        # This keeps us under SendGrid's limits and looks more natural
        if i < len(prospects):
            print("  ⏳ Waiting 10 seconds...")
            time.sleep(10)
    
    print("\n" + "=" * 60)
    print("✅ CAMPAIGN COMPLETE!")
    print("=" * 60)
    print(f"   Sent: {sent_count}")
    print(f"   Failed: {failed_count}")
    print(f"   Success rate: {(sent_count/(sent_count+failed_count)*100):.1f}%")
    print(f"   Total time: ~{len(prospects) * 10 / 60:.1f} minutes")
    print("=" * 60)
    
    # Update daily analytics
    try:
        supabase.rpc('update_daily_snapshot').execute()
        print("📊 Analytics updated")
    except:
        pass

if __name__ == '__main__':
    main()
