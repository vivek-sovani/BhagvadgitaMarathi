#!/usr/bin/env python3
"""
Daily Gita concept emailer.
Reads whatsapp-links .md files, picks the next concept by day count
from START_DATE, and mails it via Gmail SMTP.
"""

import os
import re
import smtplib
from datetime import date, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ── Config ────────────────────────────────────────────────────────────────────
# Day 0: first concept goes out on this date. Change if you want a different start.
START_DATE = date(2026, 4, 30)

# Adhyay files in serial order (add new adhyay files here as they are created)
ADHYAY_FILES = [
    'adhyay1-whatsapp-links.md',
    'adhyay2-whatsapp-links.md',
    'adhyay3-whatsapp-links.md',
    'adhyay4-whatsapp-links.md',
    'adhyay5-whatsapp-links.md',
    'adhyay6-whatsapp-links.md',
    'adhyay7-whatsapp-links.md',
    'adhyay11-whatsapp-links.md',
]

SEPARATOR = '━━━━━━━━━━━━━━━━━━━━━━━'

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ── Parse .md files ───────────────────────────────────────────────────────────
def parse_concepts(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, encoding='utf-8') as f:
        content = f.read()
    blocks = content.split(SEPARATOR)
    concepts = []
    for block in blocks:
        block = block.strip()
        if '📅' in block and 'https://' in block:
            concepts.append(block)
    return concepts


def get_all_concepts():
    all_concepts = []
    for filename in ADHYAY_FILES:
        path = os.path.join(REPO_ROOT, filename)
        all_concepts.extend(parse_concepts(path))
    return all_concepts


# ── Format email ──────────────────────────────────────────────────────────────
def whatsapp_to_html(text):
    # Bold *text* → <strong>
    text = re.sub(r'\*([^*\n]+)\*', r'<strong>\1</strong>', text)
    # Italic _text_ → <em>
    text = re.sub(r'_([^_\n]+)_', r'<em>\1</em>', text)
    # Clickable links
    text = re.sub(r'(https://\S+)', r'<a href="\1" style="color:#D97706">\1</a>', text)
    # Line breaks
    text = text.replace('\n', '<br>')
    return text


def build_html(block, day_num, total):
    content_html = whatsapp_to_html(block)
    today_str = datetime.now().strftime('%d %b %Y')
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#FAFAF7;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr><td align="center" style="padding:32px 16px;">
      <table width="600" cellpadding="0" cellspacing="0"
             style="background:#fff;border-radius:12px;border:1px solid #E7E5E4;
                    box-shadow:0 2px 10px rgba(0,0,0,0.07);overflow:hidden;">

        <!-- Header -->
        <tr><td style="background:#D97706;padding:20px 28px;text-align:center;">
          <span style="font-size:2rem;line-height:1;">🕉️</span>
          <h1 style="margin:8px 0 0;color:#fff;font-size:1.1rem;font-weight:700;
                     letter-spacing:0.02em;">गीता-ज्ञानेश्वरी — आधुनिक जीवनदर्शन</h1>
          <p style="margin:4px 0 0;color:rgba(255,255,255,0.82);font-size:0.78rem;">
            {today_str} &nbsp;·&nbsp; संकल्पना {day_num} / {total}
          </p>
        </td></tr>

        <!-- Body -->
        <tr><td style="padding:28px 32px;font-size:1rem;line-height:1.85;color:#1C1917;">
          {content_html}
        </td></tr>

        <!-- Footer -->
        <tr><td style="border-top:1px solid #E7E5E4;padding:14px 28px;
                       text-align:center;color:#78716C;font-size:0.75rem;">
          🕉️ &nbsp;। श्रीकृष्णार्पणमस्तु ।
        </td></tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""


# ── Send via Gmail ─────────────────────────────────────────────────────────────
def send_email(gmail_addr, app_password, subject, html_body, plain_body):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From']    = f'गीता-ज्ञानेश्वरी <{gmail_addr}>'
    msg['To']      = gmail_addr
    msg.attach(MIMEText(plain_body, 'plain',  'utf-8'))
    msg.attach(MIMEText(html_body,  'html',   'utf-8'))
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(gmail_addr, app_password)
        server.sendmail(gmail_addr, gmail_addr, msg.as_string())


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    gmail_addr    = os.environ['GMAIL_ADDRESS']
    app_password  = os.environ['GMAIL_APP_PASSWORD']

    concepts = get_all_concepts()
    if not concepts:
        raise RuntimeError('No concept blocks found — check md files.')

    total     = len(concepts)
    today     = date.today()
    day_index = (today - START_DATE).days % total
    day_num   = day_index + 1
    block     = concepts[day_index]

    # Extract concept title (3rd bold segment: after adhyay name and संकल्पना X/Y)
    bold_parts = re.findall(r'\*([^*\n]+)\*', block)
    concept_title = bold_parts[2] if len(bold_parts) > 2 else f'संकल्पना {day_num}'

    subject = f'🕉️ गीता | {concept_title}'

    html_body  = build_html(block, day_num, total)
    plain_body = block

    send_email(gmail_addr, app_password, subject, html_body, plain_body)
    print(f'✓ Sent concept {day_num}/{total}: {concept_title}')


if __name__ == '__main__':
    main()
