#!/usr/bin/env python3
"""
I AM CFO - Follow-up Email Bot
Follow-ups focused on daily cash flow decisions
Automatically sends to prospects who didn't reply
Author: Greg Pober

TIMING: 2 days / 3 days / 3 days
"""

import os
import time
from datetime import datetime, timedelta
from supabase import create_client, Client
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, TrackingSettings, ClickTracking, OpenTracking
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

# ============================================================================
# FOLLOW-UP TEMPLATES - Cash Flow Pain Points
# ============================================================================

# Follow-up #1 - 2 days after initial (Reminder of the pain)
FOLLOWUP_1 = """Subject: Re: Can you afford to hire that new person?

{first_name},

Quick follow-up.

You know that feeling when you're staring at the bank balance, trying to figure out if you can afford something?

Hire that person?
Buy that equipment?
Take on that new project?

Most business owners spend hours in spreadsheets trying to answer these questions.

I AM CFO answers them in seconds.

Real-time cash position. Burn rate. Cash flow forecast.

One {industry} owner told me: "I spent 3 hours last month trying to figure out if I could hire. Now I just look at the dashboard. Takes 10 seconds."

Worth 15 minutes to see it?

👉 {tracking_link}

— 
Greg Pober
CEO | I AM CFO • 954-684-9011

P.S. Still connects to QuickBooks. Still takes 30 minutes to set up. Still shows your cash position today."""


# Follow-up #2 - 3 days after follow-up #1 (Social proof + urgency)
FOLLOWUP_2 = """Subject: Making decisions with month-old data

{first_name},

Straight talk:

You're making hiring decisions with month-old data.
You're bidding jobs with last month's costs.
You're planning purchases without knowing today's cash position.

That's not a criticism. That's just how traditional bookkeeping works.

But here's what changed for one {industry} company:

Before I AM CFO:
• "Can we afford this?" = 2 hours in spreadsheets
• Found out about problems weeks too late
• Made decisions based on guesses

After I AM CFO:
• "Can we afford this?" = 10 seconds
• See problems the day they start
• Make decisions based on data

The difference? Real-time cash flow visibility.

See it yourself: {tracking_link}

— 
Greg Pober
CEO | I AM CFO • 954-684-9011

P.S. $699/month. Or keep guessing. Your call."""


# Follow-up #3 - 3 days after follow-up #2 (Final value reminder)
FOLLOWUP_3 = """Subject: Last one from me

{first_name},

I'll keep this short.

Three questions you probably asked yourself this week:

1. "Can I afford to hire that person?"
2. "Why is cash tighter than I expected?"
3. "Which location/client/project is actually profitable?"

If you're still answering these with spreadsheets and guesswork, that's on you.

I AM CFO gives you the answer in real-time.

$699/month to stop guessing about your cash flow.

See it: {tracking_link}

— 
Greg

P.S. If you're good with month-old data and spreadsheet math, ignore this. If you want to see your cash position today, click the link."""


# ============================================================================
# INDUSTRY-SPECIFIC FOLLOW-UPS (More targeted)
# ============================================================================

