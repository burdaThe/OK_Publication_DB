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
                postId TEXT UNIQUE,
                keyword TEXT,
                platform TEXT,
                content TEXT,
                author TEXT,
                authorId TEXT,
                likes INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                views INTEGER DEFAULT 0,
                postDate TEXT,
                url TEXT,
                hashtags TEXT,
                mediaUrls TEXT,
                createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_keyword ON posts(keyword);
            CREATE INDEX IF NOT EXISTS idx_post_date ON posts(postDate);
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
                        Console.WriteLine($"Дубликат поста {post.PostId}, пропускаем...");
                        errorCount++;
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"Ошибка при вставке поста {post.PostId}: {ex.Message}");
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
            (postId, keyword, platform, content, author, authorId, 
             likes, shares, comments, views, postDate, url, hashtags, mediaUrls)
            VALUES ($postId, $keyword, $platform, $content, $author, $authorId, 
                    $likes, $shares, $comments, $views, $postDate, $url, $hashtags, $mediaUrls)
        ";

            // Добавляем параметры
            command.Parameters.AddWithValue("$postId", post.PostId ?? (object)DBNull.Value);
            command.Parameters.AddWithValue("$keyword", post.Keyword);
            command.Parameters.AddWithValue("$platform", post.Platform ?? (object)DBNull.Value);
            command.Parameters.AddWithValue("$content", post.Content ?? (object)DBNull.Value);
            command.Parameters.AddWithValue("$author", post.Author ?? (object)DBNull.Value);
            command.Parameters.AddWithValue("$authorId", post.AuthorId ?? (object)DBNull.Value);
            command.Parameters.AddWithValue("$likes", post.Likes);
            command.Parameters.AddWithValue("$shares", post.Shares);
            command.Parameters.AddWithValue("$comments", post.Comments);
            command.Parameters.AddWithValue("$views", post.Views);
            command.Parameters.AddWithValue("$postDate", post.PostDate ?? (object)DBNull.Value);
            command.Parameters.AddWithValue("$url", post.Url ?? (object)DBNull.Value);
            command.Parameters.AddWithValue("$hashtags", JsonConvert.SerializeObject(post.Hashtags));
            command.Parameters.AddWithValue("$mediaUrls", JsonConvert.SerializeObject(post.MediaUrls));

            command.ExecuteNonQuery();
        }
    }
}
