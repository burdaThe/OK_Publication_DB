using System;
using System.Collections.Generic;

namespace json_to_sql
{
    //модель данных
    public class SocialMediaPost
    {
        public string Keyword { get; set; } = "чай";
        public string Group_name { get; set; }
        public string Text { get; set; }
        public int Num_likes { get; set; }
        public int Num_shared { get; set; }
        public int Num_comments { get; set; }
        public string Date { get; set; }
        public string Link { get; set; }
        public DateTime CreatedAt { get; set; } = DateTime.Now;
    }
}

