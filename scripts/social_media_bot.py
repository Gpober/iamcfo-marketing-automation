#!/usr/bin/env python3
"""
I AM CFO - Social Media Automation Bot
Automatically generates and posts LinkedIn content using Claude AI
Author: Greg Pober
"""

import os
import sys
from datetime import datetime, date, time
from supabase import create_client, Client
import anthropic
import requests
import json

# Initialize clients
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
LINKEDIN_ACCESS_TOKEN = os.getenv('LINKEDIN_ACCESS_TOKEN')  # We'll get this later
LINKEDIN_ORG_ID = os.getenv('LINKEDIN_ORG_ID')  # Your company page ID

# Validate environment variables
if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("❌ ERROR: Supabase credentials not set!")
    sys.exit(1)

if not ANTHROPIC_API_KEY:
    print("❌ ERROR: Anthropic API key not set!")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# I AM CFO Brand Voice
BRAND_VOICE = """
You are the social media voice for I AM CFO, a financial dashboard platform that transforms QuickBooks and Xero data into real-time insights.

Brand personality:
- Confident but not arrogant
- Direct and punchy
- Empathetic to business owner pain points
- Occasionally uses emojis (sparingly - 1-2 per post)
- Conversational, not corporate
- Focus on transformation: data → decisions

Key messages:
- Stop spending hours in Excel
- Real-time vs month-end
- AI-powered insights
- 3 seconds vs 3 hours
- QuickBooks/Xero integration
- Built for $2M-$25M businesses

Avoid:
- Being salesy or pushy
- Overusing buzzwords
- Corporate jargon
- Fake enthusiasm
"""

def get_pending_posts():
    """Get posts scheduled for today that haven't been posted yet"""
    try:
        today = date.today().isoformat()
        current_time = datetime.now().time()
        
        response = supabase.table('social_media_posts')\
            .select('*')\
            .eq('status', 'pending')\
            .eq('scheduled_date', today)\
            .eq('platform', 'linkedin')\
            .execute()
        
        # Filter by time (should be at or past scheduled time)
        posts = []
        for post in response.data:
            scheduled_time_str = post.get('scheduled_time', '09:00:00')
            scheduled_time = datetime.strptime(scheduled_time_str, '%H:%M:%S').time()
            if current_time >= scheduled_time:
                posts.append(post)
        
        return posts
    except Exception as e:
        print(f"❌ Error fetching pending posts: {e}")
        return []

def generate_post_with_claude(post_topic):
    """Use Claude to generate LinkedIn post from topic"""
    try:
        message = claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": f"""{BRAND_VOICE}

Create a LinkedIn post for I AM CFO based on this topic:
"{post_topic}"

Requirements:
1. 100-200 words (LinkedIn sweet spot)
2. Hook in first line (make them stop scrolling)
3. Use line breaks for readability (2-3 word lines)
4. Include a clear call-to-action
5. Add 3-5 relevant hashtags at the end
6. Optional: Use 1-2 emojis if they fit naturally
7. Professional but conversational tone
8. Focus on business owner pain points

DO NOT include:
- Quotes around the entire post
- "Here's a LinkedIn post:" or similar preamble
- Markdown formatting
- Your explanations

Just write the post exactly as it should appear on LinkedIn.

