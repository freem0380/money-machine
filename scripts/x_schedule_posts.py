#!/usr/bin/env python3
"""X(Twitter) 予約投稿スクリプト - Playwrightで自動スケジュール"""
import sys, os, time, re
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

# --- 投稿データ（本文 + リプライ） ---
POSTS = [
    {
        'id': 'post_02_kakutei',
        'body': (
            '確定申告、ちゃんと準備できてる人どれくらいいる？\n\n'
            '「副業の税金っていくら？」\n'
            '「手取りって結局いくら？」\n\n'
            'この2つに即答できない人、割と多い。\n\n'
            '年収を入れるだけで所得税・住民税・社会保険料を全部自動計算するツールをClaude AIで作った。\n\n'
            '使ってみた人いたら感想教えて。'
        ),
        'reply': 'ツールはこちらです（無料）\nhttps://ai-money-lab.github.io/benri-tools/tax-calculator/',
        'date': None,  # 直近の投稿枠で自動計算
    },
    {
        'id': 'post_01_buzz',
        'body': (
            'Claude AIに「お金の計算ツール16個作って」と頼んだら\n\n'
            '本当に全部作ってくれた。\n\n'
            '・税金計算\n・年収手取り\n・住宅ローン\n・格安SIM比較\n'
            '・新NISA\n・ふるさと納税\n・年金受給額\n・配当金シミュレーション\n他8個\n\n'
            '自分はコード1行も書いてない。\n\n'
            'これ見てまだ「AIは使えない」って言える？'
        ),
        'reply': '全ツール無料で公開してます。\nhttps://ai-money-lab.github.io/benri-tools/',
        'date': None,
    },
    {
        'id': 'post_10_thread',
        'body': (
            'Claude AIで作った無料ツール16個の一覧：\n\n'
            '💰 税金計算\n💼 年収手取り計算\n🏠 住宅ローン計算\n📱 格安SIM13社比較\n'
            '📈 投資リターン計算\n🏦 新NISAシミュレーター\n🎁 ふるさと納税上限額\n'
            '🛡️ 保険必要額計算\n👴 年金受給額計算\n🌴 FIRE達成計算\n💵 配当金計算\n'
            '🏢 不動産利回り\n📋 失業保険計算\n🎯 老後資金計算\n📊 複利計算\n🏡 持ち家vs賃貸\n\n'
            '全部ブラウザで使えて、インストール不要。'
        ),
        'reply': 'こちらからどうぞ\nhttps://ai-money-lab.github.io/benri-tools/',
        'date': None,
        'reply_to_prev': True,  # 前の投稿のスレッドとして投稿
    },
    {
        'id': 'post_03_sim',
        'body': (
            'スマホ代、月いくら払ってますか？\n\n'
            '格安SIM13社を毎日自動で料金収集して比較表にするシステムをClaude AIで作った。\n\n'
            'povo → 基本0円\n日本通信SIM → 1GB 290円\nNUROモバイル → 3GB 792円\n\n'
            '大手キャリアに月7,000円払ってるの、マジでもったいない。'
        ),
        'reply': '13社の最新料金比較はこちら\nhttps://ai-money-lab.github.io/benri-tools/sim-comparison/',
        'date': None,
    },
    {
        'id': 'post_04_nisa',
        'body': (
            '新NISAで月3万円を20年積み立てたら？\n\n'
            '元本：720万円\n運用益：+513万円\n合計：1,233万円\n\n'
            'これ利回り5%の場合だけど、7%なら1,563万円になる。\n\n'
            'この差をちゃんと数字で見たことある人、意外と少ない。'
        ),
        'reply': '自分の条件で計算できるシミュレーター作りました\nhttps://ai-money-lab.github.io/benri-tools/nisa-simulator/',
        'date': None,
    },
    {
        'id': 'post_05_furusato',
        'body': (
            'ふるさと納税で損してる人の特徴：\n\n'
            '「なんとなく3万円くらい」で寄附してる。\n\n'
            '年収500万円・独身なら控除上限は約6万円。\n'
            '年収700万円・共働きなら約10万円。\n\n'
            '上限まで使い切らないと、もらえるはずの返礼品を捨ててるのと同じ。\n\n'
            'あなたの上限額、いくらか知ってる？'
        ),
        'reply': '年収と家族構成を入れるだけで上限額がわかります\nhttps://ai-money-lab.github.io/benri-tools/furusato-tax/',
        'date': None,
    },
    {
        'id': 'post_06_ai',
        'body': (
            '「AIって結局何に使えるの？」\n\n'
            '実例を見せます。\n\n'
            'Claude AIだけで作ったもの：\n'
            '・Webツール16個\n・格安SIMの料金自動収集\n・SNS画像の自動生成\n・毎朝6時に全自動更新\n\n'
            '人間がやったこと：\n・「作って」と指示した\n\n'
            '開発費：0円\n開発期間：2日\n\n'
            'AIを使う側と使わない側、差がつくのはこれからです。'
        ),
        'reply': '全ツールはここで公開してます\nhttps://ai-money-lab.github.io/benri-tools/',
        'date': None,
    },
    {
        'id': 'post_08_fukuri',
        'body': (
            '複利を知ってる人は多い。\n\n'
            'でも「自分の場合いくらになるか」を計算した人は少ない。\n\n'
            '毎月3万円・年利5%の場合：\n\n'
            '10年後 → 466万円（+106万円）\n'
            '20年後 → 1,233万円（+513万円）\n'
            '30年後 → 2,497万円（+1,417万円）\n\n'
            '20年目から爆発的に増える。これが複利の本質。\n\n'
            '始めるのが1年遅れるだけで、30年後に150万円の差が出る。'
        ),
        'reply': '自分の金額・利率で計算できます\nhttps://ai-money-lab.github.io/benri-tools/compound-interest/',
        'date': None,
    },
    {
        'id': 'post_07_ievsyachin',
        'body': (
            '持ち家と賃貸、結局どっちが得なのか。\n\n'
            '感情論じゃなくて数字で比較した。\n\n'
            '4,000万円の物件（金利0.7%・35年ローン）vs 家賃12万円\n\n'
            '35年後の総コスト：\n持ち家 → 約5,800万円\n賃貸 → 約5,400万円\n\n'
            'ただしこれ、条件で全然変わる。\n\n'
            'あなたはどっち派？'
        ),
        'reply': '自分の条件でシミュレーションできます\nhttps://ai-money-lab.github.io/benri-tools/rent-vs-buy/',
        'date': None,
    },
    {
        'id': 'post_09_haitou',
        'body': (
            '配当金で月5万円の不労所得を作るのに必要な金額：\n\n'
            '利回り3% → 2,000万円\n利回り4% → 1,500万円\n利回り5% → 1,200万円\n\n'
            '「遠い」と思うかもしれないけど、月3万円の積立を20年続ければ届く世界。\n\n'
            '配当金生活、あなたなら何年で達成できる？'
        ),
        'reply': '配当シミュレーターで計算してみてください\nhttps://ai-money-lab.github.io/benri-tools/dividend-yield/',
        'date': None,
    },
]


