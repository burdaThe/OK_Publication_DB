using json_to_sql;

class Program
{
    static void Main(string[] args)
    { 
        // Импорт данных из JSON в SQLite
        var importer = new JsonToSqliteImporter();
	    // Путь нахождения входного JSON-файла
        importer.ImportFromJsonFile("\\jsonOutput\\output.json");
    }

}