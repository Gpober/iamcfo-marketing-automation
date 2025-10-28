#!/usr/bin/env python3
"""
I AM CFO - Email Campaign Bot
Focus: Daily cash flow pain points that I AM CFO solves
Positioning: Helpful solution, not critical of current setup
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

# ============================================================================
# EMAIL TEMPLATE - Daily Cash Flow Pain Points
# ============================================================================

EMAIL_TEMPLATE_1 = """Subject: Can you afford to hire that new person?

{first_name},

You're looking at the bank balance.
You're looking at the bills due.
You're trying to do the math in your head.

"Can I afford this hire?"
"Should I wait another month?"
"What if that big invoice doesn't come in?"

Every business owner asks these questions.
But most are flying blind with spreadsheets and guesswork.

I AM CFO shows you the answer in real-time:

✅ Today's actual cash position (not last month's)
✅ Your burn rate this week (see where money's going)
✅ Cash flow forecast (know what's coming in and out)
✅ Profit by location, service, or product (know what's working)

One {industry} company used I AM CFO to discover they had $47K more cash available than they thought. They made the hire. Best decision they made.

Another found they were losing $3K/month on their most popular service. Adjusted pricing. Turned it around in 30 days.

Real-time cash flow visibility = Better decisions.

👉 See your real-time cash flow: https://info.iamcfo.com

Worth 15 minutes to stop guessing?

— 
Greg Pober
CEO | I AM CFO • 954-684-9011

P.S. Connects to your QuickBooks/Xero Accounting Software. Set up within 24 hours. See your real cash position today."""


# Alternative subject lines for A/B testing
SUBJECT_LINES = [
    "Can you afford to hire that new person?",
    "What's your real cash position today?",
    "Stop guessing about your cash flow",
    "You're making million-dollar decisions with month-old data",
    "How much cash can you actually spend this month?",
    "The question every business owner asks daily",
    "Why is cash always tighter than expected?",
]


# ============================================================================
# INDUSTRY-SPECIFIC PAIN POINTS - Daily Cash Flow Struggles
# ============================================================================

INDUSTRY_PAIN_POINTS = {
    'construction': {
        'subject': "How much can you bid on that new job?",
        'opening': "You've got a bid request. You need to decide: What can you afford to commit to?",
        'pain': "Material costs are up. Labor's tight. You've got 3 jobs running and 2 more starting next month.",
        'question': "Can you afford to take this job without stretching cash too thin?",
        'solution': "I AM CFO shows you real-time cash flow by job. You'll know exactly what you can bid without putting the business at risk.",
        'example': "A GC in Florida used I AM CFO to see they had $85K more available than expected. Bid on a $400K job. Won it. Profitable."
    },
    'restaurant': {
        'subject': "Why does cash feel tighter than sales suggest?",
        'opening': "Sales are up. But somehow, cash is still tight. What's going on?",
        'pain': "Food costs fluctuate. Labor scheduling is a puzzle. Some locations feel more profitable than others, but which ones?",
        'question': "Where is your cash actually going?",
        'solution': "I AM CFO shows real-time P&L by location and tracks your actual food cost percentage daily.",
        'example': "A 3-location restaurant group discovered one location was bleeding $4K/month. Fixed vendor pricing. Turned profitable in 6 weeks."
    },
    'property management': {
        'subject': "Which properties are actually making you money?",
        'opening': "You've got 8 properties. Some feel profitable. Some don't. But which ones actually are?",
        'pain': "Maintenance costs spike unexpectedly. Vacancy rates change. Some properties just seem to eat cash.",
        'question': "Can you see profit by property in real-time?",
        'solution': "I AM CFO gives you real-time profitability by property. You'll know exactly which ones are winners and which need attention.",
        'example': "A PM company found 2 of their 12 properties were breakeven or worse. Raised rents on one, sold the other. Added $6K/month profit."
    },
    'hvac': {
        'subject': "Can you afford that new truck?",
        'opening': "Your truck has 180K miles. You need to replace it. But can you afford it right now?",
        'pain': "Jobs are booked out 3 weeks. Revenue looks good on paper. But cash? That's harder to see.",
        'question': "What's your real cash position today?",
        'solution': "I AM CFO shows today's cash, this week's burn rate, and projects your cash flow for the next 90 days.",
        'example': "An HVAC company saw they had $65K available. Bought 2 trucks. Took on more jobs. Grew 40% in 6 months."
    },
    'professional services': {
        'subject': "Are you actually making money on that client?",
        'opening': "You've got a big client. Lots of hours. But are you actually profitable on them?",
        'pain': "Some clients take way more time than others. Scope creep happens. You bill hours but don't track true profitability.",
        'question': "Which clients are making you money and which are costing you?",
        'solution': "I AM CFO tracks profitability by client and project in real-time. You'll know exactly who's worth the effort.",
        'example': "A consulting firm found their 3rd biggest client was their least profitable. Raised rates. Client said yes. Added $5K/month margin."
    },
    'automotive': {
        'subject': "Why does cash disappear faster than expected?",
        'opening': "Parts are expensive. Labor costs are up. Sales look good. But cash always feels tight.",
        'pain': "You're juggling parts inventory, labor scheduling, and customer payments. Cash flow is a daily puzzle.",
        'question': "Where is your cash actually going?",
        'solution': "I AM CFO shows real-time cash flow with daily burn rate, accounts payable coming due, and receivables coming in.",
        'example': "An auto shop discovered they were sitting on $35K in parts inventory they didn't need. Liquidated it. Freed up cash."
    },
    'manufacturing': {
        'subject': "Can you afford that equipment upgrade?",
        'opening': "You need new equipment. It would help production. But can you afford it without stretching too thin?",
        'pain': "Material costs change. Production schedules shift. Some products are more profitable than others, but which?",
        'question': "What's your real cash position and burn rate?",
        'solution': "I AM CFO gives you real-time cash flow with 90-day projections so you can make big decisions with confidence.",
        'example': "A manufacturer saw they had $120K available. Bought new equipment. Increased capacity 30%. ROI in 8 months."
    },
    'healthcare': {
        'subject': "When will that insurance payment actually hit?",
        'opening': "You've got receivables out there. Some insurance. Some patient pay. But when does cash actually come in?",
        'pain': "Insurance delays. Patient payment plans. Revenue is complicated to track and cash flow even more so.",
        'question': "What's your real cash position today?",
        'solution': "I AM CFO tracks cash flow in real-time and projects when receivables will actually convert to cash.",
        'example': "A medical practice saw they had $45K in receivables over 90 days. Focused collections. Brought in $38K in 30 days."
    },
}


def get_industry_template(industry):
    """Get industry-specific email template"""
    if not industry:
        return None
    
    industry_lower = industry.lower()
    
    for key, template in INDUSTRY_PAIN_POINTS.items():
        if key in industry_lower:
            return template
    
    return None


def get_prospects_to_email(batch_size=100):
    """Get next batch of prospects who haven't been emailed"""
    try:
        response = supabase.table('prospects')\
            .select('*')\
            .eq('email_sent', False)\
            .limit(batch_size)\
            .execute()
        
        return response.data
    except Exception as e:
        print(f"❌ Error fetching prospects: {e}")
        return []


def personalize_with_claude(template, prospect):
    """Use Claude to personalize the email based on prospect data and daily pain points"""
    try:
        # Get prospect info
        first_name = prospect.get('first_name', 'there').strip()
        if not first_name:
            first_name = 'there'
        
        company = prospect.get('company', 'your company')
        revenue = prospect.get('revenue_estimate', '$2M-$25M')
        title = prospect.get('title', 'business owner')
        industry = prospect.get('industry', '')
        
        # Try to get industry-specific template
        industry_template = get_industry_template(industry)
        
        if industry_template:
            # Use industry-specific pain point
            prompt = f"""Personalize this email for a business owner who struggles with daily cash flow decisions.

Prospect info:
- Name: {first_name}
- Company: {company}
- Title: {title}
- Revenue: {revenue}
- Industry: {industry}

Industry-specific pain point:
Subject: {industry_template['subject']}
Opening: {industry_template['opening']}
Pain: {industry_template['pain']}
Question: {industry_template['question']}
Solution: {industry_template['solution']}
Example: {industry_template['example']}

Instructions:
1. Use their first name naturally
2. Start with the industry-specific pain point (it's relatable and real)
3. Make it feel like you understand THEIR specific daily struggle
4. Show how I AM CFO solves this with real-time cash flow visibility
5. Use the industry example to prove it works
6. Keep it conversational and empathetic (NOT salesy)
7. End with simple CTA: "See your real-time cash flow: https://info.iamcfo.com"
8. P.S. should emphasize quick setup (30 min) and immediate visibility
9. Tone: Helpful advisor who gets their pain, not a salesperson
10. Keep under 200 words
11. Return ONLY the personalized email with subject line

Personalized email:"""
        else:
            # Use generic cash flow pain template
            prompt = f"""Personalize this email for a business owner who struggles with daily cash flow decisions.

Prospect info:
- Name: {first_name}
- Company: {company}
- Title: {title}
- Revenue: {revenue}
- Industry: {industry if industry else 'small business'}

Email template:
{template}

Instructions:
1. Use their first name naturally
2. Focus on the daily pain: "Can I afford this?" decisions
3. Emphasize real-time cash flow visibility (that's what we solve)
4. Make it relatable - every business owner asks these questions
5. Show concrete value: know your cash position TODAY, not last month
6. Use {industry if industry else 'business'} for the example
7. Keep it empathetic and helpful (NOT critical or salesy)
8. Tone: Understanding advisor, not pushy salesperson
9. Keep under 200 words
10. Return ONLY the personalized email with subject line

Personalized email:"""
        
        message = claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        personalized = message.content[0].text.strip()
        
        # Extract subject and body
        if personalized.startswith('Subject:'):
            lines = personalized.split('\n', 1)
            subject = lines[0].replace('Subject:', '').strip()
            body = lines[1].strip() if len(lines) > 1 else personalized
        else:
            # Use industry-specific subject if available, otherwise default
            if industry_template:
                subject = industry_template['subject']
            else:
                subject = 'Can you afford to hire that new person?'
            body = personalized
        
        return subject, body
        
    except Exception as e:
        print(f"⚠️ Claude personalization failed for {prospect['email']}: {e}")
        
        # Fallback to basic template
        industry_template = get_industry_template(prospect.get('industry', ''))
        
        if industry_template:
            subject = industry_template['subject']
            body = f"""{first_name},

{industry_template['opening']}

{industry_template['pain']}

{industry_template['question']}

{industry_template['solution']}

{industry_template['example']}

See your real-time cash flow: https://info.iamcfo.com

— 
Greg Pober
CEO | I AM CFO • 954-684-9011

P.S. Connects to your QuickBooks/Xero Accounting Software. Set up within 24 hours. See your cash position today."""
        else:
            subject = 'Can you afford to hire that new person?'
            body = template.format(
                first_name=first_name,
                industry=prospect.get('industry', 'business')
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
    print("🚀 I AM CFO EMAIL CAMPAIGN - Daily Cash Flow Solutions")
    print("=" * 60)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📧 Batch size: {BATCH_SIZE}")
    print(f"💰 Focus: Real-time cash flow visibility")
    print(f"🎯 Pain points: Daily 'Can I afford this?' decisions")
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