def build_schedule():
    """投稿スケジュールを生成（JST 19:00-20:00 に1日1本）"""
    now = datetime.now()

    # 今日の19:00がまだなら今日から、過ぎてたら明日から
    base = now.replace(hour=19, minute=0, second=0, microsecond=0)
    if now.hour >= 19:
        base += timedelta(days=1)

    # 投稿2と投稿1は同日（投稿2=19:00, 投稿1=20:30）、投稿10は投稿1の直後
    schedule = []
    day_offset = 0
    i = 0
    while i < len(POSTS):
        post = POSTS[i]

        if post.get('reply_to_prev'):
            # スレッド返信は前の投稿の5分後
            prev_time = schedule[-1]['scheduled_at']
            post['date'] = prev_time + timedelta(minutes=5)
        elif i == 1:
            # 投稿1は投稿2の90分後（同日）
            prev_time = schedule[0]['scheduled_at']
            post['date'] = prev_time + timedelta(minutes=90)
        else:
            post['date'] = base + timedelta(days=day_offset)
            # 時間を少しずらす（19:00, 19:05, 19:10...）
            if i > 2:
                day_offset += 1

        schedule.append({
            'id': post['id'],
            'body': post['body'],
            'reply': post['reply'],
            'scheduled_at': post['date'],
            'reply_to_prev': post.get('reply_to_prev', False),
        })
        i += 1

    return schedule


