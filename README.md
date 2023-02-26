# Telegram YPHSNBot 
YPHSNBot (Yandex Practicum Homework Status Notification Bot) - бот для уведомлений об изменении статуса проверки домашних работ в Яндекс Практикум.

## Требования
- Python (3.7+)

Пакеты:
- python-dotenv (0.19.0+)
- python-telegram-bot (13.7)
- requests (2.26.0+)

## Установка
Клонировать репозиторий и перейти в него в командной строке:
```bash
git clone git@github.com:zamaev/homework_bot.git
cd homework_bot
```
Установите и активируйте виртуальное окружение:
```bash
python3 -m venv venv
source venv/bin/activate
```
Установить зависимости из файла requirements.txt:
```bash
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```
Задайте переменные окружения в файле `.env`:
```bash
cp .env.example .env
```
Запустите бота:
```bash
python homework.py
```

## Авторы
- [Айдрус](https://github.com/zamaev)