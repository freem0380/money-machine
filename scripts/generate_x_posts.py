#!/usr/bin/env python3
"""X(Twitter)投稿テンプレート生成 - ツール紹介投稿を自動生成"""
import sys, os, json, sqlite3, random
from datetime import datetime, timedelta
sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(BASE_DIR, 'data', 'money_machine.db')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output', 'social')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# GitHub Pages URL
SITE_URL = 'https://ai-money-lab.github.io/benri-tools'

TOOL_POSTS = {
    'sim-comparison': {
        'emoji': '📱',
        'hook': '格安SIMどれが安い？13社を一覧比較！',
        'body': '月額料金・データ量・通話料をひと目で比較。\nあなたに最適なプランが見つかります。',
        'tags': '#格安SIM #節約 #通信費削減 #スマホ料金',
    },
    'tax-calculator': {
        'emoji': '💰',
        'hook': '手取り額、正確に計算できてますか？',
        'body': '年収を入力するだけで所得税・住民税・社会保険料を自動計算。\n確定申告の準備にも。',
        'tags': '#確定申告 #税金計算 #手取り額 #節税',
    },
    'salary-calculator': {
        'emoji': '💼',
        'hook': '年収から手取りを即計算！',
        'body': '社会保険料・所得税・住民税を自動計算。\n転職時の年収比較にも使えます。',
        'tags': '#年収 #手取り #転職 #給料計算',
    },
    'loan-calculator': {
        'emoji': '🏠',
        'hook': '住宅ローン、月々いくら返す？',
        'body': '借入額・金利・期間を入力で月々の返済額を即計算。\n繰上返済シミュレーションも。',
        'tags': '#住宅ローン #マイホーム #ローン計算 #不動産',
    },
    'investment-return': {
        'emoji': '📈',
        'hook': '投資したらいくら増える？',
        'body': '元本・利回り・期間から将来の資産額をシミュレーション。\nグラフで成長を可視化。',
        'tags': '#投資 #資産運用 #NISA #複利効果',
    },
    'nisa-simulator': {
        'emoji': '🏦',
        'hook': '新NISAでいくら貯まる？',
        'body': 'つみたて投資枠・成長投資枠の非課税メリットを計算。\n将来の資産形成をシミュレーション。',
        'tags': '#新NISA #つみたてNISA #資産形成 #非課税',
    },
    'insurance-calculator': {
        'emoji': '🛡️',
        'hook': '必要な保険金額、計算してみませんか？',
        'body': '家族構成・収入から必要保障額を自動計算。\nムダな保険料を見直すきっかけに。',
        'tags': '#生命保険 #保険見直し #必要保障額 #節約',
    },
    'pension-calculator': {
        'emoji': '👴',
        'hook': '将来もらえる年金額は？',
        'body': '加入期間・平均年収から年金受給額を試算。\n老後の資金計画に。',
        'tags': '#年金 #老後資金 #年金計算 #将来設計',
    },
    'retirement-calculator': {
        'emoji': '🌴',
        'hook': 'FIREに必要な金額は？',
        'body': '目標年齢・生活費・投資リターンからFIRE達成に必要な資産を計算。',
        'tags': '#FIRE #早期退職 #経済的自立 #資産運用',
    },
    'dividend-yield': {
        'emoji': '💵',
        'hook': '配当金で月5万円得るには？',
        'body': '投資額・配当利回りから年間配当金を計算。\n高配当株ポートフォリオの設計に。',
        'tags': '#配当金 #高配当株 #不労所得 #投資',
    },
    'real-estate-yield': {
        'emoji': '🏢',
        'hook': 'その不動産、利回りは何%？',
        'body': '物件価格・家賃・経費から表面利回り・実質利回りを計算。',
        'tags': '#不動産投資 #利回り #ワンルーム投資 #資産運用',
    },
    'unemployment-benefit': {
        'emoji': '📋',
        'hook': '失業手当、いくらもらえる？',
        'body': '勤続年数・年齢・給与から失業給付金額と期間を自動計算。',
        'tags': '#失業保険 #雇用保険 #失業手当 #転職',
    },
    'retirement-fund': {
        'emoji': '🎯',
        'hook': '老後資金2000万円、本当に必要？',
        'body': 'あなたの状況で必要な老後資金を個別にシミュレーション。',
        'tags': '#老後2000万円 #老後資金 #年金 #資産形成',
    },
    'furusato-tax': {
        'emoji': '🎁',
        'hook': 'ふるさと納税、控除上限額いくら？',
        'body': '年収・家族構成を入力するだけで控除上限額を即計算。\nお得にふるさと納税を始めよう。',
        'tags': '#ふるさと納税 #控除上限額 #節税 #返礼品',
    },
    'compound-interest': {
        'emoji': '📊',
        'hook': '複利の力、計算してみませんか？',
        'body': '元本・利率・期間を入力で将来の資産額をシミュレーション。\n複利の効果をグラフで実感。',
        'tags': '#複利 #資産運用 #投資 #積立投資',
    },
    'rent-vs-buy': {
        'emoji': '🏡',
        'hook': '持ち家と賃貸、どっちが得？',
        'body': '物件価格・家賃・期間を入力で総コストを比較。\n住宅購入の判断材料に。',
        'tags': '#持ち家vs賃貸 #住宅購入 #マイホーム #家賃',
    },
}


def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')

    posts = []
    for slug, info in TOOL_POSTS.items():
        url = f'{SITE_URL}/{slug}/'
        text = f"{info['emoji']} {info['hook']}\n\n{info['body']}\n\n無料で使えます👇\n{url}\n\n{info['tags']}"

        posts.append({
            'slug': slug,
            'text': text,
            'chars': len(text),
        })

        # Insert to social_posts
        c.execute('''INSERT OR IGNORE INTO social_posts
                     (platform, content_type, content_text, media_path, status, scheduled_at, created_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  ('x', 'tool_promo', text, '', 'draft',
                   (datetime.now() + timedelta(hours=random.randint(1, 72))).isoformat(),
                   datetime.now().isoformat()))

    conn.commit()
    conn.close()

    # Save posts to JSON for reference
    output_path = os.path.join(OUTPUT_DIR, f'{today}_x_posts.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

    print(f"Generated {len(posts)} X post templates")
    print(f"Saved to: {output_path}")
    print(f"Inserted into social_posts table\n")

    # Show sample posts
    for p in posts[:3]:
        print(f"--- {p['slug']} ({p['chars']} chars) ---")
        print(p['text'])
        print()


if __name__ == '__main__':
    main()
