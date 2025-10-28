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
FOLLOWUP_1_SUBJECT = "Re: Can you afford to hire that new person?"
FOLLOWUP_1_HTML = """<html>
<body style="font-family: Arial, sans-serif; font-size: 16px; line-height: 1.6; color: #333;">

<p>{first_name},</p>

<p>Quick follow-up.</p>

<p>You know that feeling when you're staring at the bank balance, trying to figure out if you can afford something?</p>

<p>Hire that person?<br>
Buy that equipment?<br>
Take on that new project?</p>

<p>Most business owners spend hours in spreadsheets trying to answer these questions.</p>

<p><strong>I AM CFO answers them in seconds.</strong></p>

<p>Real-time cash position. Burn rate. Cash flow forecast.</p>

<p>One {industry} owner told me: <em>"I spent 3 hours last month trying to figure out if I could hire. Now I just look at the dashboard. Takes 10 seconds."</em></p>

<p>Worth 15 minutes to see it?</p>

<p>👉 <a href="{tracking_link}" style="color: #0066cc; text-decoration: none;">info.iamcfo.com</a></p>

<p>— <br>
Greg Pober<br>
CEO | I AM CFO • 954-684-9011</p>

<p style="font-size: 14px; color: #666;"><strong>P.S.</strong> Still connects to QuickBooks. Still takes 30 minutes to set up. Still shows your cash position today.</p>

</body>
</html>"""


# Follow-up #2 - 3 days after follow-up #1 (Social proof + urgency)
FOLLOWUP_2_SUBJECT = "Making decisions with month-old data"
FOLLOWUP_2_HTML = """<html>
<body style="font-family: Arial, sans-serif; font-size: 16px; line-height: 1.6; color: #333;">

<p>{first_name},</p>

<p><strong>Straight talk:</strong></p>

<p>You're making hiring decisions with month-old data.<br>
You're bidding jobs with last month's costs.<br>
You're planning purchases without knowing today's cash position.</p>

<p>That's not a criticism. That's just how traditional bookkeeping works.</p>

<p>But here's what changed for one {industry} company:</p>

<p><strong>Before I AM CFO:</strong><br>
• "Can we afford this?" = 2 hours in spreadsheets<br>
• Found out about problems weeks too late<br>
• Made decisions based on guesses</p>

<p><strong>After I AM CFO:</strong><br>
• "Can we afford this?" = 10 seconds<br>
• See problems the day they start<br>
• Make decisions based on data</p>

<p>The difference? <strong>Real-time cash flow visibility.</strong></p>

<p>See it yourself: <a href="{tracking_link}" style="color: #0066cc; text-decoration: none;">info.iamcfo.com</a></p>

<p>— <br>
Greg Pober<br>
CEO | I AM CFO • 954-684-9011</p>

<p style="font-size: 14px; color: #666;"><strong>P.S.</strong> $699/month. Or keep guessing. Your call.</p>

</body>
</html>"""


# Follow-up #3 - 3 days after follow-up #2 (Final value reminder)
FOLLOWUP_3_SUBJECT = "Last one from me"
FOLLOWUP_3_HTML = """<html>
<body style="font-family: Arial, sans-serif; font-size: 16px; line-height: 1.6; color: #333;">

<p>{first_name},</p>

<p>I'll keep this short.</p>

<p>Three questions you probably asked yourself this week:</p>

<p><strong>1.</strong> "Can I afford to hire that person?"<br>
<strong>2.</strong> "Why is cash tighter than I expected?"<br>
<strong>3.</strong> "Which location/client/project is actually profitable?"</p>

<p>If you're still answering these with spreadsheets and guesswork, that's on you.</p>

<p><strong>I AM CFO gives you the answer in real-time.</strong></p>

<p>$699/month to stop guessing about your cash flow.</p>

<p>See it: <a href="{tracking_link}" style="color: #0066cc; text-decoration: none;">info.iamcfo.com</a></p>

<p>— <br>
Greg</p>

<p style="font-size: 14px; color: #666;"><strong>P.S.</strong> If you're good with month-old data and spreadsheet math, ignore this. If you want to see your cash position today, click the link.</p>

</body>
</html>"""


# ============================================================================
# INDUSTRY-SPECIFIC FOLLOW-UPS (More targeted)
# ============================================================================

