<p align="center"><img src="static/img/logo.PNG" width="100" height="100" /></p>

# **<p align="center">SmartFridge: QR Control & IoT Sync»</p>**

[![Demo Video](https://img.shields.io/badge/🎥-Watch%20Demo-red)](https://example.com/demo-video)

### 🌟 Умный контроль запасов
**SmartFridge** — это революционная система для автоматизации учета продуктов в холодильниках. Проект сочетает в себе:
- 🧺 **Интеллектуальный инвентаризатор**  
  Автоматический трекинг содержимого через QR-сканирование
- 📊 **Аналитика потребления**  
  Визуализация статистики использования продуктов
- 🛒 **Генерация списка покупок**  
  Удобное управление списком продуктов
- 🔔 **Упреждающие уведомления**  
  Оповещения об истечении срока годности

**Для кого:**  
✅ Владельцы кафе и ресторанов  
✅ Семейные хозяйства  
✅ Коммуны в студенческих общежитиях  

---

## 🚀 Установка и развертывание

### 📋 Требования
- Python 3.10+
- SQLite3
- Пакеты из `requirements.txt`:
  

### ⚙️ Пошаговая инструкция

1. **Клонирование репозитория**:
 ```bash
 git clone https://github.com/yourusername/smartfridge.git
 cd smartfridge
 ```
2. **Установка зависимостей**
 ```bash
 pip install --upgrade pip
 pip install -r requirements.txt
 ```
3. **Запуск сайта**
 ```bash
 flask run --host=0.0.0.0 --port=5000
 ```