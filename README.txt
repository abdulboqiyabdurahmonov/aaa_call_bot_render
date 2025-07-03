# aaa_call_bot

Бот для приёма заявок на обратную связь через Telegram.

## Что нужно:
1. Установи зависимости:
   pip install python-telegram-bot gspread oauth2client python-dotenv

2. Добавь `google_credentials.json` (ключ от Google Service Account)

3. В файле `.env` укажи:
- BOT_TOKEN=... (токен от BotFather)
- OWNER_ID=... (свой Telegram ID)

4. Создай Google Таблицу с именем "TRIPLEA Заявки" и такими колонками:
Дата | Имя | Телефон | Email | Язык | Комментарий

5. Запусти `python main.py`

По умолчанию все заявки дублируются в Telegram владельцу и в Google Sheets.
