#!/usr/bin/env python3
"""
Generate OG shim pages and compressed thumbnails for adhyays 2-6.
Run from the project root: python3 generate_og.py
"""
import os, subprocess, re

BASE_URL = "https://vivek-sovani.github.io/BhagvadgitaMarathi"
PROJECT  = os.path.dirname(os.path.abspath(__file__))

# ── Concept data ──────────────────────────────────────────────────────────────
ADHYAYS = [
    {
        "id": 2, "number": "२", "name": "सांख्ययोग",
        "concepts": [
            (1, "🔥", "\u201cहे दुबळेपण सोड!\u201d — कृष्णाची प्रेमळ पण ठाम हाक"),
            (2, "🪔", "ज्ञानी शोक करत नाही — सांख्याचा पाया"),
            (3, "♾",  "आत्मा अमर आहे — चार शक्तींपलीकडे"),
            (4, "👘", "वासांसि जीर्णानि — कपड्यांची उपमा"),
            (5, "⚡", "कर्मण्येवाधिकारस्ते — निष्काम कर्मयोगाचा महाश्लोक"),
            (6, "🎯", "बुद्धियोग — व्यवसायात्मिका बुद्धी"),
            (7, "🌊", "स्थितप्रज्ञ — कासव आणि समुद्र उपमा"),
        ]
    },
    {
        "id": 3, "number": "३", "name": "कर्मयोग",
        "concepts": [
            (1,  "⚖️", "सांख्य की कर्मयोग"),
            (2,  "⚙️", "कर्म अनिवार्य"),
            (3,  "🔥", "यज्ञ — परस्पर-पोषण तत्त्व"),
            (4,  "🌿", "यज्ञ-पर्जन्य-अन्न — विश्वचक्र"),
            (5,  "👑", "लोकसंग्रह"),
            (6,  "🎭", "आसक्त विरुद्ध अनासक्त कर्मी"),
            (7,  "🕉️","ईश्वरार्पण"),
            (8,  "🌳", "स्वधर्म विरुद्ध परधर्म"),
            (9,  "🎯", "राग-द्वेष — लपलेले शत्रू"),
            (10, "⚔️", "काम-क्रोध — महाशत्रू"),
            (11, "🪜", "इंद्रिय निग्रह — श्रेष्ठता क्रम"),
            (12, "🔥", "ज्ञान झाकणारा काम"),
        ]
    },
    {
        "id": 4, "number": "४", "name": "ज्ञानयोग",
        "concepts": [
            (1,  "🌅", "अवताराचं रहस्य"),
            (2,  "⚡", "ईश्वराचं निर्लिप्त कर्म"),
            (3,  "🔍", "कर्म-अकर्म-विकर्म"),
            (4,  "🔥", "यज्ञाचे प्रकार"),
            (5,  "✨", "ज्ञानाग्नी"),
            (6,  "💎", "ज्ञानाची पवित्रता"),
            (7,  "🌊", "श्रद्धा आणि संशय"),
            (8,  "👁",  "पंडित समदर्शी"),
            (9,  "🌈", "ये यथा मां प्रपद्यन्ते"),
            (10, "🌟", "ज्ञानयोग — सार"),
        ]
    },
    {
        "id": 5, "number": "५", "name": "कर्मसंन्यासयोग",
        "concepts": [
            (1,  "⚖️", "संन्यास की कर्मयोग"),
            (2,  "🔗", "सांख्य आणि योग"),
            (3,  "🌿", "योगयुक्त विशुद्धात्मा"),
            (4,  "🌸", "कर्मसंन्यासी"),
            (5,  "🛠️","शरीर-मन-बुद्धी"),
            (6,  "🏰", "नवद्वारपुर"),
            (7,  "⚡", "ईश्वर कर्ता नाही"),
            (8,  "☀️", "ज्ञान हे सूर्यासारखे"),
            (9,  "👁️","समदृष्टी"),
            (10, "🌅", "बाहेरचं सुख क्षणिक"),
            (11, "⚔️", "काम-क्रोध जिंकणं"),
            (12, "🕉️","ब्रह्मनिर्वाण"),
        ]
    },
    {
        "id": 6, "number": "६", "name": "आत्मसंयमयोग",
        "concepts": [
            (1,  "🧘", "खरा योगी — कर्त्यापण सोडणारा"),
            (2,  "🪜", "साधनेचे दोन टप्पे — आरोहण आणि आरूढ"),
            (3,  "⚔️", "मन हाच शत्रू, मन हाच मित्र"),
            (4,  "🏔️","जितात्मा — स्वतःला जिंकलेल्याची शांती"),
            (5,  "📿", "ध्यानाची पद्धत — step by step"),
            (6,  "⚖️", "युक्त आहार-विहार — balanced जीवन"),
            (7,  "🕯️","दीपवत् उपमा — ध्यानाचे परम फळ"),
            (8,  "🌊", "मन भटकलं तर — अभ्यास आणि वैराग्य"),
            (9,  "🌐", "सर्वभूतस्थित — सर्वांत स्वतःला पाहणं"),
            (10, "🌱", "अर्धवट साधना — एकही प्रयत्न वाया जात नाही"),
            (11, "🕉️","योगाची परमावस्था — भक्तियोग श्रेष्ठ"),
        ]
    },
    {
        "id": 7, "number": "७", "name": "ज्ञानविज्ञानयोग",
        "concepts": [
            (1, "📚", "ज्ञान आणि विज्ञान — बोध आणि अनुभव"),
            (2, "🌍", "अपरा आणि परा प्रकृती — धाग्यात मणी"),
            (3, "🌊", "मीच सर्वांत — रस, प्रकाश, गंध, ध्वनी"),
            (4, "🌀", "माया — त्रिगुणांचा दुर्भेद्य पडदा"),
            (5, "🚫", "चार प्रकारचे अभक्त"),
            (6, "💎", "चार प्रकारचे भक्त — ज्ञानी श्रेष्ठ"),
            (7, "🌟", "देवांची पूजा — फळ क्षणिक, माझे फळ अक्षय"),
            (8, "🌫️","मला सर्व माहीत — इच्छा-द्वेष पडदा टाकतो"),
            (9, "🌌", "अव्यक्त परमात्मा — वासुदेवः सर्वम्"),
        ]
    },
    {
        "id": 11, "number": "११", "name": "विश्वरूपदर्शनयोग",
        "concepts": [
            (1, "🙏",  "अर्जुनाची विनंती — दिव्य दृष्टी द्या"),
            (2, "🌌",  "विश्वरूप प्रकट — हजार सूर्यांचे तेज"),
            (3, "😱",  "भयंकर रूप — काळापुढे कुणी थारत नाही"),
            (4, "⏳",  "\"मी काळ आहे\" — तू निमित्त मात्र हो"),
            (5, "🙇",  "अर्जुनाची स्तुती आणि क्षमायाचना"),
            (6, "🌸",  "सौम्य रूप — कठोर सत्य स्वीकारणे हीच परिपक्वता"),
            (7, "🌺",  "अनन्यभक्तीशिवाय विश्वरूप दिसत नाही"),
        ]
    },
]