INDUSTRY_FOLLOWUPS = {
    'construction': {
        'followup_1': """Subject: Re: How much can you bid on that new job?

{first_name},

Quick follow-up on that bid question.

You've got materials fluctuating. Labor's tight. Jobs overlapping.

And you're trying to figure out: "Can I afford to take on this next job?"

Most GCs spend hours in spreadsheets trying to answer this.

I AM CFO shows you:
• Real-time cash by job
• What you can actually commit to
• Where you're profitable vs. bleeding

A GC in Tampa told me: "I used to spend Friday afternoons doing cash flow math. Now I check my phone. Takes 30 seconds."

See it: {tracking_link}

— 
Greg Pober
CEO | I AM CFO • 954-684-9011""",
        
        'followup_2': """Subject: Stop bidding jobs blind

{first_name},

Real talk: Are you bidding jobs based on last month's costs?

Materials went up 8% two weeks ago. Your bid spreadsheet doesn't know that yet.

I AM CFO shows you real-time costs, real-time margins, real-time cash available.

One GC found they were underbidding by 12% on concrete work. Caught it week 1 instead of month 3. Saved $40K on the next 5 jobs.

That's 57 months of I AM CFO paid for by one insight.

See your real-time job costs: {tracking_link}

— 
Greg Pober
CEO | I AM CFO • 954-684-9011""",
        
        'followup_3': """Subject: Last chance (from me)

{first_name},

Your competitors are seeing their job profitability in real-time.

You'll see yours in 3 weeks when your bookkeeper closes the books.

The gap between you and them is growing.

$699/month to stop flying blind.

{tracking_link}

— 
Greg"""
    },
    
    'restaurant': {
        'followup_1': """Subject: Re: Why does cash feel tighter than sales suggest?

{first_name},

Quick follow-up on that cash flow question.

Sales are up. Tables are full. But somehow cash is tight.

Where's it going?

Most restaurant owners spend hours trying to figure this out.

I AM CFO shows you:
• Real-time P&L by location
• Food cost percentage today (not month-end)
• Which locations print money vs. bleed cash

A restaurant group told me: "We discovered one location was losing $4K/month. Fixed it in week 1 instead of finding out in month 3."

See your real-time restaurant numbers: {tracking_link}

— 
Greg Pober
CEO | I AM CFO • 954-684-9011""",
        
        'followup_2': """Subject: Your food cost spiked last week

{first_name},

Actually, I don't know if your food cost spiked last week.

But you probably don't either.

You'll find out in 3 weeks when your bookkeeper's report comes in.

By then? You've bled another 3 weeks of margin.

I AM CFO shows food cost percentage daily. By location. In real-time.

One 3-location group found their downtown spot was 6% higher than the other two. Fixed vendor pricing. Added $48K/year profit.

See your real-time food cost: {tracking_link}

— 
Greg Pober
CEO | I AM CFO • 954-684-9011""",
        
        'followup_3': """Subject: Closing your file

{first_name},

No response — I get it.

If you ever want to see which locations are actually profitable (in real-time, not month-end), you know where to find me.

{tracking_link}

— 
Greg"""
    },
    
    'hvac': {
        'followup_1': """Subject: Re: Can you afford that new truck?

{first_name},

Quick follow-up on that truck question.

You need equipment. Business is good. But is cash actually available?

Most HVAC owners spend Friday doing mental math trying to figure this out.

I AM CFO shows you:
• Today's cash position
• This week's burn rate
• 90-day cash flow projection

An HVAC company in Miami told me: "We saw we had $65K available. Bought 2 trucks. Took on 40% more jobs. Grew faster than we thought possible."

See your real-time cash position: {tracking_link}

— 
Greg Pober
CEO | I AM CFO • 954-684-9011""",
        
        'followup_2': """Subject: Your cash is tighter than it should be

{first_name},

You're booked out 3 weeks. Revenue looks good.

But cash? Cash feels tight.

Why?

Most HVAC owners don't know because they're looking at month-old data.

I AM CFO shows you real-time:
• Where cash is going (A/P, payroll, materials)
• What's coming in (A/R aging, payment schedule)
• What you actually have available today

One HVAC company found they were sitting on $35K in parts inventory they didn't need. Liquidated it. Freed up cash for the trucks they did need.

See where your cash is going: {tracking_link}

— 
Greg Pober
CEO | I AM CFO • 954-684-9011""",
        
        'followup_3': """Subject: Equipment or wait?

{first_name},

That equipment question isn't going away.

You can keep guessing about cash availability.

Or you can see it in real-time.

$699/month vs. guessing wrong on a $50K decision.

{tracking_link}

— 
Greg"""
    },
}


def generate_tracking_link(campaign, source, medium, content, industry=None):
    """
    Generate UTM-tracked link for info.iamcfo.com
    
    Args:
        campaign: followup_1, followup_2, followup_3
        source: email
        medium: followup
        content: prospect email or ID
        industry: construction, restaurant, hvac, etc.
    
    Returns:
        Full URL with UTM parameters
    """
    base_url = "https://info.iamcfo.com"
    
    # Build UTM parameters
    params = {
        'utm_source': source,
        'utm_medium': medium,
        'utm_campaign': campaign,
        'utm_content': content
    }
    
    # Add industry if available
    if industry:
        params['utm_term'] = industry.lower().replace(' ', '_')
    
    # Build query string
    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    
    return f"{base_url}?{query_string}"


def get_industry_followup(industry, step):
    """Get industry-specific follow-up template"""
    if not industry:
        return None
    
    industry_lower = industry.lower()
    
    # Map step to followup key
    followup_key = f'followup_{step}'
    
    for key, templates in INDUSTRY_FOLLOWUPS.items():
        if key in industry_lower and followup_key in templates:
            return templates[followup_key]
    
    return None


def get_prospects_for_followup(step):
    """Get prospects who need follow-up"""
    try:
        # Calculate days since last contact
        # TIMING: 2 days / 3 days / 3 days
        if step == 1:
            days_ago = 2  # 2 days after initial email
            previous_step = 1  # They received initial email
        elif step == 2:
            days_ago = 3  # 3 days after follow-up #1
            previous_step = 2  # They received follow-up #1
        else:  # step == 3
            days_ago = 3  # 3 days after follow-up #2
            previous_step = 3  # They received follow-up #2
        
        cutoff_date = (datetime.now() - timedelta(days=days_ago)).isoformat()
        
        response = supabase.table('prospects')\
            .select('*')\
            .eq('sequence_step', previous_step)\
            .eq('replied', False)\
            .lte('email_sent_at', cutoff_date)\
            .execute()
        
        return response.data
    except Exception as e:
        print(f"❌ Error fetching prospects: {e}")
        return []


