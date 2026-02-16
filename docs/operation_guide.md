# Money Machine 運用ガイド

## 全体像

```
[自動] 毎朝6:00                    [手動] あなたがやること
  |                                    |
  v                                    v
SIMデータ収集                      X投稿をコピペ（1日1本）
  ↓                                A8.netでアフィリエイト提携申請
比較表HTML更新                     新ツール追加の指示
  ↓
SNS画像生成
  ↓
サイトインデックス更新
  ↓
GitHub Pagesに自動デプロイ
```

---

## 1. 自動で動いていること（触らなくてOK）

### Windows タスクスケジューラ（毎朝6:00）
以下が自動実行される：
- 格安SIM 13社の最新料金データを収集
- SIM比較表HTMLを最新データで更新
- SNS用ランキング画像を自動生成
- サイトインデックスページを更新

### GitHub Actions（push時 + 毎日21:00 UTC）
- GitHub Pagesに自動デプロイ
- サイトURL: https://freem0380.github.io/benri-tools/

### 確認方法
```
ブラウザで https://freem0380.github.io/benri-tools/ を開く
→ ツール一覧が表示されればOK
```

---

## 2. 手動でやること

### A) X投稿（1日1本、5分）

**手順：**
1. `output/social/x_posts_claude_sidejob.md` を開く
2. 今日の投稿テキストをコピー
3. https://x.com にログイン（@claude_sidejob）
4. 投稿欄にペースト
5. 画像を付けたい場合 → `output/social/` の `.png` をドラッグ＆ドロップ
6. 「ポストする」

**投稿スケジュール（推奨）：**

| 日付 | 内容 | 投稿テキスト番号 |
|------|------|-----------------|
| 2/16(日) | 確定申告ツール | 投稿2 |
| 2/17(月) | バズ狙い（16個作った話） | 投稿1 → 返信で投稿10 |
| 2/18(火) | SIM比較 | 投稿3 |
| 2/19(水) | 新NISA | 投稿4 |
| 2/20(木) | ふるさと納税 | 投稿5 |
| 2/21(金) | AI活用事例 | 投稿6 |
| 2/22(土) | 複利計算 | 投稿8 |
| 2/23(日) | 持ち家vs賃貸 | 投稿7 |
| 2/24(月) | 配当金 | 投稿9 |

**投稿のベスト時間帯：**
- 朝 7:00-8:00（通勤時間帯）
- 昼 12:00-13:00（昼休み）
- 夜 20:00-22:00（ゴールデンタイム）

---

### B) アフィリエイトリンクの取得（1回やれば完了）

現在アフィリエイト収益が発生するリンクは **マネーフォワード（A8.net）の1件のみ**。
他のツールにもリンクを設定すると収益が増える。

**手順：**
1. https://www.a8.net/ にログイン
   - ID: freemlife
2. 上部メニュー「プログラム検索」をクリック
3. 案件名で検索（例：「RENOSY」「モゲチェック」「保険見直しラボ」）
4. 見つかったら「提携申請する」をクリック
5. 提携完了後「広告リンク作成」→ URLをコピー
6. `config/affiliate_links.json` の該当案件の `url` を書き換え
7. Claude Codeで `python scripts/inject_affiliate_links.py` を実行

**申請すべき案件一覧：**

| 案件 | 検索キーワード | ツール |
|------|---------------|--------|
| RENOSY | RENOSY リノシー | 不動産利回り |
| マネードクター | マネードクター | 保険計算 |
| 保険見直しラボ | 保険見直しラボ | 保険計算 |
| モゲチェック | モゲチェック | 住宅ローン |
| 税理士ドットコム | 税理士ドットコム | 税金計算 |
| WealthNavi | ウェルスナビ | NISA・投資 |
| SBI証券 | SBI証券 | 投資リターン |

詳細ガイド → `docs/a8_partnership_guide.html` をブラウザで開く

---

### C) 新しいツールを追加したいとき

Claude Codeで以下を実行：
```
/build-tool [slug名]
```

例：
```
/build-tool education-cost
```

現在16個が公開中、あと36個が未作成。
追加するたびにサイトが充実する。

---

## 3. 収益の仕組み

```
X投稿 → ツールに集客 → アフィリエイトリンクをクリック → 成約 → 報酬
```

**収益を増やす3つのレバー：**
1. **ツールの数を増やす** → 入口が増える（現在16/52）
2. **X投稿を続ける** → アクセスが増える
3. **アフィリエイト提携を増やす** → クリック→報酬の導線が増える

**報酬の目安（A8.net）：**
- RENOSY → 面談完了で 30,000〜50,000円
- マネードクター → 面談完了で 10,000〜15,000円
- WealthNavi → 口座開設で 3,000〜5,000円
- SBI証券 → 口座開設で 2,000〜3,000円
- モゲチェック → 相談申込で 5,000〜10,000円

---

## 4. フォルダ構成

```
money-machine/
├── output/
│   ├── tools/          ← 公開中のHTMLツール（16個）
│   │   ├── index.html  ← ツール一覧ページ
│   │   ├── tax-calculator/
│   │   ├── sim-comparison/
│   │   └── ...
│   └── social/         ← X投稿テンプレート＆画像
│       ├── x_posts_claude_sidejob.md  ← 投稿テキスト
│       ├── 2026-02-16_sim_ranking.png
│       └── 2026-02-16_tool_highlight.png
├── config/
│   └── affiliate_links.json  ← アフィリエイトURL設定
├── data/
│   └── money_machine.db      ← 全データ（SQLite）
├── scripts/                   ← 自動実行スクリプト群
├── docs/
│   ├── operation_guide.md     ← このファイル
│   └── a8_partnership_guide.html ← A8提携申請ガイド
└── logs/                      ← 実行ログ
```

---

## 5. トラブルシューティング

### サイトが更新されない
→ Claude Codeで実行：
```
cd money-machine
git add . && git commit -m "update" && git push origin main
```

### 日次実行が動いているか確認
→ Claude Codeで実行：
```
python scripts/status.py
```

### 手動で日次処理を実行
→ Claude Codeで実行：
```
python scripts/daily_run.py
```

### SIMデータが古い
→ Claude Codeで実行：
```
python scrapers/sim_scraper.py
```
