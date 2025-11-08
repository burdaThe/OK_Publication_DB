using json_to_sql;

class Program
{
    static void Main(string[] args)
    { 
        // Импорт данных из JSON в SQLite
        var importer = new JsonToSqliteImporter();
        importer.ImportFromJsonFile("C:\\Users\\srvow\\source\\repos\\OK_Publication_DB\\JSONS\\Test.json");
    }

}