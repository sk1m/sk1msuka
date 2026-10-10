"""Сравнение телефонов через Claude API."""
import logging

import anthropic

MODEL = "claude-opus-5-5"

SYSTEM = """Ты — эксперт по смартфонам в Telegram-боте. Помогаешь сравнивать модели телефонов и выбирать.

Как отвечать:
- Пиши по-русски, простым языком.
- Сравнивай по главным характеристикам: процессор, экран, камеры, батарея и зарядка, память, вес и размеры, защита, цена на старте.
- Для каждой характеристики коротко скажи, у кого лучше, и почему это важно в жизни.
- В конце дай вывод: кому какой телефон подойдёт.
- Если характеристики свежей модели не уверен — найди их через поиск. Если точных данных нет, так и скажи, не выдумывай цифры.
- Если вопрос не про телефоны и гаджеты, вежливо скажи, что бот помогает только с выбором и сравнением телефонов.

Формат: обычный текст для Telegram. Без Markdown-таблиц, без **звёздочек** и # заголовков. Можно эмодзи и списки через «•».
Длина: до 3000 символов."""

# Поиск в интернете, чтобы брать актуальные характеристики новых моделей
TOOLS = [{"type": "web_search_20260209", "name": "web_search", "max_uses": 3}]

log = logging.getLogger(__name__)


class PhoneAI:
    def __init__(self):
        self.client = anthropic.AsyncAnthropic()  # ключ из ANTHROPIC_API_KEY

    async def answer(self, history: list[dict]) -> str:
        """history — список сообщений [{'role': 'user'|'assistant', 'content': str}, ...]."""
        messages = list(history)
        try:
            for _ in range(4):  # pause_turn: серверный поиск может попросить продолжить
                resp = await self.client.beta.messages.create(
                    model=MODEL,
                    max_tokens=16000,
                    system=SYSTEM,
                    messages=messages,
                    tools=TOOLS,
                    thinking={"type": "adaptive"},
                    output_config={"effort": "medium"},
                    # если модель откажет по правилам безопасности, сервер повторит запрос на другой модели
                    betas=["server-side-fallback-2026-07-01"],
                    fallbacks="default",
                )
                if resp.stop_reason != "pause_turn":
                    break
                messages = messages + [{"role": "assistant", "content": resp.content}]
        except anthropic.RateLimitError:
            return "⏳ Слишком много запросов. Попробуй через минуту."
        except anthropic.APIStatusError as e:
            log.error("Claude API error %s: %s", e.status_code, e.message)
            return "⚠️ AI сейчас недоступен. Попробуй чуть позже."
        except anthropic.APIConnectionError:
            log.exception("Claude API connection error")
            return "⚠️ Нет связи с AI. Попробуй чуть позже."

        if resp.stop_reason == "refusal":
            return "Не могу ответить на этот вопрос. Спроси про сравнение телефонов 📱"
        text = "".join(b.text for b in resp.content if b.type == "text").strip()
        return text or "Не получилось сформировать ответ. Попробуй переформулировать вопрос."
