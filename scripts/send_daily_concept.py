#!/usr/bin/env python3
"""
Daily Gita concept emailer.
Sends trigger text + WhatsApp post for the next concept in serial order.
Posts  : adhyayX-whatsapp-links.md files
Triggers: js/triggers.js  (GITA_TRIGGERS[adhyayId][conceptId])
"""

import json
import os
import re
import smtplib
import subprocess
from datetime import date, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ── Config ────────────────────────────────────────────────────────────────────
# Adhyay 2 concept 6 is at index 12 → START_DATE set so May 1 2026 = day 12
START_DATE = date(2026, 4, 19)

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
REPO_ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── Devanagari helpers ────────────────────────────────────────────────────────
_DEVA = '०१२३४५६७८९'

def deva_to_int(s):
    return int(''.join(str(_DEVA.index(c)) for c in s if c in _DEVA))


# ── Parse WhatsApp post blocks ────────────────────────────────────────────────
def parse_concepts(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, encoding='utf-8') as f:
        content = f.read()
    concepts = []
    for block in content.split(SEPARATOR):
        block = block.strip()
        if '📅' in block and 'https://' in block:
            concepts.append(block)
    return concepts


def get_all_concepts():
    all_concepts = []
    for filename in ADHYAY_FILES:
        all_concepts.extend(parse_concepts(os.path.join(REPO_ROOT, filename)))
    return all_concepts


def extract_ids(block):
    """Return (adhyay_id, concept_id) as ints from a WhatsApp post block."""
    ma = re.search(r'अध्याय\s+([०-९]+)', block)
    mc = re.search(r'संकल्पना\s+([०-९]+)/', block)
    adhyay_id  = deva_to_int(ma.group(1)) if ma else None
    concept_id = deva_to_int(mc.group(1)) if mc else None
    return adhyay_id, concept_id


# ── Load triggers from JS ─────────────────────────────────────────────────────
def load_triggers():
    node_script = """
const fs = require('fs');
eval(fs.readFileSync('js/triggers.js','utf8')
  .replace('const GITA_TRIGGERS','global.GITA_TRIGGERS'));
console.log(JSON.stringify(GITA_TRIGGERS));
"""
    result = subprocess.run(
        ['node', '-e', node_script],
        capture_output=True, text=True, cwd=REPO_ROOT
    )
    if result.returncode != 0 or not result.stdout.strip():
        return {}
    return json.loads(result.stdout)


def get_trigger(triggers, adhyay_id, concept_id):
    if not triggers or adhyay_id is None or concept_id is None:
        return None
    adhyay_data = triggers.get(str(adhyay_id))
    if not adhyay_data:
        return None
    return adhyay_data.get(str(concept_id))


# ── Email builder ─────────────────────────────────────────────────────────────
def whatsapp_to_html(text):
    text = re.sub(r'\*([^*\n]+)\*', r'<strong>\1</strong>', text)
    text = re.sub(r'_([^_\n]+)_',   r'<em>\1</em>',         text)
    text = re.sub(r'(https://\S+)',  r'<a href="\1" style="color:#D97706;font-weight:600">\1</a>', text)
    return text.replace('\n', '<br>')