def schedule_post(page, text, schedule_dt):
    """X の予約投稿機能で1件予約する"""
    # 投稿ボタンをクリック（ツイート作成画面を開く）
    try:
        compose_btn = page.locator('[data-testid="SideNav_NewTweet_Button"]')
        if compose_btn.count() > 0 and compose_btn.first.is_visible(timeout=3000):
            compose_btn.first.click()
            time.sleep(1.5)
        else:
            # フォールバック: ショートカットキー
            page.keyboard.press('n')
            time.sleep(1.5)
    except Exception:
        page.keyboard.press('n')
        time.sleep(1.5)

    # テキストを入力
    editor = page.locator('[data-testid="tweetTextarea_0"]')
    if editor.count() == 0:
        # フォールバック
        editor = page.locator('[role="textbox"]')
    editor.first.click()
    time.sleep(0.3)

    # テキストを行ごとに入力（改行はEnter）
    lines = text.split('\n')
    for j, line in enumerate(lines):
        if line:
            page.keyboard.type(line, delay=10)
        if j < len(lines) - 1:
            page.keyboard.press('Enter')
    time.sleep(0.5)

    # 予約アイコンをクリック
    schedule_btn = page.locator('[data-testid="scheduledButton"]')
    if schedule_btn.count() == 0:
        # フォールバック: カレンダーアイコン
        schedule_btn = page.locator('[aria-label*="スケジュール"], [aria-label*="Schedule"]')
    schedule_btn.first.click()
    time.sleep(1)

    # 日付を設定
    # 日付入力フィールドを探す
    date_input = page.locator('[data-testid="scheduledDateField"], input[name="date"]')
    if date_input.count() > 0:
        date_input.first.fill(schedule_dt.strftime('%Y-%m-%d'))
    else:
        # セレクトボックス形式の場合
        set_schedule_selects(page, schedule_dt)

    time.sleep(0.5)

    # 時刻を設定
    time_input = page.locator('[data-testid="scheduledTimeField"], input[name="time"]')
    if time_input.count() > 0:
        time_input.first.fill(schedule_dt.strftime('%H:%M'))

    time.sleep(0.5)

    # 確認ボタン
    confirm_btn = page.locator('[data-testid="scheduledConfirmationPrimaryAction"]')
    if confirm_btn.count() == 0:
        confirm_btn = page.locator('button:has-text("確認"), button:has-text("Confirm")')
    if confirm_btn.count() > 0:
        confirm_btn.first.click()
        time.sleep(1)

    # 予約投稿ボタン
    submit_btn = page.locator('[data-testid="tweetButton"]')
    if submit_btn.count() == 0:
        submit_btn = page.locator('[data-testid="tweetButtonInline"]')
    submit_btn.first.click()
    time.sleep(2)

    return True


