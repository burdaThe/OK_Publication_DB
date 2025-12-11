using System;
using System.Collections.Generic;
using System.Xml.Linq;
using Microsoft.Data.Sqlite;
using Newtonsoft.Json;
using static System.Net.Mime.MediaTypeNames;
using static System.Runtime.InteropServices.JavaScript.JSType;

namespace json_to_sql
{
    public class JsonToSqliteImporter
    {
        private readonly string _connectionString;
        // Путь сохранения/открытия выходного БД-файла
        public JsonToSqliteImporter(string databasePath = "..\\..\\..\\..\\db_output\\posts.db")
        {
            _connectionString = $"Data Source={databasePath}";
            InitializeDatabase();
        }

        // Инициализация/создание БД(если не существует)
        private void InitializeDatabase()
        {
            using var connection = new SqliteConnection(_connectionString);
            connection.Open();

            var createTableCommand = connection.CreateCommand();
            createTableCommand.CommandText = @"
            CREATE TABLE IF NOT EXISTS keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT UNIQUE,
                posts_num INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS authors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword_id INTEGER,
                author_id INTEGER,
                text TEXT,
                published_at TEXT,
                url TEXT UNIQUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT posts_authors_fk
                FOREIGN KEY (author_id) REFERENCES authors (id) ON DELETE CASCADE,
                CONSTRAINT posts_keywords_fk
                FOREIGN KEY (keyword_id) REFERENCES keywords (id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER UNIQUE,
                likes_num INTEGER DEFAULT 0,
                shares_num INTEGER DEFAULT 0,
                comms_num INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT statistics_posts_fk
                FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE
            );
            
            CREATE INDEX IF NOT EXISTS idx_keyword ON keywords(keyword);
            CREATE INDEX IF NOT EXISTS idx_author ON authors(name);
            CREATE INDEX IF NOT EXISTS idx_date ON posts(published_at);
        ";

            createTableCommand.ExecuteNonQuery();
            Console.WriteLine("База данных инициализирована успешно!");
        }

        // Десериализация постов из JSON в массив posts
        public bool ImportFromJsonFile(string jsonFilePath)
        {
            if (!File.Exists(jsonFilePath))
            {
                Console.WriteLine($"Файл {jsonFilePath} не найден");
                return false;
            }

            try
            {
                var jsonContent = File.ReadAllText(jsonFilePath);
                var posts = JsonConvert.DeserializeObject<List<SocialMediaPost>>(jsonContent);

                if (posts == null || !posts.Any())
                {
                    Console.WriteLine("JSON файл не содержит данных или имеет неверный формат");
                    return false;
                }

                return InsertPosts(posts);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Ошибка при чтении JSON файла: {ex.Message}");
                return false;
            }
        }

        // Открытие БД и вставка постов через метод InsertPost + кэч дубликатов/ошибок
        private bool InsertPosts(List<SocialMediaPost> posts)
        {
            using var connection = new SqliteConnection(_connectionString);
            connection.Open();

            var successCount = 0;
            var errorCount = 0;

            using var transaction = connection.BeginTransaction();

            try
            {
                foreach (var post in posts)
                {
                    try
                    {
                        InsertPost(connection, post);
                        successCount++;
                    }
                    catch (SqliteException ex) when (ex.SqliteErrorCode == 19) // ошибка уникальности объекта
                    {
                        // Дубликат проверяется по ссылке - пропускаем
                        Console.WriteLine($"Дубликат поста {post.link}, пропускаем...");
                        errorCount++;
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"Ошибка при вставке поста {post.link}: {ex.Message}");
                        errorCount++;
                    }
                }

                transaction.Commit();

                Console.WriteLine($"Обработано постов: {posts.Count}");
                Console.WriteLine($"Успешно: {successCount}");
                Console.WriteLine($"Ошибок/дубликатов: {errorCount}");

                return successCount > 0;
            }
            catch (Exception ex)
            {
                transaction.Rollback();
                Console.WriteLine($"Транзакция отменена: {ex.Message}");
                return false;
            }
        }
        
        // Метод вставки поста в БД
        private void InsertPost(SqliteConnection connection, SocialMediaPost post)
        {
            var keywordsCommand = connection.CreateCommand();
            keywordsCommand.CommandText = @"
            INSERT OR IGNORE INTO keywords (keyword, posts_num) VALUES ($keyword, 0);
            UPDATE keywords 
            SET posts_num = (
            SELECT COUNT(*) FROM posts 
            WHERE keyword_id = keywords.id
            )
            WHERE keyword = $keyword;
            ";
            keywordsCommand.Parameters.AddWithValue("$keyword", post.keyword);
            keywordsCommand.ExecuteNonQuery();

            var authorsCommand = connection.CreateCommand();
            authorsCommand.CommandText = @"
            INSERT OR IGNORE INTO authors(name) VALUES ($name);
            ";
            authorsCommand.Parameters.AddWithValue("$name", post.group_name ?? (object)DBNull.Value);
            authorsCommand.ExecuteNonQuery();

            var postsCommand = connection.CreateCommand();
            postsCommand.CommandText = @"
            INSERT INTO 
            posts(keyword_id, author_id, text, published_at, url) VALUES (
            (SELECT id FROM keywords WHERE keyword = $keyword),
            (SELECT id FROM authors WHERE name = $name),
            $text, $date, $link);
            SELECT last_insert_rowid();
            ";
            postsCommand.Parameters.AddWithValue("$keyword", post.keyword);
            postsCommand.Parameters.AddWithValue("$name", post.group_name ?? (object)DBNull.Value);
            postsCommand.Parameters.AddWithValue("$text", post.text ?? (object)DBNull.Value);
            postsCommand.Parameters.AddWithValue("$date", post.date ?? (object)DBNull.Value);
            postsCommand.Parameters.AddWithValue("$link", post.link ?? (object)DBNull.Value);

            var postId = Convert.ToInt64(postsCommand.ExecuteScalar());

            var statisticsCommand = connection.CreateCommand();
            statisticsCommand.CommandText = @"
            INSERT INTO statistics
            (post_id, likes_num, shares_num, comms_num) VALUES ($post_id, $likes_num, $shares_num, $comms_num);
            ";
            statisticsCommand.Parameters.AddWithValue("$post_id", postId);
            statisticsCommand.Parameters.AddWithValue("$comms_num", post.num_comments);
            statisticsCommand.Parameters.AddWithValue("$likes_num", post.num_likes);
            statisticsCommand.Parameters.AddWithValue("$shares_num", post.num_shared);
            statisticsCommand.ExecuteNonQuery();

            var updateCommand = connection.CreateCommand();
            updateCommand.CommandText = @"
            UPDATE keywords 
            SET posts_num = (
            SELECT COUNT(*) FROM posts 
            WHERE keyword_id = keywords.id
            )
            WHERE keyword = $keyword;
            ";
            updateCommand.Parameters.AddWithValue("$keyword", post.keyword);
            updateCommand.ExecuteNonQuery();
        }
    }
}