INDUSTRY_FOLLOWUPS = {
    'construction': {
        'subject_1': "Re: How much can you bid on that new job?",
        'followup_1': """<html>
<body style="font-family: Arial, sans-serif; font-size: 16px; line-height: 1.6; color: #333;">

<p>{first_name},</p>

<p>Quick follow-up on that bid question.</p>

<p>You've got materials fluctuating. Labor's tight. Jobs overlapping.</p>

<p>And you're trying to figure out: <strong>"Can I afford to take on this next job?"</strong></p>

<p>Most GCs spend hours in spreadsheets trying to answer this.</p>

<p><strong>I AM CFO shows you:</strong><br>
• Real-time cash by job<br>
• What you can actually commit to<br>
• Where you're profitable vs. bleeding</p>

<p>A GC in Tampa told me: <em>"I used to spend Friday afternoons doing cash flow math. Now I check my phone. Takes 30 seconds."</em></p>

<p>See it: <a href="{tracking_link}" style="color: #0066cc; text-decoration: none;">info.iamcfo.com</a></p>

<p>— <br>
Greg Pober<br>
CEO | I AM CFO • 954-684-9011</p>

</body>
</html>""",
        
        'subject_2': "Stop bidding jobs blind",
        'followup_2': """<html>
<body style="font-family: Arial, sans-serif; font-size: 16px; line-height: 1.6; color: #333;">

<p>{first_name},</p>

<p><strong>Real talk:</strong> Are you bidding jobs based on last month's costs?</p>

<p>Materials went up 8% two weeks ago. Your bid spreadsheet doesn't know that yet.</p>

<p><strong>I AM CFO shows you real-time costs, real-time margins, real-time cash available.</strong></p>

<p>One GC found they were underbidding by 12% on concrete work. Caught it week 1 instead of month 3. Saved $40K on the next 5 jobs.</p>

<p>That's 57 months of I AM CFO paid for by one insight.</p>

<p>See your real-time job costs: <a href="{tracking_link}" style="color: #0066cc; text-decoration: none;">info.iamcfo.com</a></p>

<p>— <br>
Greg Pober<br>
CEO | I AM CFO • 954-684-9011</p>

</body>
</html>""",
        
        'subject_3': "Last chance (from me)",
        'followup_3': """<html>
<body style="font-family: Arial, sans-serif; font-size: 16px; line-height: 1.6; color: #333;">

<p>{first_name},</p>

<p>Your competitors are seeing their job profitability in real-time.</p>

<p>You'll see yours in 3 weeks when your bookkeeper closes the books.</p>

<p>The gap between you and them is growing.</p>

<p><strong>$699/month to stop flying blind.</strong></p>

<p><a href="{tracking_link}" style="color: #0066cc; text-decoration: none;">info.iamcfo.com</a></p>

<p>— <br>
Greg</p>

</body>
</html>"""
    },
    
    'restaurant': {
        'subject_1': "Re: Why does cash feel tighter than sales suggest?",
        'followup_1': """<html>
<body style="font-family: Arial, sans-serif; font-size: 16px; line-height: 1.6; color: #333;">

<p>{first_name},</p>

<p>Quick follow-up on that cash flow question.</p>

<p>Sales are up. Tables are full. But somehow cash is tight.</p>

<p>Where's it going?</p>

<p>Most restaurant owners spend hours trying to figure this out.</p>

<p><strong>I AM CFO shows you:</strong><br>
• Real-time P&L by location<br>
• Food cost percentage today (not month-end)<br>
• Which locations print money vs. bleed cash</p>

<p>A restaurant group told me: <em>"We discovered one location was losing $4K/month. Fixed it in week 1 instead of finding out in month 3."</em></p>

<p>See your real-time restaurant numbers: <a href="{tracking_link}" style="color: #0066cc; text-decoration: none;">info.iamcfo.com</a></p>

<p>— <br>
Greg Pober<br>
CEO | I AM CFO • 954-684-9011</p>

</body>
</html>""",
        
        'subject_2': "Your food cost spiked last week",
        'followup_2': """<html>
<body style="font-family: Arial, sans-serif; font-size: 16px; line-height: 1.6; color: #333;">

<p>{first_name},</p>

<p>Actually, I don't know if your food cost spiked last week.</p>

<p>But you probably don't either.</p>

<p>You'll find out in 3 weeks when your bookkeeper's report comes in.</p>

<p>By then? You've bled another 3 weeks of margin.</p>

<p><strong>I AM CFO shows food cost percentage daily. By location. In real-time.</strong></p>

<p>One 3-location group found their downtown spot was 6% higher than the other two. Fixed vendor pricing. Added $48K/year profit.</p>

<p>See your real-time food cost: <a href="{tracking_link}" style="color: #0066cc; text-decoration: none;">info.iamcfo.com</a></p>

<p>— <br>
Greg Pober<br>
CEO | I AM CFO • 954-684-9011</p>

</body>
</html>""",
        
        'subject_3': "Closing your file",
        'followup_3': """<html>
<body style="font-family: Arial, sans-serif; font-size: 16px; line-height: 1.6; color: #333;">

<p>{first_name},</p>

<p>No response — I get it.</p>

<p>If you ever want to see which locations are actually profitable (in real-time, not month-end), you know where to find me.</p>

<p><a href="{tracking_link}" style="color: #0066cc; text-decoration: none;">info.iamcfo.com</a></p>

<p>— <br>
Greg</p>

</body>
</html>"""
    },
    
    'hvac': {
        'subject_1': "Re: Can you afford that new truck?",
        'followup_1': """<html>
<body style="font-family: Arial, sans-serif; font-size: 16px; line-height: 1.6; color: #333;">

<p>{first_name},</p>

<p>Quick follow-up on that truck question.</p>

<p>You need equipment. Business is good. But is cash actually available?</p>

<p>Most HVAC owners spend Friday doing mental math trying to figure this out.</p>

<p><strong>I AM CFO shows you:</strong><br>
• Today's cash position<br>
• This week's burn rate<br>
• 90-day cash flow projection</p>

<p>An HVAC company in Miami told me: <em>"We saw we had $65K available. Bought 2 trucks. Took on 40% more jobs. Grew faster than we thought possible."</em></p>

<p>See your real-time cash position: <a href="{tracking_link}" style="color: #0066cc; text-decoration: none;">info.iamcfo.com</a></p>

<p>— <br>
Greg Pober<br>
CEO | I AM CFO • 954-684-9011</p>

</body>
</html>""",
        
        'subject_2': "Your cash is tighter than it should be",
        'followup_2': """<html>
<body style="font-family: Arial, sans-serif; font-size: 16px; line-height: 1.6; color: #333;">

<p>{first_name},</p>

<p>You're booked out 3 weeks. Revenue looks good.</p>

<p>But cash? Cash feels tight.</p>

<p>Why?</p>

<p>Most HVAC owners don't know because they're looking at month-old data.</p>

<p><strong>I AM CFO shows you real-time:</strong><br>
• Where cash is going (A/P, payroll, materials)<br>
• What's coming in (A/R aging, payment schedule)<br>
• What you actually have available today</p>

<p>One HVAC company found they were sitting on $35K in parts inventory they didn't need. Liquidated it. Freed up cash for the trucks they did need.</p>

<p>See where your cash is going: <a href="{tracking_link}" style="color: #0066cc; text-decoration: none;">info.iamcfo.com</a></p>

<p>— <br>
Greg Pober<br>
CEO | I AM CFO • 954-684-9011</p>

</body>
</html>""",
        
        'subject_3': "Equipment or wait?",
        'followup_3': """<html>
<body style="font-family: Arial, sans-serif; font-size: 16px; line-height: 1.6; color: #333;">

<p>{first_name},</p>

<p>That equipment question isn't going away.</p>

<p>You can keep guessing about cash availability.</p>

<p>Or you can see it in real-time.</p>

<p><strong>$699/month vs. guessing wrong on a $50K decision.</strong></p>

<p><a href="{tracking_link}" style="color: #0066cc; text-decoration: none;">info.iamcfo.com</a></p>

<p>— <br>
Greg</p>

</body>
</html>"""
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
        return None, None
    
    industry_lower = industry.lower()
    
    # Map step to followup key
    subject_key = f'subject_{step}'
    followup_key = f'followup_{step}'
    
    for key, templates in INDUSTRY_FOLLOWUPS.items():
        if key in industry_lower:
            if subject_key in templates and followup_key in templates:
                return templates[subject_key], templates[followup_key]
    
    return None, None


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
        industry_subject, industry_template = get_industry_followup(industry, step)
        
        if industry_template:
            # Use industry-specific template
            subject = industry_subject
            html_body = industry_template.format(
                first_name=first_name,
                industry=industry,
                tracking_link=tracking_link
            )
        else:
            # Use generic follow-up
            if step == 1:
                subject = FOLLOWUP_1_SUBJECT
                html_body = FOLLOWUP_1_HTML
            elif step == 2:
                subject = FOLLOWUP_2_SUBJECT
                html_body = FOLLOWUP_2_HTML
            else:
                subject = FOLLOWUP_3_SUBJECT
                html_body = FOLLOWUP_3_HTML
            
            html_body = html_body.format(
                first_name=first_name,
                industry=industry if industry else 'business',
                tracking_link=tracking_link
            )
        
        # Send HTML email
        message = Mail(
            from_email=(SENDER_EMAIL, SENDER_NAME),
            to_emails=prospect['email'],
            subject=subject,
            html_content=html_body  # Changed from plain_text_content to html_content
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