LinkedIn post:"""
            }]
        )
        
        post_content = message.content[0].text.strip()
        
        # Remove any markdown or quotes if present
        post_content = post_content.replace('```', '').strip()
        if post_content.startswith('"') and post_content.endswith('"'):
            post_content = post_content[1:-1]
        
        return post_content
        
    except Exception as e:
        print(f"❌ Claude generation failed: {e}")
        return None

def post_to_linkedin(content, image_url=None):
    """Post content to LinkedIn company page"""
    
    # Check if LinkedIn credentials are set
    if not LINKEDIN_ACCESS_TOKEN or not LINKEDIN_ORG_ID:
        print("⚠️  LinkedIn API not configured yet - would post:")
        print("-" * 60)
        print(content)
        print("-" * 60)
        return {
            'success': False,
            'error': 'LinkedIn API not configured',
            'post_url': None
        }
    
    try:
        # LinkedIn API endpoint for organization posts
        url = "https://api.linkedin.com/v2/ugcPosts"
        
        headers = {
            "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        # Build post payload
        post_data = {
            "author": f"urn:li:organization:{LINKEDIN_ORG_ID}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        # Add image if provided
        if image_url:
            post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
            post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                {
                    "status": "READY",
                    "media": image_url
                }
            ]
        
        # Post to LinkedIn
        response = requests.post(url, headers=headers, json=post_data)
        
        if response.status_code in [200, 201]:
            post_id = response.json().get('id')
            post_url = f"https://www.linkedin.com/feed/update/{post_id}"
            return {
                'success': True,
                'post_url': post_url,
                'error': None
            }
        else:
            return {
                'success': False,
                'error': f"LinkedIn API error: {response.status_code} - {response.text}",
                'post_url': None
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'post_url': None
        }

def update_post_status(post_id, status, generated_content=None, post_url=None, error=None):
    """Update post status in database"""
    try:
        update_data = {
            'status': status,
            'updated_at': datetime.now().isoformat()
        }
        
        if generated_content:
            update_data['generated_content'] = generated_content
        
        if post_url:
            update_data['post_url'] = post_url
            update_data['posted_at'] = datetime.now().isoformat()
        
        if error:
            update_data['error_message'] = error
        
        supabase.table('social_media_posts')\
            .update(update_data)\
            .eq('id', post_id)\
            .execute()
        
        return True
    except Exception as e:
        print(f"❌ Error updating post status: {e}")
        return False

def main():
    """Main execution"""
    print("=" * 60)
    print("🤖 I AM CFO SOCIAL MEDIA BOT")
    print("=" * 60)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    # Get pending posts
    posts = get_pending_posts()
    
    if not posts:
        print("ℹ️  No posts scheduled for now.")
        print("\nTo add posts:")
        print("  1. Go to your admin panel")
        print("  2. Add post topics with scheduled dates")
        print("  3. This bot will auto-generate and post them!")
        return
    
    print(f"📧 Found {len(posts)} pending post(s)")
    print("-" * 60)
    
    posted_count = 0
    failed_count = 0
    
    for i, post in enumerate(posts, 1):
        print(f"\n[{i}/{len(posts)}] Processing: {post['post_topic'][:60]}...")
        
        # Generate post with Claude
        print("  🤖 Generating post with Claude AI...")
        generated_content = generate_post_with_claude(post['post_topic'])
        
        if not generated_content:
            print(f"  ❌ Failed to generate post")
            update_post_status(post['id'], 'failed', error='Claude generation failed')
            failed_count += 1
            continue
        
        print(f"  ✅ Generated {len(generated_content)} characters")
        
        # Post to LinkedIn
        print("  📤 Posting to LinkedIn...")
        result = post_to_linkedin(generated_content, post.get('image_url'))
        
        if result['success']:
            print(f"  ✅ Posted successfully!")
            if result['post_url']:
                print(f"  🔗 {result['post_url']}")
            update_post_status(
                post['id'],
                'posted',
                generated_content=generated_content,
                post_url=result['post_url']
            )
            posted_count += 1
        else:
            print(f"  ❌ Failed to post: {result['error']}")
            update_post_status(
                post['id'],
                'failed',
                generated_content=generated_content,
                error=result['error']
            )
            failed_count += 1
    
    print("\n" + "=" * 60)
    print("✅ SOCIAL MEDIA BOT COMPLETE!")
    print("=" * 60)
    print(f"   Posted: {posted_count}")
    print(f"   Failed: {failed_count}")
    if posted_count > 0:
        print(f"   Check LinkedIn: https://www.linkedin.com/company/i-am-cfo")
    print("=" * 60)

if __name__ == '__main__':
    main()
