#!/usr/bin/env python3
"""アフィリエイトリンク一括注入スクリプト

config/affiliate_links.json のURLを読み取り、
全ツールの href="#" プレースホルダーを実際のアフィリエイトURLに置換する。

使い方:
  1. config/affiliate_links.json の各 "url" フィールドにASPから取得したURLを貼付
  2. python scripts/inject_affiliate_links.py を実行
  3. python scripts/inject_affiliate_links.py --dry-run で変更内容のプレビュー
"""
import json
import os
import re
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'affiliate_links.json')
TOOLS_DIR = os.path.join(BASE_DIR, 'output', 'tools')

# ツール別のリンク定義: (ファイル, 検索パターン, configキー)
# 検索パターンは href="#" の直前のテキスト or クラス名で特定
TOOL_LINK_MAP = {
    'salary-calculator': [
        {'match': 'LHH転職エージェント', 'key': 'lhh_agent'},
        {'match': 'FREENANCE', 'key': 'freenance'},
    ],
    'unemployment-benefit': [
        {'match': 'ピタテン', 'key': 'pitaten'},
        {'match': 'UZUZ', 'key': 'uzuz'},
    ],
    'insurance-calculator': [
        {'match': 'マネードクター', 'key': 'money_doctor'},
        {'match': '保険見直しラボ', 'key': 'hoken_minaoshi_lab'},
    ],
    'investment-return': [
        {'match': 'SBI証券', 'key': 'sbi_securities'},
        {'match': 'DMM FX', 'key': 'dmm_fx'},
    ],
    'loan-calculator': [
        {'match': 'モゲチェック', 'key': 'mogecheck'},
        {'match': 'ファミリー工房', 'key': 'family_koubou'},
    ],
    'dividend-yield': [
        {'match': 'SBI証券', 'key': 'sbi_securities'},
        {'match': 'DMM FX', 'key': 'dmm_fx'},
    ],
    'pension-calculator': [
        {'match': 'マネードクター', 'key': 'money_doctor'},
        {'match': 'SBI証券', 'key': 'sbi_securities'},
    ],
    'nisa-simulator': [
        {'match': 'SBI証券', 'key': 'sbi_securities'},
        {'match': 'DMM FX', 'key': 'dmm_fx'},
    ],
    'compound-interest': [
        {'match': 'SBI証券', 'key': 'sbi_securities'},
        {'match': 'DMM FX', 'key': 'dmm_fx'},
    ],
    'retirement-calculator': [
        {'match': 'マネードクター', 'key': 'money_doctor'},
        {'match': 'SBI証券', 'key': 'sbi_securities'},
    ],
    'retirement-fund': [
        {'match': 'マネードクター', 'key': 'money_doctor'},
        {'match': 'SBI証券', 'key': 'sbi_securities'},
    ],
    'tax-calculator': [
        {'match': 'マネーフォワード', 'key': 'money_forward'},
        {'match': 'FREENANCE', 'key': 'freenance'},
    ],
    'real-estate-yield': [
        {'match': 'リショップナビ', 'key': 'reshop_navi'},
        {'match': 'ハピすむ', 'key': 'hapisumu'},
    ],
    'rent-vs-buy': [
        {'match': 'モゲチェック', 'key': 'mogecheck'},
        {'match': 'ファミリー工房', 'key': 'family_koubou'},
    ],
}

# SIM比較のプロバイダー→configキーのマッピング
SIM_PROVIDER_MAP = {
    'povo': 'sim_povo',
    'LINEMO': 'sim_linemo',
    'IIJmio': 'sim_iijmio',
    '楽天モバイル': 'sim_rakuten',
    'mineo': 'sim_mineo',
    'ahamo': 'sim_ahamo',
    'UQモバイル': 'sim_uqmobile',
    'ワイモバイル': 'sim_ymobile',
    'NUROモバイル': 'sim_nuro_mobile',
    'BIGLOBEモバイル': 'sim_biglobe',
    'J:COMモバイル': 'sim_jcom',
    'LIBMO': 'sim_libmo',
    '日本通信SIM': 'sim_default',
}