def set_schedule_selects(page, dt):
    """セレクトボックス形式の日時設定"""
    # 月
    month_sel = page.locator('select[aria-label*="月"], select[name*="month"]')
    if month_sel.count() > 0:
        month_sel.first.select_option(str(dt.month))

    # 日
    day_sel = page.locator('select[aria-label*="日"], select[name*="day"]')
    if day_sel.count() > 0:
        day_sel.first.select_option(str(dt.day))

    # 年
    year_sel = page.locator('select[aria-label*="年"], select[name*="year"]')
    if year_sel.count() > 0:
        year_sel.first.select_option(str(dt.year))

    # 時間
    hour_sel = page.locator('select[aria-label*="時"], select[name*="hour"]')
    if hour_sel.count() > 0:
        hour_sel.first.select_option(str(dt.hour))

    # 分
    min_sel = page.locator('select[aria-label*="分"], select[name*="minute"]')
    if min_sel.count() > 0:
        # 最も近い選択肢（0, 5, 10, ...）
        minute_rounded = (dt.minute // 5) * 5
        min_sel.first.select_option(str(minute_rounded))


def post_reply(page, reply_text):
    """直前に投稿したポストにリプライする"""
    time.sleep(2)

    # 自分のプロフィールから最新投稿を開く
    page.goto('https://x.com/claude_sidejob', wait_until='domcontentloaded', timeout=15000)
    time.sleep(3)

    # 最新ツイートをクリック
    tweets = page.locator('article[data-testid="tweet"]')
    if tweets.count() > 0:
        tweets.first.click()
        time.sleep(2)

        # リプライ欄に入力
        reply_editor = page.locator('[data-testid="tweetTextarea_0"]')
        if reply_editor.count() == 0:
            reply_editor = page.locator('[role="textbox"]')

        if reply_editor.count() > 0:
            reply_editor.first.click()
            time.sleep(0.3)

            lines = reply_text.split('\n')
            for j, line in enumerate(lines):
                if line:
                    page.keyboard.type(line, delay=10)
                if j < len(lines) - 1:
                    page.keyboard.press('Enter')

            time.sleep(0.5)

            # リプライ送信
            reply_btn = page.locator('[data-testid="tweetButton"]')
            if reply_btn.count() == 0:
                reply_btn = page.locator('[data-testid="tweetButtonInline"]')
            reply_btn.first.click()
            time.sleep(2)
            return True

    return False


def main():
    schedule = build_schedule()

    print('=' * 50)
    print('  X 予約投稿スケジュール')
    print('=' * 50)
    for s in schedule:
        dt_str = s['scheduled_at'].strftime('%m/%d %H:%M')
        print(f"  {dt_str}  {s['id']}")
        print(f"           {s['body'][:40]}...")
        print(f"           リプ: {s['reply'][:40]}...")
        print()

    print(f'合計: {len(schedule)} 件')
    print()

    input('Enterキーで予約投稿を開始します（Ctrl+C でキャンセル）...')

    with sync_playwright() as p:
        # ユーザーデータを使ってログイン済みブラウザを起動
        user_data = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome', 'User Data')
        if os.path.exists(user_data):
            print('Chrome のログイン状態を使用します...')
            context = p.chromium.launch_persistent_context(
                user_data,
                headless=False,
                channel='chrome',
                viewport={'width': 1280, 'height': 900},
                locale='ja-JP',
                args=['--profile-directory=Default'],
            )
            page = context.pages[0] if context.pages else context.new_page()
        else:
            print('新しいブラウザを起動します。Xにログインしてください。')
            browser = p.chromium.launch(headless=False)
            page = browser.new_page(viewport={'width': 1280, 'height': 900}, locale='ja-JP')

        # X を開く
        page.goto('https://x.com/home', wait_until='domcontentloaded', timeout=30000)
        time.sleep(3)

        # ログイン確認
        if 'login' in page.url.lower() or 'i/flow' in page.url.lower():
            print('\n⚠️  Xにログインしてください。ログイン後にEnterを押してください。')
            input('ログイン完了後、Enterキーを押してください...')
            time.sleep(2)

        page.screenshot(path=os.path.join(LOGS_DIR, 'x_home.png'))
        print(f'ログイン確認: {page.url}')

        results = {}
        for i, s in enumerate(schedule):
            post_id = s['id']
            dt = s['scheduled_at']
            print(f"\n--- [{i+1}/{len(schedule)}] {post_id} ({dt.strftime('%m/%d %H:%M')}) ---")

            try:
                # ホームに戻る
                page.goto('https://x.com/home', wait_until='domcontentloaded', timeout=15000)
                time.sleep(2)

                # 予約投稿
                ok = schedule_post(page, s['body'], dt)
                page.screenshot(path=os.path.join(LOGS_DIR, f'x_scheduled_{post_id}.png'))

                if ok:
                    print(f'  ✅ 本文を {dt.strftime("%m/%d %H:%M")} に予約')

                    # リプライも同時刻+1分で予約（リンク付き）
                    time.sleep(1)
                    page.goto('https://x.com/home', wait_until='domcontentloaded', timeout=15000)
                    time.sleep(2)
                    reply_dt = dt + timedelta(minutes=1)
                    schedule_post(page, s['reply'], reply_dt)
                    print(f'  ✅ リプライを {reply_dt.strftime("%m/%d %H:%M")} に予約')

                    results[post_id] = 'scheduled'
                else:
                    results[post_id] = 'failed'
                    print(f'  ❌ 予約失敗')

            except Exception as e:
                results[post_id] = f'error: {e}'
                print(f'  ❌ エラー: {e}')
                page.screenshot(path=os.path.join(LOGS_DIR, f'x_error_{post_id}.png'))

            time.sleep(2)

        # 結果サマリー
        print(f"\n{'=' * 50}")
        print(f'  予約投稿結果')
        print(f"{'=' * 50}")
        for post_id, result in results.items():
            print(f'  [{result:15s}] {post_id}')

        scheduled = sum(1 for v in results.values() if v == 'scheduled')
        print(f'\n  成功: {scheduled}/{len(schedule)}')

        if hasattr(page.context, 'close'):
            page.context.close()
        else:
            page.close()


if __name__ == '__main__':
    main()
