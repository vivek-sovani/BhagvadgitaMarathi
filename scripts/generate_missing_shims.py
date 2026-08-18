#!/usr/bin/env python3
"""
Generate missing /c/{adhyayId}/{conceptId}/index.html shim pages.

Shim pages provide OG meta tags for WhatsApp/Telegram preview cards
and immediately redirect to adhyay.html?id=X&concept=Y.

Run from the project root:
    python3 scripts/generate_missing_shims.py
"""

import os

BASE_URL = "https://vivek-sovani.github.io/BhagvadgitaMarathi"
FALLBACK_IMAGE = f"{BASE_URL}/assets/home-banner-landscape.jpg"
FALLBACK_IMAGE_W = 1200
FALLBACK_IMAGE_H = 630

# Adhyays that already have /c/ shim pages — skip these
EXISTING_ADHYAYS = {1, 2, 3, 4, 5, 6, 7, 8, 11}

# Full concept data from js/data.js
ADHYAYS = [
    {
        "id": 9, "number": "९", "name": "राजविद्याराजगुह्ययोग",
        "concepts": [
            {"id": 1, "emoji": "👑", "name": "राजविद्या-राजगुह्य — सर्वोच्च ज्ञान"},
            {"id": 2, "emoji": "🌌", "name": "मी सर्वात व्यापलेलो — उदासीन ईश्वर"},
            {"id": 3, "emoji": "👁️", "name": "मूढ आणि महात्मे — दोन दृष्टी"},
            {"id": 4, "emoji": "🌍", "name": "मी यज्ञ, पिता, माता, सुहृद"},
            {"id": 5, "emoji": "⚡", "name": "त्रैविद्य — स्वर्ग — परत — आणि योगक्षेम"},
            {"id": 6, "emoji": "🌿", "name": "पत्र-पुष्प-फल-जल — सर्व अर्पण"},
            {"id": 7, "emoji": "❤️", "name": "समभाव — न मे भक्तः प्रणश्यति"},
        ]
    },
    {
        "id": 10, "number": "१०", "name": "विभूतियोग",
        "concepts": [
            {"id": 1, "emoji": "🌟", "name": "माझा उद्गम कुणालाही माहीत नाही — जो जाणतो तो मुक्त"},
            {"id": 2, "emoji": "🧠", "name": "माझ्यापासून निघणारे भाव — बुद्धी, ज्ञान, क्षमा, सत्य..."},
            {"id": 3, "emoji": "💡", "name": "विभूती-योग जाणणारा — मी त्याला बुद्धियोग देतो"},
            {"id": 4, "emoji": "♾️", "name": "विभूती अनंत — मी सर्वांच्या हृदयात आत्मा"},
            {"id": 5, "emoji": "✨", "name": "विभूती यादी — प्रत्येक श्रेष्ठात माझा अंश"},
            {"id": 6, "emoji": "🔥", "name": "जे विभूतिमत् — माझ्या तेजाचा अंश"},
            {"id": 7, "emoji": "🌈", "name": "एकांशेन स्थितो जगत् — अध्यायाचे परम सत्य"},
        ]
    },
    {
        "id": 12, "number": "१२", "name": "भक्तियोग",
        "concepts": [
            {"id": 1,  "emoji": "❓", "name": "अर्जुनाचा प्रश्न — सगुण की निर्गुण?"},
            {"id": 2,  "emoji": "🙏", "name": "सगुण भक्तीची श्रेष्ठता — मन माझ्यात स्थापन कर"},
            {"id": 3,  "emoji": "🧘", "name": "निर्गुण उपासना — कठीण पण शक्य"},
            {"id": 4,  "emoji": "🪜", "name": "भक्तीचे चार टप्पे — अभ्यासापासून ज्ञानापर्यंत"},
            {"id": 5,  "emoji": "☮️", "name": "कर्मसंन्यास — कृष्णावर सर्व अर्पण"},
            {"id": 6,  "emoji": "💎", "name": "प्रिय भक्त — भाग १ : द्वेष नाही, मैत्री सर्वांशी"},
            {"id": 7,  "emoji": "🌊", "name": "प्रिय भक्त — भाग २ : संतोष, स्थिरमती, समर्पण"},
            {"id": 8,  "emoji": "🌿", "name": "प्रिय भक्त — भाग ३ : शत्रू-मित्र समान, मान-अपमान समान"},
            {"id": 9,  "emoji": "🔥", "name": "प्रिय भक्त — भाग ४ : श्रद्धा, भक्ती, धर्मनिष्ठा"},
            {"id": 10, "emoji": "🌅", "name": "परम प्रिय भक्त — अमृत तुल्य जो"},
            {"id": 11, "emoji": "🕉️", "name": "अध्याय १२ — सार व समारोप"},
        ]
    },
    {
        "id": 13, "number": "१३", "name": "क्षेत्रक्षेत्रज्ञविभागयोग",
        "concepts": [
            {"id": 1, "emoji": "🏡", "name": "क्षेत्र आणि क्षेत्रज्ञ — शरीर आणि आत्मा"},
            {"id": 2, "emoji": "🌿", "name": "क्षेत्राचे स्वरूप — पंचमहाभूतांपासून मनापर्यंत"},
            {"id": 3, "emoji": "💎", "name": "ज्ञानाची २० लक्षणे — अमानित्व ते तत्त्वज्ञान"},
            {"id": 4, "emoji": "♾️", "name": "ज्ञेय — परमात्मा कसा आहे?"},
            {"id": 5, "emoji": "⚖️", "name": "प्रकृती आणि पुरुष — सृष्टीचे दोन स्तंभ"},
            {"id": 6, "emoji": "🪷", "name": "पुरुष — भोक्ता, साक्षी, अनुमंता"},
            {"id": 7, "emoji": "🛤️", "name": "मुक्तीचे चार मार्ग — ध्यान, ज्ञान, कर्म, श्रद्धा"},
            {"id": 8, "emoji": "👁️", "name": "सर्व भूतांत ईश्वर — समदृष्टी आणि परम पद"},
            {"id": 9, "emoji": "🌅", "name": "प्रकृतीने केले, पुरुष साक्षी — सार व समारोप"},
        ]
    },
    {
        "id": 14, "number": "१४", "name": "गुणत्रयविभागयोग",
        "concepts": [
            {"id": 1, "emoji": "🌱", "name": "त्रिगुणांचा जन्म — सत्त्व, रज, तम"},
            {"id": 2, "emoji": "☀️", "name": "सत्त्वगुण — प्रकाश, ज्ञान, सुख"},
            {"id": 3, "emoji": "🔥", "name": "रजोगुण — इच्छा, कर्म, तृष्णा"},
            {"id": 4, "emoji": "🌑", "name": "तमोगुण — अज्ञान, आळस, प्रमाद"},
            {"id": 5, "emoji": "⚡", "name": "तीन गुणांचा संघर्ष — कोण जिंकतो?"},
            {"id": 6, "emoji": "🪷", "name": "गुणांतीत कोण? — स्थितप्रज्ञाचा भाऊ"},
            {"id": 7, "emoji": "🛤️", "name": "गुणांतीत होण्याचा मार्ग — भक्तीने"},
            {"id": 8, "emoji": "🌅", "name": "अध्याय १४ — सार व समारोप"},
        ]
    },
    {
        "id": 15, "number": "१५", "name": "पुरुषोत्तमयोग",
        "concepts": [
            {"id": 1, "emoji": "🌳", "name": "अश्वत्थ वृक्ष — संसाराचे उलटे झाड"},
            {"id": 2, "emoji": "🪓", "name": "असंग शस्त्र — झाड तोडण्याचा उपाय"},
            {"id": 3, "emoji": "✨", "name": "जीव — परमाचा अंश, गुणांत अडकलेला"},
            {"id": 4, "emoji": "☀️", "name": "परमात्म्याचा प्रकाश — सूर्य-चंद्र-अग्नीपलीकडे"},
            {"id": 5, "emoji": "🌱", "name": "क्षर, अक्षर आणि पुरुषोत्तम — तीन तत्त्वे"},
            {"id": 6, "emoji": "👑", "name": "पुरुषोत्तम — उत्तम पुरुष कोण?"},
            {"id": 7, "emoji": "🌅", "name": "अध्याय १५ — सार व समारोप"},
        ]
    },
    {
        "id": 16, "number": "१६", "name": "दैवासुरसम्पद्विभागयोग",
        "concepts": [
            {"id": 1, "emoji": "✨", "name": "दैवीसंपद — दिव्य स्वभावाची २६ लक्षणे"},
            {"id": 2, "emoji": "🌑", "name": "आसुरीसंपद — आसुरी स्वभावाची लक्षणे"},
            {"id": 3, "emoji": "🔥", "name": "आसुरी माणूस — काम, क्रोध, लोभाचा दास"},
            {"id": 4, "emoji": "⚡", "name": "तीन नरकद्वारे — काम, क्रोध, लोभ"},
            {"id": 5, "emoji": "📜", "name": "शास्त्रप्रमाण — विवेकाचा आधार"},
            {"id": 6, "emoji": "🌱", "name": "दैवी स्वभाव वाढवणे — साधनेचा मार्ग"},
            {"id": 7, "emoji": "🌅", "name": "अध्याय १६ — सार व समारोप"},
        ]
    },
    {
        "id": 17, "number": "१७", "name": "श्रद्धात्रयविभागयोग",
        "concepts": [
            {"id": 1, "emoji": "🙏", "name": "तीन प्रकारची श्रद्धा — सात्त्विक, राजसिक, तामसिक"},
            {"id": 2, "emoji": "🍽️", "name": "तीन प्रकारचे आहार — सात्त्विक, राजसिक, तामसिक"},
            {"id": 3, "emoji": "🔥", "name": "तीन प्रकारचे यज्ञ"},
            {"id": 4, "emoji": "🌿", "name": "तीन प्रकारचे तप — शरीर, वाणी, मन"},
            {"id": 5, "emoji": "🎁", "name": "तीन प्रकारचे दान"},
            {"id": 6, "emoji": "🕉️", "name": "ॐ तत् सत् — तीन शब्दांत ब्रह्म"},
            {"id": 7, "emoji": "🌅", "name": "अध्याय १७ — सार व समारोप"},
        ]
    },
    {
        "id": 18, "number": "१८", "name": "मोक्षसंन्यासयोग",
        "concepts": [
            {"id": 1,  "emoji": "🌿", "name": "संन्यास आणि त्याग — नित्यसंन्यासी कोण?"},
            {"id": 2,  "emoji": "⚖️", "name": "त्याग तीन प्रकारचा — सात्त्विक, राजसिक, तामसिक"},
            {"id": 3,  "emoji": "🧠", "name": "ज्ञान, कर्म, कर्ता — तीन प्रकार"},
            {"id": 4,  "emoji": "🎯", "name": "धृती, बुद्धी, सुख — तीन प्रकार"},
            {"id": 5,  "emoji": "🌱", "name": "वर्णधर्म — स्वधर्म हेच श्रेष्ठ कर्म"},
            {"id": 6,  "emoji": "💫", "name": "ब्रह्मभाव — कर्मसंन्यासाचे परम फळ"},
            {"id": 7,  "emoji": "🙏", "name": "भक्तीचे परम रहस्य — सर्वधर्मान्परित्यज्य"},
            {"id": 8,  "emoji": "❤️", "name": "कृष्णाचे शेवटचे वचन — मन्मना भव"},
            {"id": 9,  "emoji": "📜", "name": "गीता श्रवण आणि पठणाचे फळ"},
            {"id": 10, "emoji": "🌅", "name": "अध्याय १८ — सार व महासमारोप"},
        ]
    },
]

