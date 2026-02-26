"""
YouTube Comments Analyzer using Claude AI
Парсит комментарии YouTube и анализирует их через Claude API
"""

import os
import json
import argparse
from datetime import datetime
from googleapiclient.discovery import build
import anthropic


# ─────────────────────────────────────────────
# YouTube Parser
# ─────────────────────────────────────────────

def get_video_id(url_or_id: str) -> str:
    """Извлекает video_id из URL или возвращает как есть."""
    import re
    patterns = [
        r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})",
        r"^([A-Za-z0-9_-]{11})$",
    ]
    for p in patterns:
        m = re.search(p, url_or_id)
        if m:
            return m.group(1)
    raise ValueError(f"Не удалось извлечь video_id из: {url_or_id}")


def fetch_comments(video_id: str, max_comments: int = 100) -> list[dict]:
    """
    Получает комментарии к видео через YouTube Data API v3.
    Возвращает список словарей с полями: author, text, likes, published_at.
    """
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        raise EnvironmentError("Переменная YOUTUBE_API_KEY не задана.")

    youtube = build("youtube", "v3", developerKey=api_key)
    comments = []
    next_page_token = None

    print(f"⏳ Загрузка комментариев для video_id={video_id}...")

    while len(comments) < max_comments:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=min(100, max_comments - len(comments)),
            pageToken=next_page_token,
            textFormat="plainText",
            order="relevance",
        )
        response = request.execute()

        for item in response.get("items", []):
            snippet = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "author": snippet.get("authorDisplayName", "Unknown"),
                "text": snippet.get("textDisplay", ""),
                "likes": snippet.get("likeCount", 0),
                "published_at": snippet.get("publishedAt", ""),
            })

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    print(f"✅ Загружено {len(comments)} комментариев.")
    return comments


# ─────────────────────────────────────────────
# Claude Analyzer
# ─────────────────────────────────────────────

ANALYSIS_PROMPT = """
Ты — аналитик аудитории. Тебе предоставлены {count} комментариев с YouTube-видео.

Проведи глубокий анализ и верни **строго валидный JSON** следующей структуры (без markdown-блоков):

{{
  "summary": "Краткое резюме обсуждения (2-3 предложения)",
  "overall_sentiment": "positive | negative | neutral | mixed",
  "sentiment_breakdown": {{
    "positive_pct": 0,
    "neutral_pct": 0,
    "negative_pct": 0
  }},
  "top_topics": ["тема 1", "тема 2", "тема 3"],
  "key_insights": ["инсайт 1", "инсайт 2", "инсайт 3"],
  "audience_profile": "Описание аудитории (1-2 предложения)",
  "recommendations": ["рекомендация 1", "рекомендация 2"],
  "notable_comments": [
    {{"author": "...", "text": "...", "reason": "почему выделен"}}
  ]
}}

Комментарии:
{comments_text}
"""


def analyze_with_claude(comments: list[dict], model: str = "claude-opus-4-6") -> dict:
    """
    Отправляет комментарии в Claude API для анализа.
    Возвращает структурированный результат.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("Переменная ANTHROPIC_API_KEY не задана.")

    client = anthropic.Anthropic(api_key=api_key)

    # Формируем текст комментариев
    comments_text = "\n\n".join(
        f"[{i+1}] @{c['author']} ({c['likes']} лайков):\n{c['text']}"
        for i, c in enumerate(comments)
    )

    prompt = ANALYSIS_PROMPT.format(
        count=len(comments),
        comments_text=comments_text,
    )

    print(f"🤖 Отправка в Claude ({model})...")

    message = client.messages.create(
        model=model,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_response = message.content[0].text

    try:
        result = json.loads(raw_response)
    except json.JSONDecodeError:
        # Попытка вытащить JSON если модель добавила лишний текст
        import re
        match = re.search(r"\{.*\}", raw_response, re.DOTALL)
        if match:
            result = json.loads(match.group())
        else:
            result = {"raw_response": raw_response}

    return result


# ─────────────────────────────────────────────
# Report Generator
# ─────────────────────────────────────────────

def print_report(analysis: dict, video_id: str):
    """Красиво выводит результат анализа в консоль."""
    sep = "─" * 60
    print(f"\n{sep}")
    print(f"  📊 АНАЛИЗ КОММЕНТАРИЕВ  |  video: {video_id}")
    print(sep)

    print(f"\n📝 Резюме:\n   {analysis.get('summary', 'N/A')}")
    print(f"\n🎭 Тональность: {analysis.get('overall_sentiment', 'N/A').upper()}")

    sb = analysis.get("sentiment_breakdown", {})
    if sb:
        print(
            f"   👍 Позитив: {sb.get('positive_pct', 0)}%  "
            f"😐 Нейтрал: {sb.get('neutral_pct', 0)}%  "
            f"👎 Негатив: {sb.get('negative_pct', 0)}%"
        )

    topics = analysis.get("top_topics", [])
    if topics:
        print(f"\n🏷️  Топ темы:")
        for t in topics:
            print(f"   • {t}")

    insights = analysis.get("key_insights", [])
    if insights:
        print(f"\n💡 Ключевые инсайты:")
        for ins in insights:
            print(f"   • {ins}")

    print(f"\n👥 Аудитория:\n   {analysis.get('audience_profile', 'N/A')}")

    recs = analysis.get("recommendations", [])
    if recs:
        print(f"\n🎯 Рекомендации:")
        for r in recs:
            print(f"   → {r}")

    notable = analysis.get("notable_comments", [])
    if notable:
        print(f"\n⭐ Примечательные комментарии:")
        for nc in notable[:3]:
            print(f"   @{nc.get('author')}: \"{nc.get('text', '')[:80]}...\"")
            print(f"   └─ {nc.get('reason', '')}")

    print(f"\n{sep}\n")


def save_results(comments: list[dict], analysis: dict, video_id: str, output_dir: str = "output"):
    """Сохраняет комментарии и анализ в JSON-файлы."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    comments_file = os.path.join(output_dir, f"{video_id}_comments_{timestamp}.json")
    analysis_file = os.path.join(output_dir, f"{video_id}_analysis_{timestamp}.json")

    with open(comments_file, "w", encoding="utf-8") as f:
        json.dump(comments, f, ensure_ascii=False, indent=2)

    with open(analysis_file, "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)

    print(f"💾 Комментарии → {comments_file}")
    print(f"💾 Анализ      → {analysis_file}")


# ─────────────────────────────────────────────
# CLI Entry Point
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Анализ YouTube-комментариев через Claude AI"
    )
    parser.add_argument(
        "video",
        help="URL или ID YouTube-видео",
    )
    parser.add_argument(
        "-n", "--max-comments",
        type=int,
        default=100,
        help="Максимальное количество комментариев (по умолчанию: 100)",
    )
    parser.add_argument(
        "--model",
        default="claude-opus-4-6",
        help="Claude-модель (по умолчанию: claude-opus-4-6)",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Сохранить результаты в папку output/",
    )
    args = parser.parse_args()

    video_id = get_video_id(args.video)
    comments = fetch_comments(video_id, max_comments=args.max_comments)
    analysis = analyze_with_claude(comments, model=args.model)
    print_report(analysis, video_id)

    if args.save:
        save_results(comments, analysis, video_id)


if __name__ == "__main__":
    main()
