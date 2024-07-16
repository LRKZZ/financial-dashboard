# Автоматизированная визуализация финансовых данных в реальном времени
Добро пожаловать в репозиторий нашего совместного проекта с "Lapamore" под названием "Автоматизированная визуализация финансовых данных в реальном времени". Этот проект представляет собой дашборд для мониторинга и анализа финансовых данных, обеспечивая удобный и интуитивно понятный интерфейс для визуализации ключевых показателей в режиме реального времени.

Мы рады поделиться результатами нашей работы и надеемся, что наш проект будет полезен и интересен сообществу!

## Использование
### Установка WSL
Прежде всего, вам нужно установить Windows Subsystem for Linux (WSL) на свой компьютер, так как наша разработка работает на базе Linux. WSL позволяет запускать среду Linux на компьютере Windows без необходимости отдельной виртуальной машины или двойной загрузки. Если вашей ОС является Linux, пропустите этот этап.
1. Откройте PowerShell с правами администратора
2. Выведите в запущенной консоли список доступных дистрибутивов командой `wsl --list --online`
3. Установите WSL c нужным дистрибутивом, выполнив команду `wsl --install -d name`, где name – название дистрибутива.
Эта команда установит WSL и автоматически установит дистрибутив Ubuntu.

### Настройка WSL
Запустите WSL. Обновите пакетный менеджер и установите обновления:
```bash
sudo apt update && sudo apt upgrade -y
```

### Настройка git
Первое, что вам следует сделать — указать ваше имя и адрес электронной почты. Это важно, потому что каждый коммит в Git содержит эту информацию, и она включена в коммиты, передаваемые вами, и не может быть далее изменена:
```bash
$ git config --global user.name "John Doe"
$ git config --global user.email johndoe@example.com
```

### Установка Redis
1. Откройте терминал WSL (Ubuntu) и выполните команды:
```bash
sudo apt update
sudo apt install redis-server -y
```

2. Настройка Redis для автозапуска
Откройте файл конфигурации Redis:
```
sudo nano /etc/redis/redis.conf
```

Найдите строку `supervised no` и замените `no` на `systemd`:
```ini
supervised systemd
```
Сохраните изменения и закройте редактор (`Ctrl + O`, `Enter`, `Ctrl + X`).

3. Запуск и проверка Redis
   
Запустите Redis:
```bash
sudo service redis-server start
```

Проверьте статус Redis:
```bash
sudo service redis-server status
```

Проверьте работу Redis, подключившись к нему:
```bash
redis-cli
```

Внутри Redis CLI выполните команду `ping` и убедитесь, что возвращается `PONG`:
```bash
127.0.0.1:6379> ping
PONG
```

### Установка PostgreSQL
1. Обновите список пакетов и установите PostgreSQL
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib -y
```

2. Запуск PostgreSQL
```bash
sudo service postgresql start
```

3. Создание базы данных и нужных таблиц
Войдите в `psql`
```bash
sudo -u postgres psql
```

Создайте базу данных
```sql
CREATE DATABASE financial_db;
```

Создайте табилцу с наименованием `figi_numbers`
```sql
CREATE TABLE figi_numbers (
    figi_id SERIAL PRIMARY KEY,
    figi_number VARCHAR(50) NOT NULL,
    company_name VARCHAR(50)
);
```

Создайте четыре таблицы с названиями `candles`, `candles_5_min`, `candles_10_min`, `candles_60_min`
```sql
CREATE TABLE candles (
    candles_id SERIAL PRIMARY KEY,
    time_of_candle TIMESTAMP WITH TIME ZONE NOT NULL,
    open_price NUMERIC(10, 5),
    low_price NUMERIC(10, 5),
    high_price NUMERIC(10, 5),
    close_price NUMERIC(10, 5),
    volume INTEGER,
    figi_id SMALLINT REFERENCES figi_numbers(figi_id)
);
```

