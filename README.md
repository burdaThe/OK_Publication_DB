# &nbsp;		  OK\_Publication\_DB

### ℹ️Краткое описание:

###### 
Университетское групповое задание **по сбору данных о публикациях** **в** социальной сети **OK.ru**. 

###### 
Выполнили: **Вадим Х. - BarbieKenn(Python)**, **Вадим Д. - MonforSalentaiel(Python)**, **Ренат С. - burdaThe(C#)**.

### Состоит из:

######
💻 **Парсер OK.ru** - сбор данных из социальной сети. Написано на **Python** (Использовано: **Playwright**, **Chromium**)

💾 **Импортер в SQLite** - сохранение данных в БД. Написано на **C#** (Использовано: **ADO.NET**, **Json.NET**)

---
### Функциональность:
---

###### 
🔍 **Поиск** постов по **ключевым словам**


###### 
📊 **Извлечение** **данных**: **текст**, **лайки**, **комментарии**, **репосты**, **дата**, **группа/имя пользователя**, **ссылка**


###### 
📂 Сохранение в **Json** и импорт **в** **SQLite**

###### 

⚡ **Кэч** **ошибок** и **логирование**
######

---
### 📅 ER-диаграмма БД:
---

<img width="1155" height="468" alt="ERD-model" src="https://github.com/user-attachments/assets/9fa4e0b0-437b-44a4-bc36-9b8323a01af0" />

---
### 🗒️Структура проекта
---

```
 OK_Publication_DB/
   ├── src/
   │   ├── auth.py
   │   ├── browser.py
   │   ├── parser.py
   │   ├── storage.py
   │   └── errors.py
   ├── json_to_sql/
   │   ├── SocialMediaPost.cs
   │   ├── JsonToSqliteImporter.cs
   │   ├── Program.cs     
   │   ├── json_t_sql.sln	# решение c#
   │   └── bin/
   │       └── Debug/
   │           └── net9.0/
   │               └── json_to_sql.exe # запуск конвертера
   ├── db_output/
   │   └── posts.db(*)
   ├── jsons_output/
   │   └── output.json(*)
   ├── main.py              # запуск парсера
   ├── config.py            # конфигурация парсера
   └── ok_cookies.json(*)

(*) - создаваемые/изменяемые файлы(их расположение тоже)
```
---
### ⚙️Использование:
---

#### 1. **Установка зависимостей**

##### &nbsp;	1. **Newtonsoft.Json**

##### &nbsp;	2. **Microsoft.Data.Sqlite**

##### &nbsp;	3. **Playwright**

##### &nbsp;	4. **Chromium**

#### 2. **Конфигурация**

##### &nbsp;	1. **В config.py задать путь выходного json-файла**
```py
output_path: str = 'jsons_output/output.json'
```
##### &nbsp;	2. **В main.py указать ключевое слово и количество постов**
```py
config = Config('ключевое_слово', количество постов, False)
```
##### &nbsp;	3. **В JsonToSqliteImporter.cs задать путь сохранения выходного db-файла**
```cs
public JsonToSqliteImporter(string databasePath = "..\\..\\..\\..\\db_output\\posts.db")
```
##### &nbsp;	4. **В Program.cs задать путь нахождения входного JSON-файла**
```cs
importer.ImportFromJsonFile("..\\..\\..\\..\\jsons_output\\output.json");
```
#### 3. **Запуск**

##### &nbsp;	1. **Запуск парсера через main.py**

#####  	2. **Открывается страница входа в аккаунт OK.ru**

#####  	3. **Необходимо залогиниться в свой аккаунт, дождаться полной загрузки ленты и только тогда закрыть браузер. Ждем выхода json-файла в jsons_output**

#####  	4. **Запуск импортера из json-файла в db-файл через jsonToSql_sol/bin/Debug/net9.0/json_to_sql.exe**

#####  	5. **Готово!**

#### 
---
### ⚖️**Лицензирование**

##### **Проект распространяется на условиях лицензии MIT**







