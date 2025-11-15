using Microsoft.Data.Sqlite;
using Newtonsoft.Json;

namespace json_to_sql
{
    public class JsonToSqliteImporter
    {
        private readonly string _connectionString;

        public JsonToSqliteImporter(string databasePath = "C:\\Users\\srvow\\source\\repos\\OK_Publication_DB\\SQL\\DBs\\posts.db")
        {
            _connectionString = $"Data Source={databasePath}";
            InitializeDatabase();
        }

        private void InitializeDatabase()
        {
            using var connection = new SqliteConnection(_connectionString);
            connection.Open();

            var createTableCommand = connection.CreateCommand();
            createTableCommand.CommandText = @"
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT,
                group_name TEXT,
                text TEXT,
                num_likes INTEGER DEFAULT 0,
                num_shared INTEGER DEFAULT 0,
                num_comments INTEGER DEFAULT 0,
                date TEXT,
                link TEXT,
                createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_keyword ON posts(keyword);
            CREATE INDEX IF NOT EXISTS idx_date ON posts(date);
        ";

            createTableCommand.ExecuteNonQuery();
            Console.WriteLine("База данных инициализирована успешно!");
        }

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
                    catch (SqliteException ex) when (ex.SqliteErrorCode == 19) // повтор
                    {
                        // Дубликат post_id - пропускаем или обновляем
                        Console.WriteLine($"Дубликат поста {post.Link}, пропускаем...");
                        errorCount++;
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"Ошибка при вставке поста {post.Link}: {ex.Message}");
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

        private void InsertPost(SqliteConnection connection, SocialMediaPost post)
        {
            var command = connection.CreateCommand();
            command.CommandText = @"
            INSERT OR IGNORE INTO posts 
            (keyword, group_name, text, num_likes, num_shared, num_comments, date, link)
            VALUES ($keyword, $group_name, $text, $num_likes, $num_shared, $num_comments, $date, $link)
        ";

            // Добавляем параметры
            command.Parameters.AddWithValue("$keyword", post.Keyword);
            command.Parameters.AddWithValue("$group_name", post.Group_name ?? (object)DBNull.Value);
            command.Parameters.AddWithValue("$text", post.Text ?? (object)DBNull.Value);
            command.Parameters.AddWithValue("$num_likes", post.Num_likes);
            command.Parameters.AddWithValue("$num_shared", post.Num_shared);
            command.Parameters.AddWithValue("$num_comments", post.Num_comments);
            command.Parameters.AddWithValue("$date", post.Date ?? (object)DBNull.Value);
            command.Parameters.AddWithValue("$link", post.Link ?? (object)DBNull.Value);

            command.ExecuteNonQuery();
        }
    }
}
