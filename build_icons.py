# ============================================================
# build_icons.py — ساخت icons.svg از فایل‌های SVG
# ============================================================

import os
import re

ICONS_DIR = os.path.join('static', 'icons')
OUTPUT_FILE = os.path.join('static', 'icons', 'icons.svg')

# ===== نقشه: اسم ساده → اسم فایل =====
ICONS_MAP = {
    'brain':          'brain.svg',
    'chart':          'chart-column-big.svg',
    'wind':           'wind.svg',
    'flower':         'flower-2.svg',
    'notebook':       'notebook-pen.svg',
    'message':        'message-circle.svg',
    'clipboard':      'clipboard-list.svg',
    'scroll':         'scroll.svg',
    'user':           'user.svg',
    'home':           'house.svg',
    'trending':       'trending-up.svg',
    'lock':           'lock.svg',
    'log-out':        'log-out.svg',
    'moon':           'moon.svg',
    'sun':            'sun.svg',
    'alert':          'triangle-alert.svg',
    'life-buoy':      'life-buoy.svg',
    'phone':          'phone.svg',
}


def extract_svg_content(svg_text):
    """استخراج محتوای داخل <svg>...</svg>"""
    match = re.search(r'<svg[^>]*>(.*)</svg>', svg_text, re.DOTALL)
    if not match:
        return None
    return match.group(1).strip()


def main():
    print("🔄 در حال ساخت icons.svg ...\n")

    symbols = []
    missing = []

    for name, filename in ICONS_MAP.items():
        file_path = os.path.join(ICONS_DIR, filename)

        if not os.path.exists(file_path):
            print(f"⚠️ پیدا نشد: {filename}")
            missing.append(name)
            continue

        with open(file_path, 'r', encoding='utf-8') as f:
            svg_text = f.read()

        content = extract_svg_content(svg_text)

        if not content:
            print(f"⚠️ محتوا خالی: {filename}")
            continue

        symbol = f'''  <symbol id="icon-{name}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    {content}
  </symbol>'''

        symbols.append(symbol)
        print(f"✅ {name}  ←  {filename}")

    # ساخت فایل نهایی
    sprite = f'''<!-- ============================================================
     همراه آرامش — Icon Sprite
     ============================================================
     خودکار ساخته شده توسط build_icons.py

     استفاده:
       <svg class="icon"><use href="/static/icons/icons.svg#icon-brain"/></svg>
     ============================================================ -->

<svg xmlns="http://www.w3.org/2000/svg" style="display: none;">
{chr(10).join(symbols)}
</svg>
'''

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(sprite)

    print(f"\n✅ icons.svg ساخته شد!")
    print(f"📍 مسیر: {OUTPUT_FILE}")
    print(f"📊 تعداد آیکون: {len(symbols)} از {len(ICONS_MAP)}")

    if missing:
        print(f"\n⚠️ آیکون‌های گم‌شده: {', '.join(missing)}")


if __name__ == '__main__':
    main()