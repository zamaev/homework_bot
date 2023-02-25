# Telegram YPHSNBot 
YPHSNBot (Yandex Practicum Homework Status Notification Bot) - бот для уведомлений об изменении статуса проверки домашних работ в Яндекс Практикум.

## Требования
- Python (3.7+)

Пакеты:
- python-dotenv (0.19.0+)
- python-telegram-bot (13.7)
- requests (2.26.0+)

## Установка
Скачайте проект
```bash
git clone git@github.com:zamaev/homework_bot.git
```
Установите и активируйте виртуальное окружение
```bash
cd homework_bot
python3.7 -m venv venv
. venv/bin/activate
```
Установите необходимые зависимости
```bash
pip install -r requirements.txt
```
Установите переменные окружения в файле `.env`
```bash
cp .env.example .env
```
Запустите бота
```bash
python homework.py
```

## Авторы
- [Айдрус](https://github.com/zamaev)