SHIM_TEMPLATE = """\
<!DOCTYPE html>
<html lang="mr">
<head>
  <meta charset="UTF-8">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{og_url}">
  <meta property="og:title" content="{og_title}">
  <meta property="og:description" content="गीता-ज्ञानेश्वरी — आधुनिक जीवनदर्शन">
  <meta property="og:image" content="{og_image}">
  <meta property="og:image:width" content="{og_image_w}">
  <meta property="og:image:height" content="{og_image_h}">
  <meta name="twitter:card" content="{twitter_card}">
  <meta http-equiv="refresh" content="0;url={redirect_url}">
  <title>{page_title} | गीता-ज्ञानेश्वरी</title>
  <script>window.location.replace('{redirect_url}');</script>
</head>
<body>
  <a href="{redirect_url}">पुढे जा →</a>
</body>
</html>
"""


def get_og_image(adhyay_id, concept_id):
    """
    Return (relative_og_path, width, height) for a concept's OG share image,
    generating a resized copy under assets/og/ if one doesn't exist yet.

    The raw assets/adhyay-N/concept-M.jpg infographics are 500-1000KB —
    WhatsApp's preview fetcher silently fails (or takes a very long time) on
    images that large, showing no preview image at all. Every other adhyay's
    shim uses a much smaller (~150-250KB) resized copy in assets/og/ instead,
    so concept images must always go through this same resize step, never
    point at the raw infographic directly.
    """
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_path = os.path.join(root, "assets", f"adhyay-{adhyay_id}", f"concept-{concept_id}.jpg")
    og_rel   = f"assets/og/adhyay-{adhyay_id}/concept-{concept_id}.jpg"
    og_path  = os.path.join(root, og_rel)

    if not os.path.isfile(raw_path):
        return None

    if not os.path.isfile(og_path):
        from PIL import Image
        os.makedirs(os.path.dirname(og_path), exist_ok=True)
        with Image.open(raw_path) as im:
            w, h = im.size
            target_w = 540
            target_h = round(h * target_w / w)
            im.convert("RGB").resize((target_w, target_h), Image.LANCZOS).save(
                og_path, "JPEG", quality=85
            )

    from PIL import Image
    with Image.open(og_path) as im:
        w, h = im.size
    return og_rel, w, h