def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def inject_tool_links(config, dry_run=False):
    """通常ツール（sim-comparison以外）のリンク置換"""
    changes = 0
    for slug, links in TOOL_LINK_MAP.items():
        filepath = os.path.join(TOOLS_DIR, slug, 'index.html')
        if not os.path.isfile(filepath):
            print(f"  SKIP: {slug} (file not found)")
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original = content
        for link_def in links:
            key = link_def['key']
            match_text = link_def['match']
            url = config.get(key, {}).get('url', '')

            if not url:
                print(f"  SKIP: {slug} [{match_text}] - URL not set in config ({key})")
                continue

            # href="#" の直前100文字以内にmatch_textがあるパターンを探す
            # 方法: match_textを含むブロック内の href="#" を置換
            pattern = re.compile(
                r'((?:(?!<a\b).){0,500}' + re.escape(match_text) + r'(?:(?!</a>).){0,500})href="#"',
                re.DOTALL
            )
            new_content = pattern.sub(lambda m: m.group(0).replace('href="#"', f'href="{url}"'), content, count=1)

            if new_content == content:
                # 逆パターン: href="#" が match_text より前にある場合
                pattern2 = re.compile(
                    r'href="#"((?:(?!</a>).){0,500}' + re.escape(match_text) + r')',
                    re.DOTALL
                )
                new_content = pattern2.sub(f'href="{url}"\\1', content, count=1)

            if new_content != content:
                content = new_content
                changes += 1
                print(f"  OK: {slug} [{match_text}] -> {key}")
            else:
                print(f"  WARN: {slug} [{match_text}] - pattern not found")

        if content != original and not dry_run:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

    return changes


def inject_sim_links(config, dry_run=False):
    """sim-comparison のリンク置換（JavaScript内のテンプレートリテラル修正）"""
    filepath = os.path.join(TOOLS_DIR, 'sim-comparison', 'index.html')
    if not os.path.isfile(filepath):
        print("  SKIP: sim-comparison (file not found)")
        return 0

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # URL マッピングを構築
    url_map = {}
    for provider, key in SIM_PROVIDER_MAP.items():
        url = config.get(key, {}).get('url', '')
        if url:
            url_map[provider] = url

    default_url = config.get('sim_default', {}).get('url', '')

    if not url_map and not default_url:
        print("  SKIP: sim-comparison - no SIM URLs configured")
        return 0

    # JavaScriptにprovider→URLマッピングオブジェクトを注入
    # href="#" をプロバイダーに応じた動的URLに変更
    js_map = json.dumps(url_map, ensure_ascii=False)

    # 既存の href="#" を動的リンクに変更
    old_link = '<a href="#" class="btn-official">公式サイト</a>'
    new_link = f'<a href="${{affiliateUrls[p.provider]||\\"{default_url}\\"}}" class="btn-official" target="_blank" rel="nofollow noopener">公式サイト</a>'

    if old_link in content:
        # マッピングオブジェクトを allPlans の直後に挿入
        content = content.replace(
            'let currentSort="price";',
            f'const affiliateUrls={js_map};\nlet currentSort="price";'
        )
        content = content.replace(old_link, new_link)

        if not dry_run:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

        active = len(url_map)
        print(f"  OK: sim-comparison - {active} providers mapped, default={'set' if default_url else 'none'}")
        return 1

    print("  WARN: sim-comparison - pattern not found (already replaced?)")
    return 0


def main():
    dry_run = '--dry-run' in sys.argv

    if dry_run:
        print("=== DRY RUN (no files will be modified) ===\n")

    print("=== Affiliate Link Injection ===")
    print(f"Config: {CONFIG_PATH}\n")

    config = load_config()

    # 設定済みURL数をカウント
    set_count = sum(1 for k, v in config.items() if isinstance(v, dict) and v.get('url'))
    total = sum(1 for k, v in config.items() if isinstance(v, dict) and 'url' in v)
    print(f"Configured URLs: {set_count}/{total}\n")

    if set_count == 0:
        print("No URLs configured. Edit config/affiliate_links.json first.")
        print("See _HOWTO field in the config file for instructions.")
        return 1

    print("[Tools]")
    tool_changes = inject_tool_links(config, dry_run)

    print("\n[SIM Comparison]")
    sim_changes = inject_sim_links(config, dry_run)

    total_changes = tool_changes + sim_changes
    print(f"\n=== Done: {total_changes} links {'would be ' if dry_run else ''}updated ===")
    return 0


if __name__ == '__main__':
    sys.exit(main())