def send_followup(prospect, step):
    """Send follow-up email with industry-specific template if available"""
    try:
        first_name = prospect.get('first_name', 'there').strip() or 'there'
        industry = prospect.get('industry', '')
        prospect_email = prospect.get('email', '')
        
        # Generate tracking link
        campaign = f"followup_{step}"
        tracking_link = generate_tracking_link(
            campaign=campaign,
            source='email',
            medium='followup',
            content=prospect_email,
            industry=industry
        )
        
        # Try to get industry-specific follow-up
        industry_template = get_industry_followup(industry, step)
        
        if industry_template:
            # Use industry-specific template
            body = industry_template.format(
                first_name=first_name,
                industry=industry,
                tracking_link=tracking_link
            )
        else:
            # Use generic follow-up
            if step == 1:
                template = FOLLOWUP_1
            elif step == 2:
                template = FOLLOWUP_2
            else:
                template = FOLLOWUP_3
            
            body = template.format(
                first_name=first_name,
                industry=industry if industry else 'business',
                tracking_link=tracking_link
            )
        
        # Extract subject and email body
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
        
        # Enable tracking
        message.tracking_settings = TrackingSettings()
        message.tracking_settings.click_tracking = ClickTracking(True, True)
        message.tracking_settings.open_tracking = OpenTracking(True)
        
        response = sendgrid.send(message)
        
        # Update database
        supabase.table('prospects').update({
            'sequence_step': step + 1,  # Move to next step
            'last_followup_at': datetime.now().isoformat()
        }).eq('id', prospect['id']).execute()
        
        print(f"✅ Follow-up #{step} sent to {prospect['email']} ({prospect.get('company', 'Unknown')})")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send follow-up to {prospect['email']}: {e}")
        return False


def main():
    """Main execution"""
    print("=" * 60)
    print("🔄 I AM CFO FOLLOW-UP BOT - Daily Cash Flow Follow-ups")
    print("=" * 60)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📅 TIMING: 2 days → 3 days → 3 days")
    print(f"🎯 Focus: Reinforce cash flow pain + real-time solutions")
    print("-" * 60)
    
    total_sent = 0
    
    # Process follow-up #1 (2 days after initial)
    print("\n📧 Processing Follow-up #1 (2 days after initial)...")
    prospects_step1 = get_prospects_for_followup(1)
    print(f"   Found {len(prospects_step1)} prospects")
    
    for i, prospect in enumerate(prospects_step1, 1):
        print(f"   [{i}/{len(prospects_step1)}] {prospect['email']}...", end=" ")
        if send_followup(prospect, 1):
            total_sent += 1
        
        # Rate limiting
        if i < len(prospects_step1):
            time.sleep(2)  # 2 seconds between emails
    
    # Process follow-up #2 (3 days after follow-up #1)
    print("\n📧 Processing Follow-up #2 (3 days after follow-up #1)...")
    prospects_step2 = get_prospects_for_followup(2)
    print(f"   Found {len(prospects_step2)} prospects")
    
    for i, prospect in enumerate(prospects_step2, 1):
        print(f"   [{i}/{len(prospects_step2)}] {prospect['email']}...", end=" ")
        if send_followup(prospect, 2):
            total_sent += 1
        
        # Rate limiting
        if i < len(prospects_step2):
            time.sleep(2)
    
    # Process follow-up #3 (3 days after follow-up #2)
    print("\n📧 Processing Follow-up #3 (3 days after follow-up #2)...")
    prospects_step3 = get_prospects_for_followup(3)
    print(f"   Found {len(prospects_step3)} prospects")
    
    for i, prospect in enumerate(prospects_step3, 1):
        print(f"   [{i}/{len(prospects_step3)}] {prospect['email']}...", end=" ")
        if send_followup(prospect, 3):
            total_sent += 1
        
        # Rate limiting
        if i < len(prospects_step3):
            time.sleep(2)
    
    print("\n" + "=" * 60)
    print("✅ FOLLOW-UP COMPLETE!")
    print("=" * 60)
    print(f"   Total sent: {total_sent}")
    print(f"   Follow-up #1 (2 days): {len(prospects_step1)} prospects")
    print(f"   Follow-up #2 (3 days): {len(prospects_step2)} prospects")
    print(f"   Follow-up #3 (3 days): {len(prospects_step3)} prospects")
    print("=" * 60)


if __name__ == '__main__':
    main()
