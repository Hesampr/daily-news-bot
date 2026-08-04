"""Telegram message sender for daily news bot."""
import os
import requests
from typing import Tuple, List

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "").strip()


def is_configured() -> bool:
    """Check if Telegram is configured."""
    return bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)


def send_message(message_text: str, parse_mode: str = "HTML") -> Tuple[bool, str]:
    """Send message to Telegram chat.
    
    Args:
        message_text: Message content (plain text or HTML if parse_mode=HTML)
        parse_mode: 'HTML', 'Markdown', or 'MarkdownV2'
    
    Returns:
        (success: bool, response_text: str)
    """
    if not is_configured():
        return False, "Telegram not configured (missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID)"
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message_text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True,
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=15)
        if resp.status_code == 200:
            return True, "Message sent successfully"
        else:
            return False, f"Telegram API error: {resp.status_code} {resp.text}"
    except Exception as e:
        return False, f"Failed to send telegram: {str(e)}"


def format_for_telegram(message_text: str) -> str:
    """Format Slack-style message for Telegram.
    
    Converts markdown-like formatting:
    - *text* → <b>text</b> (bold)
    - plain bullet list → Telegram-friendly format
    
    Args:
        message_text: Raw message text (Slack format)
    
    Returns:
        Telegram-formatted HTML text
    """
    import re
    
    # Convert *category* headers to bold
    text = re.sub(r'\*([^*]+)\*', r'<b>\1</b>', message_text)
    
    # Convert links from slack format <url|title> to title (url)
    text = re.sub(r'<([^|]+)\|([^>]+)>', r'\2', text)
    
    # Escape remaining HTML special chars (but preserve our tags)
    def escape_html(m):
        chars = m.group(1)
        chars = chars.replace("&", "&amp;")
        chars = chars.replace("<", "&lt;")
        chars = chars.replace(">", "&gt;")
        chars = chars.replace('"', "&quot;")
        return chars
    
    # Only escape text outside of tags
    parts = re.split(r'(<[^>]+>)', text)
    for i in range(len(parts)):
        if not parts[i].startswith('<'):
            parts[i] = escape_html(re.match(r'.*', parts[i]))
    text = ''.join(parts)
    
    return text


def split_message(message_text: str, max_length: int = 4096) -> List[str]:
    """Split message if it exceeds Telegram's max length.
    
    Args:
        message_text: Message to split
        max_length: Telegram's max message length (default 4096)
    
    Returns:
        List of message chunks
    """
    if len(message_text) <= max_length:
        return [message_text]
    
    chunks = []
    lines = message_text.split('\n')
    current_chunk = []
    current_length = 0
    
    for line in lines:
        line_len = len(line) + 1  # +1 for newline
        if current_length + line_len > max_length and current_chunk:
            chunks.append('\n'.join(current_chunk))
            current_chunk = [line]
            current_length = line_len
        else:
            current_chunk.append(line)
            current_length += line_len
    
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    
    return chunks


def send_aggregated_news(message_text: str) -> Tuple[bool, str]:
    """Send aggregated news message to Telegram.
    
    Handles formatting and message splitting if needed.
    
    Args:
        message_text: Formatted news message (Slack style)
    
    Returns:
        (success: bool, details: str)
    """
    if not is_configured():
        return False, "Telegram not configured"
    
    formatted = format_for_telegram(message_text)
    chunks = split_message(formatted, max_length=4096)
    
    if not chunks:
        return False, "Empty message"
    
    all_success = True
    results = []
    
    for i, chunk in enumerate(chunks, 1):
        success, msg = send_message(chunk, parse_mode="HTML")
        results.append(msg)
        if not success:
            all_success = False
            print(f"⚠️ Telegram chunk {i}/{len(chunks)} failed: {msg}")
        else:
            print(f"✅ Telegram chunk {i}/{len(chunks)} sent")
    
    detail = f"{len(chunks)} chunk(s) sent" + (f" with some failures" if not all_success else "")
    return all_success, detail