def generate_shims():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    created = 0
    skipped = 0

    for adhyay in ADHYAYS:
        aid = adhyay["id"]
        if aid in EXISTING_ADHYAYS:
            skipped += 1
            continue

        for concept in adhyay["concepts"]:
            cid = concept["id"]
            out_dir = os.path.join(project_root, "c", str(aid), str(cid))
            out_file = os.path.join(out_dir, "index.html")

            og_asset = get_og_image(aid, cid)

            # Skip if already exists and already points at the resized OG
            # image (or no real image exists yet). Regenerate if a shim was
            # created before its concept image was uploaded (stuck on the
            # fallback banner) or before this script resized images under
            # assets/og/ (stuck pointing at the raw, oversized infographic)
            # — otherwise either bug persists forever, since this check only
            # ever ran once at first-generation time.
            if os.path.isfile(out_file):
                if og_asset is None:
                    skipped += 1
                    continue
                with open(out_file, encoding="utf-8") as f:
                    existing = f.read()
                og_rel_url = f"{BASE_URL}/{og_asset[0]}"
                if FALLBACK_IMAGE not in existing and og_rel_url in existing:
                    skipped += 1
                    continue

            os.makedirs(out_dir, exist_ok=True)

            redirect_url = f"{BASE_URL}/adhyay.html?id={aid}&concept={cid}"
            og_url       = f"{BASE_URL}/c/{aid}/{cid}/"
            og_title     = f"{concept['emoji']} {concept['name']} | अध्याय {adhyay['number']} · {adhyay['name']}"
            page_title   = f"{concept['emoji']} {concept['name']}"

            # Use the resized OG copy if a real concept image is available
            # (generating it on the fly if needed), else fallback banner
            if og_asset:
                rel_path, w, h = og_asset
                og_image   = f"{BASE_URL}/{rel_path}"
                og_image_w = str(w)
                og_image_h = str(h)
                twitter_card = "summary"
            else:
                og_image   = FALLBACK_IMAGE
                og_image_w = str(FALLBACK_IMAGE_W)
                og_image_h = str(FALLBACK_IMAGE_H)
                twitter_card = "summary_large_image"

            html = SHIM_TEMPLATE.format(
                og_url=og_url,
                og_title=og_title,
                og_image=og_image,
                og_image_w=og_image_w,
                og_image_h=og_image_h,
                twitter_card=twitter_card,
                redirect_url=redirect_url,
                page_title=page_title,
            )

            with open(out_file, "w", encoding="utf-8") as f:
                f.write(html)

            print(f"  Created: c/{aid}/{cid}/index.html")
            created += 1

    print(f"\nDone — {created} shim pages created, {skipped} skipped.")


if __name__ == "__main__":
    generate_shims()
