#!/usr/bin/env python3
"""
social_image_generator.py
SNS (X/Twitter) 用の画像とテキストを自動生成するスクリプト。
DBの比較データからランキング画像を生成し、social_postsテーブルに記録する。
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

import os
import sqlite3
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "money_machine.db"
OUTPUT_DIR = BASE_DIR / "output" / "social"
SITE_URL = "ai-money-lab.github.io/benri-tools"

# Image dimensions (Twitter card)
IMG_W = 1200
IMG_H = 630

# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------
COLOR_BG = "#FFFFFF"
COLOR_TITLE_BG = "#1DA1F2"          # Twitter-blue header band
COLOR_TITLE_TEXT = "#FFFFFF"
COLOR_BODY_TEXT = "#1A1A2E"
COLOR_ACCENT = "#E63946"
COLOR_RANK_GOLD = "#FFD700"
COLOR_RANK_SILVER = "#C0C0C0"
COLOR_RANK_BRONZE = "#CD7F32"
COLOR_RANK_DEFAULT = "#4A90D9"
COLOR_PRICE = "#E63946"
COLOR_PROVIDER = "#16213E"
COLOR_PLAN = "#555555"
COLOR_FOOTER_BG = "#F0F4F8"
COLOR_FOOTER_TEXT = "#666666"
COLOR_DIVIDER = "#E0E0E0"
COLOR_HIGHLIGHT_BG = "#FFF9E6"
COLOR_TOOL_CARD_BG = "#F8F9FA"
COLOR_TOOL_ACCENT = "#2ECC71"

RANK_COLORS = [COLOR_RANK_GOLD, COLOR_RANK_SILVER, COLOR_RANK_BRONZE]

# ---------------------------------------------------------------------------
# Font helpers (Meiryo on Windows, fallback to MS Gothic, then default)
# ---------------------------------------------------------------------------

def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Load a Japanese-capable font at the given size."""
    candidates = []
    if bold:
        candidates += ["meiryob.ttc", "msgothic.ttc"]
    candidates += ["meiryo.ttc", "msgothic.ttc", "yugothm.ttc"]
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except (OSError, IOError):
            continue
    # Last resort: Pillow default (no Japanese support)
    return ImageFont.load_default()


