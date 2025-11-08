using System;
using System.Collections.Generic;

namespace json_to_sql
{
    //модель данных
    public class SocialMediaPost
    {
        public string PostId { get; set; }
        public string Keyword { get; set; } = "чай";
        public string Platform { get; set; }
        public string Content { get; set; }
        public string Author { get; set; }
        public string AuthorId { get; set; }
        public int Likes { get; set; }
        public int Shares { get; set; }
        public int Comments { get; set; }
        public int Views { get; set; }
        public string PostDate { get; set; }
        public string Url { get; set; }
        public List<string> Hashtags { get; set; } = new List<string>();
        public List<string> MediaUrls { get; set; } = new List<string>();
        public DateTime CreatedAt { get; set; } = DateTime.Now;
    }
}