def build_html(post_block, trigger, day_num, total):
    today_str     = datetime.now().strftime('%d %b %Y')
    post_html     = whatsapp_to_html(post_block)

    # Trigger section (may be absent for some concepts)
    trigger_html = ''
    if trigger:
        paras_html = ''.join(
            f'<p style="margin:0 0 10px;line-height:1.8;">{p}</p>'
            for p in trigger['paras']
        )
        cta_html = (
            f'<p style="margin:14px 0 0;color:#B45309;font-weight:600;'
            f'font-size:0.92rem;line-height:1.7;">{trigger["cta"]}</p>'
            if trigger.get('cta') else ''
        )
        trigger_html = f"""
        <!-- Trigger -->
        <tr><td style="padding:24px 32px 0;">
          <div style="background:#FEF3C7;border-left:4px solid #D97706;
                      border-radius:0 8px 8px 0;padding:18px 20px;">
            <p style="margin:0 0 12px;font-size:0.7rem;font-weight:700;
                      letter-spacing:0.12em;text-transform:uppercase;color:#92400E;">
              💡 आजचा विचार
            </p>
            {paras_html}
            {cta_html}
          </div>
        </td></tr>
        <tr><td style="padding:16px 32px 0;">
          <hr style="border:none;border-top:1px solid #E7E5E4;margin:0;">
        </td></tr>"""

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body style="margin:0;padding:0;background:#FAFAF7;
             font-family:'Segoe UI',Arial,sans-serif;color:#1C1917;">
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr><td align="center" style="padding:28px 12px;">
      <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;
             background:#fff;border-radius:12px;border:1px solid #E7E5E4;
             box-shadow:0 2px 10px rgba(0,0,0,0.07);overflow:hidden;">

        <!-- Header -->
        <tr><td style="background:#D97706;padding:22px 28px;text-align:center;">
          <div style="font-size:2rem;line-height:1;">🕉️</div>
          <h1 style="margin:8px 0 0;color:#fff;font-size:1.05rem;font-weight:700;">
            गीता-ज्ञानेश्वरी — आधुनिक जीवनदर्शन
          </h1>
          <p style="margin:4px 0 0;color:rgba(255,255,255,0.82);font-size:0.78rem;">
            {today_str} &nbsp;·&nbsp; संकल्पना {day_num} / {total}
          </p>
        </td></tr>

        {trigger_html}

        <!-- WhatsApp post -->
        <tr><td style="padding:24px 32px;">
          <p style="margin:0 0 14px;font-size:0.7rem;font-weight:700;
                    letter-spacing:0.12em;text-transform:uppercase;color:#78716C;">
            📲 WhatsApp Post
          </p>
          <div style="background:#F5F4F0;border-radius:8px;padding:18px 20px;
                      font-size:0.95rem;line-height:1.85;">
            {post_html}
          </div>
        </td></tr>

        <!-- Footer -->
        <tr><td style="border-top:1px solid #E7E5E4;padding:14px 28px;
                       text-align:center;color:#78716C;font-size:0.75rem;">
          🕉️ &nbsp;। श्रीकृष्णार्पणमस्तु ।
        </td></tr>

      </table>
    </td></tr>
  </table>
</body></html>"""


def build_plain(post_block, trigger):
    parts = []
    if trigger:
        parts.append('── आजचा विचार ──')
        parts.extend(re.sub(r'<[^>]+>', '', p) for p in trigger['paras'])
        if trigger.get('cta'):
            parts.append(re.sub(r'<[^>]+>', '', trigger['cta']))
        parts.append('')
    parts.append('── WhatsApp Post ──')
    parts.append(post_block)
    return '\n'.join(parts)


# ── Send via Gmail ────────────────────────────────────────────────────────────
def send_email(gmail_addr, app_password, subject, html_body, plain_body):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From']    = f'गीता-ज्ञानेश्वरी <{gmail_addr}>'
    msg['To']      = gmail_addr
    msg.attach(MIMEText(plain_body, 'plain', 'utf-8'))
    msg.attach(MIMEText(html_body,  'html',  'utf-8'))
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(gmail_addr, app_password)
        server.sendmail(gmail_addr, gmail_addr, msg.as_string())


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    gmail_addr   = os.environ['GMAIL_ADDRESS']
    app_password = os.environ['GMAIL_APP_PASSWORD']

    concepts = get_all_concepts()
    if not concepts:
        raise RuntimeError('No concept blocks found — check md files.')

    total     = len(concepts)
    today     = date.today()
    day_index = (today - START_DATE).days % total
    day_num   = day_index + 1
    block     = concepts[day_index]

    adhyay_id, concept_id = extract_ids(block)

    triggers = load_triggers()
    trigger  = get_trigger(triggers, adhyay_id, concept_id)

    bold_parts    = re.findall(r'\*([^*\n]+)\*', block)
    concept_title = bold_parts[2] if len(bold_parts) > 2 else f'संकल्पना {day_num}'
    subject       = f'🕉️ गीता | {concept_title}'

    html_body  = build_html(block, trigger, day_num, total)
    plain_body = build_plain(block, trigger)

    send_email(gmail_addr, app_password, subject, html_body, plain_body)
    print(f'✓ Sent concept {day_num}/{total} '
          f'(adhyay {adhyay_id} concept {concept_id}): {concept_title}')


if __name__ == '__main__':
    main()