SHIM_TEMPLATE = """\
<!DOCTYPE html>
<html lang="mr">
<head>
  <meta charset="UTF-8">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{base}/c/{aid}/{cid}/">
  <meta property="og:title" content="{emoji} {cname} | अध्याय {anum} · {aname}">
  <meta property="og:description" content="गीता-ज्ञानेश्वरी — आधुनिक जीवनदर्शन">
  <meta property="og:image" content="{base}/assets/og/adhyay-{aid}/concept-{cid}.jpg">
  <meta property="og:image:width" content="540">
  <meta property="og:image:height" content="960">
  <meta name="twitter:card" content="summary">
  <meta http-equiv="refresh" content="0;url={base}/adhyay.html?id={aid}&concept={cid}">
  <title>{emoji} {cname} | गीता-ज्ञानेश्वरी</title>
  <script>window.location.replace('{base}/adhyay.html?id={aid}&concept={cid}');</script>
</head>
<body>
  <a href="{base}/adhyay.html?id={aid}&concept={cid}">पुढे जा →</a>
</body>
</html>
"""

total_shims = 0
total_thumbs = 0

for adhyay in ADHYAYS:
    aid   = adhyay["id"]
    anum  = adhyay["number"]
    aname = adhyay["name"]

    # ── Thumbnails ────────────────────────────────────────────────
    og_dir  = os.path.join(PROJECT, "assets", "og", f"adhyay-{aid}")
    src_dir = os.path.join(PROJECT, "assets", f"adhyay-{aid}")
    os.makedirs(og_dir, exist_ok=True)

    for (cid, emoji, cname) in adhyay["concepts"]:
        src = os.path.join(src_dir, f"concept-{cid}.jpg")
        tmp = f"/tmp/og_{aid}_{cid}.jpg"
        dst = os.path.join(og_dir, f"concept-{cid}.jpg")

        if not os.path.exists(src):
            print(f"  ⚠️  Source missing: {src}")
            continue

        # resize to fit within 540×960, then reduce quality to ~60
        subprocess.run(["sips", "-z", "960", "540", src, "--out", tmp],
                       capture_output=True)
        subprocess.run(["sips", "-s", "formatOptions", "60", tmp, "--out", dst],
                       capture_output=True)
        kb = os.path.getsize(dst) // 1024
        print(f"  ✅ thumb  adhyay-{aid}/concept-{cid}.jpg  ({kb} KB)")
        total_thumbs += 1

    # ── Shim pages ────────────────────────────────────────────────
    for (cid, emoji, cname) in adhyay["concepts"]:
        shim_dir = os.path.join(PROJECT, "c", str(aid), str(cid))
        os.makedirs(shim_dir, exist_ok=True)
        html = SHIM_TEMPLATE.format(
            base=BASE_URL, aid=aid, cid=cid,
            anum=anum, aname=aname,
            emoji=emoji, cname=cname,
        )
        path = os.path.join(shim_dir, "index.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  ✅ shim   c/{aid}/{cid}/index.html")
        total_shims += 1

    # ── Update whatsapp-links.md ──────────────────────────────────
    md_path = os.path.join(PROJECT, f"adhyay{aid}-whatsapp-links.md")
    if os.path.exists(md_path):
        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()
        # replace adhyay.html?id=X&concept=Y → c/X/Y/
        new_content = re.sub(
            r'adhyay\.html\?id=' + str(aid) + r'&concept=(\d+)',
            lambda m: f'c/{aid}/{m.group(1)}/',
            content
        )
        if new_content != content:
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"  ✅ links  adhyay{aid}-whatsapp-links.md updated")
        else:
            print(f"  ℹ️  links  adhyay{aid}-whatsapp-links.md already up to date")

print(f"\nDone — {total_thumbs} thumbnails, {total_shims} shim pages generated.")
