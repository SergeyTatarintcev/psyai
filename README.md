# 🧠 PsyAI — онлайн-консультант с искусственным интеллектом

**PsyAI** — это веб-платформа для поддержки пользователей через чат с ИИ-психологом.  
Проект создан как дипломная работа в рамках курса **Zerocoder: Python from Scratch**.  
Используется стек **Django + DRF + HTML/JS (vanilla)**.

---

## 🚀 Возможности

- 💬 **Один бесплатный вопрос** без регистрации  
  (гостевой режим с лимитом 3 сообщений)
- 👤 **Регистрация и вход по email + пароль**
- 🔑 **Авторизация через DRF Token**
- 💡 **Личный кабинет с тарифом**  
  (10 бесплатных сообщений или безлимит при оплате)
- 🤖 **Интеграция с OpenAI API** — естественные ответы ИИ-консультанта  
- 🧩 **Сохранение истории чатов**
- 💸 **Имитация оплаты (заглушка)**  
  можно расширить под реальные платёжные шлюзы

---

## ⚙️ Технологии

- **Backend:** Django 5, Django REST Framework  
- **Frontend:** нативный HTML, CSS, JavaScript  
- **AI:** OpenAI Responses API (через client.responses.create)  
- **Auth:** Django `User` + DRF `TokenAuthentication`  
- **DB:** SQLite  
- **Deploy:** любой VPS с Gunicorn + Nginx  

---

## 📦 Установка и запуск локально

```bash
# 1. Клонируем репозиторий
git clone https://github.com/SergeyTatarintcev/psyai.git
cd psyai

# 2. Создаём виртуальное окружение
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
# source .venv/bin/activate

# 3. Устанавливаем зависимости
pip install -r requirements.txt

# 4. Применяем миграции
python manage.py migrate

# 5. Запускаем сервер
python manage.py runserver
```

Сайт откроется на http://127.0.0.1:8000

---

## 🧠 OpenAI API

Для работы ответов ИИ необходимо задать токен OpenAI в `.env`:

```
OPENAI_API_KEY=sk-xxxx...
```

---

## 📸 Скриншоты

- Главная страница — бесплатный вопрос, тарифы, блок доверия 
[Главная страница] (.\screenshots\2025-10-29_15-11-13.png) 
- Регистрация / Авторизация — вход и регистрация с токеном  
[Регистрация] (.\screenshots\2025-10-29_15-11-23.png)
- Чат с консультантом — история сообщений, лимиты тарифов
[Чат] (.\screenshots\2025-10-29_15-11-28.png)

---

## 🧩 Структура проекта

```
psyai/
├── accounts/     # регистрация, вход, тарифы
├── chat/         # диалоги, сообщения, логика ИИ
├── config/       # маршруты, настройки, free-question API
├── templates/
│   └── home.html # фронтенд с UI
└── manage.py
```

---

## 📄 Лицензия

Этот проект предназначен для учебных целей (курсовая/диплом). Используйте как пример и основу для своих проектов.

---

## 💬 Автор

Сделано [SergeyTatarintcev](https://github.com/SergeyTatarintcev) ❤️