FONT_TITLE = _load_font(36, bold=True)
FONT_SUBTITLE = _load_font(22)
FONT_RANK_NUM = _load_font(32, bold=True)
FONT_PROVIDER = _load_font(24, bold=True)
FONT_PLAN = _load_font(18)
FONT_PRICE = _load_font(28, bold=True)
FONT_PRICE_UNIT = _load_font(16)
FONT_FOOTER = _load_font(16)
FONT_TOOL_NAME = _load_font(30, bold=True)
FONT_TOOL_DESC = _load_font(20)
FONT_DATE = _load_font(14)


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def fetch_sim_ranking(limit: int = 7) -> list[dict]:
    """Fetch top cheapest SIM plans from comparison_data."""
    conn = get_db()
    rows = conn.execute(
        """
        SELECT provider, plan_name, price, data_gb, data_json
        FROM comparison_data
        WHERE category = 'sim' AND is_current = 1
        ORDER BY price ASC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def fetch_random_tool() -> dict | None:
    """Pick a random tool from the tools table."""
    conn = get_db()
    rows = conn.execute(
        "SELECT id, name, slug, category, file_path, deploy_url FROM tools"
    ).fetchall()
    conn.close()
    if not rows:
        return None
    return dict(random.choice(rows))


def insert_social_post(platform: str, content_type: str, content_text: str,
                       media_path: str, scheduled_at: str) -> int:
    """Insert a social_posts record and return the new row id."""
    conn = get_db()
    cur = conn.execute(
        """
        INSERT INTO social_posts
            (platform, content_type, content_text, media_path, status, scheduled_at)
        VALUES (?, ?, ?, ?, 'draft', ?)
        """,
        (platform, content_type, content_text, media_path, scheduled_at),
    )
    conn.commit()
    row_id = cur.lastrowid
    conn.close()
    return row_id


# ---------------------------------------------------------------------------
# Placeholder data (used when DB is empty)
# ---------------------------------------------------------------------------

PLACEHOLDER_SIM_DATA = [
    {"provider": "povo",          "plan_name": "povo2.0 基本料",       "price": 0,    "data_gb": 0},
    {"provider": "日本通信SIM",   "plan_name": "合理的シンプル290 1GB", "price": 290,  "data_gb": 1},
    {"provider": "NUROモバイル",  "plan_name": "VSプラン 3GB",         "price": 792,  "data_gb": 3},
    {"provider": "IIJmio",        "plan_name": "2ギガプラン",          "price": 850,  "data_gb": 2},
    {"provider": "LINEMO",        "plan_name": "ミニプラン 3GB",       "price": 990,  "data_gb": 3},
    {"provider": "mineo",         "plan_name": "マイそく スタンダード", "price": 990, "data_gb": 999},
    {"provider": "楽天モバイル",  "plan_name": "Rakuten最強プラン 3GB", "price": 1078, "data_gb": 3},
]

PLACEHOLDER_TOOL = {
    "id": 0,
    "name": "年収手取り計算機",
    "slug": "salary-calculator",
    "category": "calculator",
    "file_path": "output/tools/salary-calculator/index.html",
    "deploy_url": None,
}


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def _text_size(draw: ImageDraw.ImageDraw, text: str, font) -> tuple[int, int]:
    """Return (width, height) of rendered text, compatible across Pillow versions."""
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def _draw_rounded_rect(draw: ImageDraw.ImageDraw, xy, radius, fill):
    """Draw a rounded rectangle."""
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


def _draw_header(draw: ImageDraw.ImageDraw, title: str, subtitle: str = ""):
    """Draw the blue header band with title."""
    # Header background
    draw.rectangle([0, 0, IMG_W, 90], fill=COLOR_TITLE_BG)

    # Title (centered)
    tw, th = _text_size(draw, title, FONT_TITLE)
    tx = (IMG_W - tw) // 2
    draw.text((tx, 20), title, fill=COLOR_TITLE_TEXT, font=FONT_TITLE)

    # Subtitle
    if subtitle:
        sw, sh = _text_size(draw, subtitle, FONT_SUBTITLE)
        sx = (IMG_W - sw) // 2
        draw.text((sx, 64), subtitle, fill="#D0E8FF", font=FONT_SUBTITLE)


def _draw_footer(draw: ImageDraw.ImageDraw, today_str: str):
    """Draw footer with site URL and date."""
    footer_y = IMG_H - 50
    draw.rectangle([0, footer_y, IMG_W, IMG_H], fill=COLOR_FOOTER_BG)
    draw.line([(0, footer_y), (IMG_W, footer_y)], fill=COLOR_DIVIDER, width=1)

    # Site URL (left)
    draw.text((30, footer_y + 14), SITE_URL, fill=COLOR_FOOTER_TEXT, font=FONT_FOOTER)

    # Date (right)
    date_text = today_str
    dw, _ = _text_size(draw, date_text, FONT_DATE)
    draw.text((IMG_W - dw - 30, footer_y + 16), date_text, fill=COLOR_FOOTER_TEXT, font=FONT_DATE)

    # Center tagline
    tagline = "-- Data updated automatically --"
    tgw, _ = _text_size(draw, tagline, FONT_DATE)
    draw.text(((IMG_W - tgw) // 2, footer_y + 16), tagline,
              fill="#AAAAAA", font=FONT_DATE)


# ---------------------------------------------------------------------------
# Image generators
# ---------------------------------------------------------------------------

def generate_sim_ranking_image(today_str: str) -> tuple[str, str]:
    """
    Generate a SIM ranking image.
    Returns (image_path, tweet_text).
    """
    # Fetch data
    sims = fetch_sim_ranking(7)
    if not sims:
        sims = PLACEHOLDER_SIM_DATA
        print("[INFO] comparison_data にSIMデータなし。プレースホルダーを使用。")

    img = Image.new("RGB", (IMG_W, IMG_H), COLOR_BG)
    draw = ImageDraw.Draw(img)

    # Header
    _draw_header(draw, "格安SIM 月額料金ランキング", f"{today_str} 更新")

    # Body: ranking rows
    start_y = 105
    row_h = 68
    margin_x = 40

    for i, sim in enumerate(sims):
        y = start_y + i * row_h

        # Alternating background
        if i % 2 == 0:
            draw.rectangle([margin_x - 10, y - 4, IMG_W - margin_x + 10, y + row_h - 8],
                           fill="#F8FAFC")

        # Rank badge
        rank = i + 1
        badge_color = RANK_COLORS[i] if i < 3 else COLOR_RANK_DEFAULT
        badge_cx = margin_x + 22
        badge_cy = y + 24
        badge_r = 20
        draw.ellipse([badge_cx - badge_r, badge_cy - badge_r,
                      badge_cx + badge_r, badge_cy + badge_r],
                     fill=badge_color)
        rank_text = str(rank)
        rw, rh = _text_size(draw, rank_text, FONT_RANK_NUM)
        draw.text((badge_cx - rw // 2, badge_cy - rh // 2 - 2),
                  rank_text, fill="#FFFFFF", font=FONT_RANK_NUM)

        # Provider name
        provider = sim["provider"]
        draw.text((margin_x + 60, y + 4), provider,
                  fill=COLOR_PROVIDER, font=FONT_PROVIDER)

        # Plan name
        plan = sim["plan_name"]
        draw.text((margin_x + 60, y + 32), plan,
                  fill=COLOR_PLAN, font=FONT_PLAN)

        # Data GB (middle area)
        data_gb = sim["data_gb"]
        if data_gb == 0:
            gb_text = "---"
        elif data_gb >= 900:
            gb_text = "使い放題"
        else:
            gb_val = int(data_gb) if data_gb == int(data_gb) else data_gb
            gb_text = f"{gb_val}GB"
        gw, _ = _text_size(draw, gb_text, FONT_PLAN)
        draw.text((700 - gw // 2, y + 16), gb_text,
                  fill=COLOR_PLAN, font=FONT_PLAN)

        # Price (right-aligned)
        price = sim["price"]
        if price == 0:
            price_str = "0"
        else:
            price_str = f"{int(price):,}"
        unit = "円/月"
        pw, ph = _text_size(draw, price_str, FONT_PRICE)
        uw, uh = _text_size(draw, unit, FONT_PRICE_UNIT)
        price_right = IMG_W - margin_x - 10
        draw.text((price_right - pw - uw - 4, y + 8),
                  price_str, fill=COLOR_PRICE, font=FONT_PRICE)
        draw.text((price_right - uw, y + 18),
                  unit, fill=COLOR_PLAN, font=FONT_PRICE_UNIT)

    # Footer
    _draw_footer(draw, today_str)

    # Save
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{today_str}_sim_ranking.png"
    filepath = OUTPUT_DIR / filename
    img.save(str(filepath), "PNG")
    print(f"[OK] SIMランキング画像を生成: {filepath}")

    # Tweet text
    top3_lines = []
    for i, s in enumerate(sims[:3]):
        medal = ["1.", "2.", "3."][i]
        p = int(s["price"])
        top3_lines.append(f"{medal} {s['provider']} {s['plan_name']} ... {p:,}円/月")

    tweet = (
        f"【格安SIM月額ランキング】{today_str} 更新\n"
        "\n"
        + "\n".join(top3_lines) + "\n"
        "\n"
        f"全ランキング・比較ツールはこちら\n"
        f"https://{SITE_URL}/tools/telecom-savings/\n"
        "\n"
        "#格安SIM #スマホ料金 #通信費節約 #携帯乗り換え"
    )

    return str(filepath), tweet


def generate_tool_highlight_image(today_str: str) -> tuple[str, str]:
    """
    Generate a 'today's recommended tool' image.
    Returns (image_path, tweet_text).
    """
    tool = fetch_random_tool()
    if not tool:
        tool = PLACEHOLDER_TOOL
        print("[INFO] tools テーブルが空。プレースホルダーを使用。")

    img = Image.new("RGB", (IMG_W, IMG_H), COLOR_BG)
    draw = ImageDraw.Draw(img)

    # Header
    _draw_header(draw, "今日のおすすめツール")

    # Tool card area
    card_margin = 60
    card_top = 115
    card_bottom = IMG_H - 70
    _draw_rounded_rect(draw,
                       [card_margin, card_top, IMG_W - card_margin, card_bottom],
                       radius=16, fill=COLOR_TOOL_CARD_BG)

    # Green accent bar on left
    draw.rectangle([card_margin, card_top + 20, card_margin + 8, card_bottom - 20],
                   fill=COLOR_TOOL_ACCENT)

    # Tool name
    tool_name = tool["name"]
    tnw, tnh = _text_size(draw, tool_name, FONT_TOOL_NAME)
    name_x = (IMG_W - tnw) // 2
    name_y = card_top + 40
    draw.text((name_x, name_y), tool_name,
              fill=COLOR_BODY_TEXT, font=FONT_TOOL_NAME)

    # Divider
    div_y = name_y + tnh + 25
    draw.line([(card_margin + 40, div_y), (IMG_W - card_margin - 40, div_y)],
              fill=COLOR_DIVIDER, width=2)

    # Category badge
    cat_text = f"カテゴリ: {tool['category']}"
    cw, ch = _text_size(draw, cat_text, FONT_TOOL_DESC)
    cat_x = (IMG_W - cw) // 2
    cat_y = div_y + 20
    draw.text((cat_x, cat_y), cat_text,
              fill=COLOR_PLAN, font=FONT_TOOL_DESC)

    # Description / slug
    slug_text = tool["slug"]
    url_text = f"https://{SITE_URL}/tools/{slug_text}/"
    uw, uh = _text_size(draw, url_text, FONT_TOOL_DESC)
    url_x = (IMG_W - uw) // 2
    url_y = cat_y + ch + 25
    draw.text((url_x, url_y), url_text,
              fill=COLOR_RANK_DEFAULT, font=FONT_TOOL_DESC)

    # Feature bullets
    features = [
        "無料で使える計算・シミュレーションツール",
        "スマホ対応 -- いつでもどこでも利用可能",
        "データは自動更新 -- 常に最新情報",
    ]
    bullet_y = url_y + uh + 35
    for feat in features:
        feat_display = f"  {feat}"
        fw, fh = _text_size(draw, feat_display, FONT_PLAN)
        fx = (IMG_W - fw) // 2
        draw.text((fx, bullet_y), feat_display,
                  fill=COLOR_BODY_TEXT, font=FONT_PLAN)
        bullet_y += fh + 12

    # Footer
    _draw_footer(draw, today_str)

    # Save
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{today_str}_tool_highlight.png"
    filepath = OUTPUT_DIR / filename
    img.save(str(filepath), "PNG")
    print(f"[OK] ツール紹介画像を生成: {filepath}")

    # Tweet text
    tweet = (
        f"【無料ツール紹介】{tool_name}\n"
        "\n"
        f"{tool['category']}カテゴリの便利ツールです。\n"
        "ブラウザだけで使えて、インストール不要。\n"
        "\n"
        f"https://{SITE_URL}/tools/{slug_text}/\n"
        "\n"
        "#無料ツール #家計管理 #節約 #マネーツール"
    )

    return str(filepath), tweet


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    today_str = datetime.now().strftime("%Y-%m-%d")
    scheduled_at = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")

    print(f"=== Social Image Generator === {today_str}")
    print(f"DB: {DB_PATH}")
    print(f"Output: {OUTPUT_DIR}")
    print()

    results = []

    # 1. SIM Ranking image
    try:
        img_path, tweet_text = generate_sim_ranking_image(today_str)
        rel_path = str(Path(img_path).relative_to(BASE_DIR))
        row_id = insert_social_post(
            platform="twitter",
            content_type="sim-ranking",
            content_text=tweet_text,
            media_path=rel_path,
            scheduled_at=scheduled_at,
        )
        results.append(("sim-ranking", img_path, row_id))
        print(f"  -> social_posts に登録 (id={row_id})")
        print(f"  -> ツイート文:\n{tweet_text}\n")
    except Exception as e:
        print(f"[ERROR] SIMランキング画像生成失敗: {e}")

    # 2. Tool highlight image
    try:
        img_path, tweet_text = generate_tool_highlight_image(today_str)
        rel_path = str(Path(img_path).relative_to(BASE_DIR))
        scheduled_at_2 = (datetime.now() + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")
        row_id = insert_social_post(
            platform="twitter",
            content_type="tool-highlight",
            content_text=tweet_text,
            media_path=rel_path,
            scheduled_at=scheduled_at_2,
        )
        results.append(("tool-highlight", img_path, row_id))
        print(f"  -> social_posts に登録 (id={row_id})")
        print(f"  -> ツイート文:\n{tweet_text}\n")
    except Exception as e:
        print(f"[ERROR] ツール紹介画像生成失敗: {e}")

    # Summary
    print("=" * 50)
    print(f"生成完了: {len(results)} 件")
    for content_type, path, rid in results:
        print(f"  [{content_type}] {path}  (post_id={rid})")
    print("=" * 50)


if __name__ == "__main__":
    main()
