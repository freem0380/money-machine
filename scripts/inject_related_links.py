#!/usr/bin/env python3
"""全ツールに「関連ツール」セクションを一括注入"""
import os, re

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'output', 'tools'))
SITE = 'https://ai-money-lab.github.io/benri-tools'

TOOLS = {
    'salary-calculator': '年収手取り計算機',
    'tax-calculator': '副業税金シミュレーター',
    'tax-return-checker': '確定申告要否チェッカー',
    'furusato-tax': 'ふるさと納税上限額計算機',
    'loan-calculator': '住宅ローン計算機',
    'investment-return': '投資リターン計算機',
    'nisa-simulator': '積立NISAシミュレーター',
    'compound-interest': '複利計算シミュレーター',
    'dividend-yield': '配当金利回り計算機',
    'insurance-calculator': '生命保険必要額シミュレーター',
    'pension-calculator': '年金受給額シミュレーター',
    'retirement-fund': '老後資金シミュレーター',
    'retirement-calculator': '退職金計算シミュレーター',
    'unemployment-benefit': '失業保険計算機',
    'rent-vs-buy': '持ち家vs賃貸比較',
    'real-estate-yield': '不動産投資利回り計算機',
    'sim-comparison': '格安SIM比較表',
}

RELATED = {
    'salary-calculator': ['tax-calculator', 'tax-return-checker', 'pension-calculator', 'unemployment-benefit'],
    'tax-calculator': ['tax-return-checker', 'salary-calculator', 'furusato-tax', 'nisa-simulator'],
    'tax-return-checker': ['tax-calculator', 'furusato-tax', 'salary-calculator', 'nisa-simulator'],
    'furusato-tax': ['tax-calculator', 'tax-return-checker', 'salary-calculator', 'nisa-simulator'],
    'loan-calculator': ['rent-vs-buy', 'real-estate-yield', 'insurance-calculator', 'salary-calculator'],
    'investment-return': ['compound-interest', 'nisa-simulator', 'dividend-yield', 'retirement-fund'],
    'nisa-simulator': ['investment-return', 'compound-interest', 'dividend-yield', 'tax-calculator'],
    'compound-interest': ['investment-return', 'nisa-simulator', 'dividend-yield', 'retirement-fund'],
    'dividend-yield': ['investment-return', 'nisa-simulator', 'compound-interest', 'retirement-fund'],
    'insurance-calculator': ['pension-calculator', 'retirement-fund', 'salary-calculator', 'loan-calculator'],
    'pension-calculator': ['retirement-fund', 'retirement-calculator', 'salary-calculator', 'insurance-calculator'],
    'retirement-fund': ['pension-calculator', 'retirement-calculator', 'compound-interest', 'nisa-simulator'],
    'retirement-calculator': ['pension-calculator', 'retirement-fund', 'salary-calculator', 'tax-calculator'],
    'unemployment-benefit': ['salary-calculator', 'tax-calculator', 'pension-calculator', 'insurance-calculator'],
    'rent-vs-buy': ['loan-calculator', 'real-estate-yield', 'insurance-calculator', 'salary-calculator'],
    'real-estate-yield': ['rent-vs-buy', 'loan-calculator', 'investment-return', 'compound-interest'],
    'sim-comparison': ['salary-calculator', 'furusato-tax', 'tax-calculator', 'insurance-calculator'],
}

STYLE = '''<style>.related-tools{background:#f8f9fa;border-radius:12px;padding:20px;margin:20px 0}.related-tools h3{font-size:1rem;color:#1a2744;margin-bottom:12px;padding-bottom:8px;border-bottom:2px solid #667eea}.related-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:8px}.related-link{display:block;padding:10px 14px;background:#fff;border-radius:8px;text-decoration:none;color:#333;font-size:.9rem;font-weight:500;box-shadow:0 1px 3px rgba(0,0,0,.08);transition:transform .15s,box-shadow .15s}.related-link:hover{transform:translateY(-1px);box-shadow:0 3px 8px rgba(102,126,234,.2);color:#667eea}</style>'''

def build_section(slug):
    links = RELATED.get(slug, [])
    if not links:
        return ''
    items = ''
    for s in links:
        name = TOOLS.get(s, s)
        items += f'    <a href="{SITE}/{s}/" class="related-link">{name}</a>\n'
    return f'''
  <div class="related-tools">
    <h3>関連ツール</h3>
    <div class="related-grid">
{items}    </div>
  </div>'''

def inject(slug):
    path = os.path.join(BASE, slug, 'index.html')
    if not os.path.isfile(path):
        print(f'  SKIP: {slug} (not found)')
        return False
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    if 'related-tools' in html:
        print(f'  SKIP: {slug} (already has related-tools)')
        return False

    section = build_section(slug)
    if not section:
        print(f'  SKIP: {slug} (no related links defined)')
        return False

    # Insert style before </head>
    html = html.replace('</head>', STYLE + '\n</head>', 1)

    # Insert section before </div> that precedes <script> or before <footer
    # Strategy: insert before the last </div> before <script>
    # Find the footer or note/disclaimer near the end
    patterns = [
        (r'(<p class="note">)', r'{}\1'),
        (r'(<footer)', r'{}\1'),
        (r'(<!-- Disclaimer -->)', r'{}\1'),
        (r'(<div class="disclaimer")', r'{}\1'),
    ]
    inserted = False
    for pat, repl in patterns:
        m = re.search(pat, html)
        if m:
            pos = m.start()
            html = html[:pos] + section + '\n\n  ' + html[pos:]
            inserted = True
            break

    if not inserted:
        # Fallback: insert before </div>\n\n<script>
        html = re.sub(r'(</div>\s*\n\s*<script>)', section + r'\n\1', html, count=1)
        inserted = True

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'  OK: {slug}')
    return True

count = 0
for slug in TOOLS:
    if inject(slug):
        count += 1
print(f'\nDone: {count} tools updated')
