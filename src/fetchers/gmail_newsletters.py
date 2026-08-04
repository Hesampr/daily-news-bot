"""Gmail newsletter fetcher using Google API."""
import os
import json
import re
from datetime import datetime, timedelta
from typing import Tuple, List

# Gmail API imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.service_account import Credentials
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    GMAIL_API_AVAILABLE = True
except ImportError:
    GMAIL_API_AVAILABLE = False


GMAIL_CREDENTIALS_PATH = os.environ.get("GMAIL_CREDENTIALS_JSON", "").strip()
GMAIL_USER_EMAIL = os.environ.get("GMAIL_USER_EMAIL", "").strip()
GMAIL_NEWSLETTER_QUERY = os.environ.get("GMAIL_NEWSLETTER_QUERY", "label:newsletters from:newsletter").strip()

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def is_configured() -> bool:
    """Check if Gmail is properly configured."""
    if not GMAIL_API_AVAILABLE:
        return False
    return bool(GMAIL_CREDENTIALS_PATH and os.path.exists(GMAIL_CREDENTIALS_PATH))


def _get_gmail_service():
    """Build and return Gmail API service."""
    if not is_configured():
        return None
    try:
        creds = service_account.Credentials.from_service_account_file(
            GMAIL_CREDENTIALS_PATH, scopes=SCOPES
        )
        service = build("gmail", "v1", credentials=creds)
        return service
    except Exception as e:
        print(f"⚠️ Gmail API service build failed: {e}")
        return None


def _extract_text_from_payload(payload: dict) -> str:
    """Recursively extract text from MIME payload."""
    text = ""
    if "parts" in payload:
        for part in payload["parts"]:
            text += _extract_text_from_payload(part)
    elif "data" in payload:
        import base64
        try:
            text = base64.urlsafe_b64decode(payload["data"]).decode("utf-8", errors="ignore")
        except Exception:
            pass
    return text


def _extract_links_from_html(html_text: str) -> List[str]:
    """Extract URLs from HTML/text content."""
    # Find href links
    href_pattern = r'href=["\'](https?://[^\s"\'<>]+)'
    links = re.findall(href_pattern, html_text, re.IGNORECASE)
    
    # Also find bare URLs
    url_pattern = r'https?://[^\s<>"\'{}|\\^`\[\]]*'
    bare_urls = re.findall(url_pattern, html_text)
    
    # Combine and deduplicate
    all_links = list(set(links + bare_urls))
    # Filter out tracking/unsubscribe links
    filtered = [
        url for url in all_links
        if not any(
            skip in url.lower()
            for skip in ["unsubscribe", "preferences", "manage", "newsletter/settings"]
        )
    ]
    return filtered[:5]  # Limit to 5 links per email


def _clean_subject(subject: str) -> str:
    """Clean email subject for article title."""
    # Remove common prefixes
    subject = re.sub(r"^\[.*?\]\s*", "", subject)
    subject = re.sub(r"^(FW|Re|Fwd):\s*", "", subject, flags=re.IGNORECASE)
    return subject.strip()


def fetch() -> Tuple[List[dict], List[str]]:
    """Fetch newsletters from Gmail.
    
    Returns:
        (articles: list of dicts, errors: list of strings)
    """
    articles = []
    errors = []
    
    if not is_configured():
        return [], ["Gmail not configured (missing credentials or config)"]
    
    try:
        service = _get_gmail_service()
        if not service:
            return [], ["Gmail API service unavailable"]
        
        # Search for newsletter emails (last 3 days by default)
        query = GMAIL_NEWSLETTER_QUERY or "label:newsletters"
        # Add time constraint
        three_days_ago = (datetime.utcnow() - timedelta(days=3)).strftime("%Y/%m/%d")
        query_with_date = f"{query} after:{three_days_ago}"
        
        print(f"🔍 Gmail search query: {query_with_date}")
        
        results = service.users().messages().list(
            userId="me", q=query_with_date, maxResults=20
        ).execute()
        
        messages = results.get("messages", [])
        if not messages:
            print("ℹ️ No newsletter emails found in the last 3 days")
            return [], []
        
        for msg in messages:
            try:
                msg_data = service.users().messages().get(userId="me", id=msg["id"], format="full").execute()
                headers = msg_data["payload"].get("headers", [])
                
                # Extract subject, from, date
                subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
                from_addr = next((h["value"] for h in headers if h["name"] == "From"), "Unknown")
                date_str = next((h["value"] for h in headers if h["name"] == "Date"), "")
                
                # Extract body text
                body_text = _extract_text_from_payload(msg_data["payload"])
                
                # Extract links
                links = _extract_links_from_html(body_text)
                if not links:
                    continue  # Skip if no links found
                
                # Create article entries (one per link, or one combined)
                title = _clean_subject(subject)
                
                # Use first link as primary
                article = {
                    "title": title,
                    "link": links[0],
                    "source": f"Gmail Newsletter ({from_addr})",
                    "feed": "Gmail Newsletters",
                    "date": date_str[:10] if date_str else datetime.utcnow().strftime("%Y-%m-%d"),
                    "description": f"From: {from_addr}\nLinks: {', '.join(links)}",
                    "region": "global",
                }
                articles.append(article)
                
                # Also add secondary links as separate low-confidence mentions
                for link in links[1:]:
                    article_secondary = {
                        "title": title,
                        "link": link,
                        "source": f"Gmail Newsletter ({from_addr})",
                        "feed": "Gmail Newsletters",
                        "date": date_str[:10] if date_str else datetime.utcnow().strftime("%Y-%m-%d"),
                        "description": f"Additional link from: {from_addr}",
                        "region": "global",
                    }
                    articles.append(article_secondary)
            
            except Exception as e:
                errors.append(f"Failed to parse email {msg['id']}: {str(e)}")
                continue
        
        print(f"✅ Gmail newsletters: {len(articles)} article links extracted from {len(messages)} emails")
        return articles, errors
    
    except Exception as e:
        error_msg = f"Gmail fetch error: {str(e)}"
        print(f"⚠️ {error_msg}")
        return [], [error_msg]
