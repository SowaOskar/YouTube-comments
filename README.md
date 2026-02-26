# 🎬 YouTube Comments Analyzer

Инструмент для парсинга комментариев YouTube и их интеллектуального анализа через **Claude AI** (Anthropic).

## ✨ Что делает

1. **Парсит** комментарии к любому YouTube-видео через официальный YouTube Data API v3
2. **Передаёт** их в Claude для глубокого анализа
3. **Выдаёт** структурированный отчёт с тональностью, ключевыми темами, инсайтами и рекомендациями

## 📋 Пример вывода

```
────────────────────────────────────────────────────────────
  📊 АНАЛИЗ КОММЕНТАРИЕВ  |  video: dQw4w9WgXcQ
────────────────────────────────────────────────────────────

📝 Резюме:
   Аудитория преимущественно ностальгирует и выражает любовь к треку.

🎭 Тональность: POSITIVE
   👍 Позитив: 78%  😐 Нейтрал: 15%  👎 Негатив: 7%

🏷️  Топ темы:
   • Ностальгия и детские воспоминания
   • Юмор и мемы
   • Восхищение артистом

💡 Ключевые инсайты:
   • Большинство зрителей попали сюда намеренно (не рикроллинг)
   • Высокая эмоциональная вовлечённость
   • Много комментариев на разных языках — глобальная аудитория
```

## 🚀 Быстрый старт

### 1. Клонировать репозиторий

```bash
git clone https://github.com/YOUR_USERNAME/youtube-comments-analyzer.git
cd youtube-comments-analyzer
```

### 2. Установить зависимости

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Настроить API-ключи

```bash
cp .env.example .env
# Открой .env и вставь свои ключи
```

Тебе понадобятся:
- **YouTube Data API v3** → [Google Cloud Console](https://console.cloud.google.com) → APIs & Services → Enable API → YouTube Data API v3 → Create Credentials
- **Anthropic API** → [console.anthropic.com](https://console.anthropic.com)

### 4. Запустить

```bash
# Базовый запуск (URL видео)
python analyzer.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# С сохранением результатов
python analyzer.py "https://youtu.be/dQw4w9WgXcQ" --save

# Указать количество комментариев и модель
python analyzer.py dQw4w9WgXcQ -n 200 --model claude-sonnet-4-6 --save
```

## ⚙️ Параметры CLI

| Параметр | Описание | По умолчанию |
|---|---|---|
| `video` | URL или ID видео | — (обязательный) |
| `-n / --max-comments` | Макс. количество комментариев | 100 |
| `--model` | Claude модель | `claude-opus-4-6` |
| `--save` | Сохранить JSON в `output/` | выключено |

## 📁 Структура проекта

```
youtube-comments-analyzer/
├── analyzer.py          # Основной скрипт
├── requirements.txt     # Зависимости
├── .env.example         # Шаблон переменных окружения
├── .env                 # Твои ключи (не коммитить!)
├── .gitignore
├── output/              # Результаты анализа (создаётся автоматически)
│   ├── VIDEO_ID_comments_TIMESTAMP.json
│   └── VIDEO_ID_analysis_TIMESTAMP.json
└── README.md
```

## 🔍 Структура JSON-анализа

```json
{
  "summary": "Краткое резюме обсуждения",
  "overall_sentiment": "positive | negative | neutral | mixed",
  "sentiment_breakdown": {
    "positive_pct": 78,
    "neutral_pct": 15,
    "negative_pct": 7
  },
  "top_topics": ["Ностальгия", "Мемы", "..."],
  "key_insights": ["Инсайт 1", "Инсайт 2"],
  "audience_profile": "Описание аудитории",
  "recommendations": ["Рекомендация для автора"],
  "notable_comments": [
    {"author": "User", "text": "...", "reason": "Почему выделен"}
  ]
}
```

## 📝 Лицензия

MIT — используй свободно.
