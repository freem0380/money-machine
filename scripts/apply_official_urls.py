#!/usr/bin/env python3
"""全ツールのhref="#"を公式サイトURLに一括置換するスクリプト"""
import os
import re
import json

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TOOLS_DIR = os.path.join(BASE_DIR, 'output', 'tools')
CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'affiliate_links.json')

with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = json.load(f)

def get_url(key):
    return config.get(key, {}).get('url', '#')

def replace_in_file(filepath, replacements):
    """replacements: list of (old_str, new_str)"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    changed = 0
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new, 1)
            changed += 1

    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    return changed

def fix_salary_calculator():
    fp = os.path.join(TOOLS_DIR, 'salary-calculator', 'index.html')
    return replace_in_file(fp, [
        # LHH転職エージェント - 1つ目のhref="#"
        ('年収アップを目指すなら【LHH転職エージェント】</div>\n    <div class="af-text">アデコグループのハイクラス転職支援。年収・働き方・やりがいすべてにこだわる転職を無料サポート。</div>\n    <a href="#"',
         f'年収アップを目指すなら【LHH転職エージェント】</div>\n    <div class="af-text">アデコグループのハイクラス転職支援。年収・働き方・やりがいすべてにこだわる転職を無料サポート。</div>\n    <a href="{get_url("lhh_agent")}"'),
        # ピタテン - 2つ目のhref="#"
        ('未経験からでも正社員転職【ピタテン】</div>\n    <div class="af-text">面談実施で手厚いサポート。未経験でも年収UP・正社員転職の実績多数。</div>\n    <a href="#"',
         f'未経験からでも正社員転職【ピタテン】</div>\n    <div class="af-text">面談実施で手厚いサポート。未経験でも年収UP・正社員転職の実績多数。</div>\n    <a href="{get_url("pitaten")}"'),
    ])

def fix_unemployment_benefit():
    fp = os.path.join(TOOLS_DIR, 'unemployment-benefit', 'index.html')
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    # ピタテン
    content = content.replace(
        'ピタテン</span></div>\n          <p class="af-desc">',
        'ピタテン</span></div>\n          <p class="af-desc">'
    )
    # Find patterns near the text markers
    # Pattern: find href="#" near ピタテン
    content = re.sub(
        r'(転職支援サービス【ピタテン】.*?)<a href="#"',
        lambda m: m.group(1) + f'<a href="{get_url("pitaten")}"',
        content, count=1, flags=re.DOTALL
    )
    content = re.sub(
        r'(20代.*?UZUZ.*?)<a href="#"',
        lambda m: m.group(1) + f'<a href="{get_url("uzuz")}"',
        content, count=1, flags=re.DOTALL
    )
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(content)
    return 2

def fix_insurance_calculator():
    fp = os.path.join(TOOLS_DIR, 'insurance-calculator', 'index.html')
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    content = re.sub(
        r'(マネードクター.*?)<a href="#"',
        lambda m: m.group(1) + f'<a href="{get_url("money_doctor")}"',
        content, count=1, flags=re.DOTALL
    )
    content = re.sub(
        r'(保険見直しラボ.*?)<a href="#"',
        lambda m: m.group(1) + f'<a href="{get_url("hoken_minaoshi_lab")}"',
        content, count=1, flags=re.DOTALL
    )
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(content)
    return 2

def fix_investment_return():
    fp = os.path.join(TOOLS_DIR, 'investment-return', 'index.html')
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    content = re.sub(
        r'(SBI証券.*?)<a href="#"',
        lambda m: m.group(1) + f'<a href="{get_url("sbi_securities")}"',
        content, count=1, flags=re.DOTALL
    )
    content = re.sub(
        r'(マネードクター.*?)<a href="#"',
        lambda m: m.group(1) + f'<a href="{get_url("money_doctor")}"',
        content, count=1, flags=re.DOTALL
    )
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(content)
    return 2

def fix_loan_calculator():
    fp = os.path.join(TOOLS_DIR, 'loan-calculator', 'index.html')
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    content = re.sub(
        r'(モゲチェック.*?)<a href="#"',
        lambda m: m.group(1) + f'<a href="{get_url("mogecheck")}"',
        content, count=1, flags=re.DOTALL
    )
    content = re.sub(
        r'(保険スクエア.*?)<a href="#"',
        lambda m: m.group(1) + f'<a href="{get_url("hoken_square_bang")}"',
        content, count=1, flags=re.DOTALL
    )
    # Also handle case where href is in the same tag as text
    content = content.replace(
        'モゲチェック】</a>', f'モゲチェック】</a>'
    )
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(content)
    return 2

def fix_dividend_yield():
    fp = os.path.join(TOOLS_DIR, 'dividend-yield', 'index.html')
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    content = re.sub(
        r'(高配当株投資.*?SBI証券.*?)<a href="#"',
        lambda m: m.group(1) + f'<a href="{get_url("sbi_securities")}"',
        content, count=1, flags=re.DOTALL
    )
    content = re.sub(
        r'(配当投資.*?マネードクター.*?)<a href="#"',
        lambda m: m.group(1) + f'<a href="{get_url("money_doctor")}"',
        content, count=1, flags=re.DOTALL
    )
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(content)
    return 2

def fix_pension_calculator():
    fp = os.path.join(TOOLS_DIR, 'pension-calculator', 'index.html')
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    content = re.sub(
        r'(老後の資金計画.*?マネードクター.*?)<a href="#"',
        lambda m: m.group(1) + f'<a href="{get_url("money_doctor")}"',
        content, count=1, flags=re.DOTALL
    )
    content = re.sub(
        r'(iDeCo.*?SBI証券.*?)<a href="#"',
        lambda m: m.group(1) + f'<a href="{get_url("sbi_securities")}"',
        content, count=1, flags=re.DOTALL
    )
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(content)
    return 2

def fix_nisa_simulator():
    fp = os.path.join(TOOLS_DIR, 'nisa-simulator', 'index.html')
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    content = re.sub(
        r'(SBI証券.*?)<a href="#"',
        lambda m: m.group(1) + f'<a href="{get_url("sbi_securities")}"',
        content, count=1, flags=re.DOTALL
    )
    content = re.sub(
        r'(WealthNavi.*?)<a href="#"',
        lambda m: m.group(1) + f'<a href="{get_url("wealthnavi")}"',
        content, count=1, flags=re.DOTALL
    )
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(content)
    return 2

def fix_retirement_calculator():
    fp = os.path.join(TOOLS_DIR, 'retirement-calculator', 'index.html')
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    content = re.sub(
        r'(マネードクター.*?)<a href="#">',
        lambda m: m.group(1) + f'<a href="{get_url("money_doctor")}">',
        content, count=1, flags=re.DOTALL
    )
    content = re.sub(
        r'(SBI証券.*?)<a href="#">',
        lambda m: m.group(1) + f'<a href="{get_url("sbi_securities")}">',
        content, count=1, flags=re.DOTALL
    )
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(content)
    return 2

def fix_retirement_fund():
    fp = os.path.join(TOOLS_DIR, 'retirement-fund', 'index.html')
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    content = re.sub(
        r'(老後の資産運用.*?マネードクター.*?)<a href="#"',
        lambda m: m.group(1) + f'<a href="{get_url("money_doctor")}"',
        content, count=1, flags=re.DOTALL
    )
    content = re.sub(
        r'(新NISA.*?SBI証券.*?)<a href="#"',
        lambda m: m.group(1) + f'<a href="{get_url("sbi_securities")}"',
        content, count=1, flags=re.DOTALL
    )
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(content)
    return 2

def fix_tax_calculator():
    fp = os.path.join(TOOLS_DIR, 'tax-calculator', 'index.html')
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    content = re.sub(
        r'(マネーフォワード.*?)<a href="#"',
        lambda m: m.group(1) + f'<a href="{get_url("money_forward")}"',
        content, count=1, flags=re.DOTALL
    )
    content = re.sub(
        r'(税理士ドットコム.*?)<a href="#"',
        lambda m: m.group(1) + f'<a href="{get_url("zeirishi_dot_com")}"',
        content, count=1, flags=re.DOTALL
    )
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(content)
    return 2

def fix_real_estate_yield():
    fp = os.path.join(TOOLS_DIR, 'real-estate-yield', 'index.html')
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    content = re.sub(
        r'(RENOSY.*?)<a href="#">',
        lambda m: m.group(1) + f'<a href="{get_url("renosy")}">',
        content, count=1, flags=re.DOTALL
    )
    content = re.sub(
        r'(マネードクター.*?)<a href="#">',
        lambda m: m.group(1) + f'<a href="{get_url("money_doctor")}">',
        content, count=1, flags=re.DOTALL
    )
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(content)
    return 2

def fix_sim_comparison():
    """SIM比較ツール: JavaScriptテンプレート内のリンクをプロバイダー別に動的化"""
    fp = os.path.join(TOOLS_DIR, 'sim-comparison', 'index.html')
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()

    # プロバイダー→URL のマッピングを構築
    sim_map = {
        'povo': get_url('sim_povo'),
        'LINEMO': get_url('sim_linemo'),
        'IIJmio': get_url('sim_iijmio'),
        '楽天モバイル': get_url('sim_rakuten'),
        'mineo': get_url('sim_mineo'),
        'ahamo': get_url('sim_ahamo'),
        'UQモバイル': get_url('sim_uqmobile'),
        'ワイモバイル': get_url('sim_ymobile'),
        'NUROモバイル': get_url('sim_nuro_mobile'),
        'BIGLOBEモバイル': get_url('sim_biglobe'),
        'J:COMモバイル': get_url('sim_jcom'),
        'LIBMO': get_url('sim_libmo'),
        '日本通信SIM': config.get('sim_nihon_tsushin', {}).get('url', '#'),
    }
    default_url = get_url('sim_default')

    js_map = json.dumps(sim_map, ensure_ascii=False)

    # allPlansの直後にURLマッピングを挿入
    content = content.replace(
        'let currentSort="price";',
        f'const affiliateUrls={js_map};\nconst defaultSimUrl="{default_url}";\nlet currentSort="price";'
    )

    # href="#" を動的URLに変更
    content = content.replace(
        '<a href="#" class="btn-official">公式サイト</a>',
        '<a href="${affiliateUrls[p.provider]||defaultSimUrl}" class="btn-official" target="_blank" rel="nofollow noopener">公式サイト</a>'
    )

    with open(fp, 'w', encoding='utf-8') as f:
        f.write(content)
    return 1


def main():
    total = 0
    fixes = [
        ('salary-calculator', fix_salary_calculator),
        ('unemployment-benefit', fix_unemployment_benefit),
        ('insurance-calculator', fix_insurance_calculator),
        ('investment-return', fix_investment_return),
        ('loan-calculator', fix_loan_calculator),
        ('dividend-yield', fix_dividend_yield),
        ('pension-calculator', fix_pension_calculator),
        ('nisa-simulator', fix_nisa_simulator),
        ('retirement-calculator', fix_retirement_calculator),
        ('retirement-fund', fix_retirement_fund),
        ('tax-calculator', fix_tax_calculator),
        ('real-estate-yield', fix_real_estate_yield),
        ('sim-comparison', fix_sim_comparison),
    ]

    for name, func in fixes:
        try:
            n = func()
            print(f"  OK: {name} ({n} links)")
            total += n
        except Exception as e:
            print(f"  ERROR: {name} - {e}")

    print(f"\nTotal: {total} links updated across {len(fixes)} tools")


if __name__ == '__main__':
    print("=== Applying Official URLs to All Tools ===\n")
    main()
    print("\n=== Done ===")
