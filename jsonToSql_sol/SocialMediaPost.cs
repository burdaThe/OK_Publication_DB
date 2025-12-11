using System;
using System.Collections.Generic;

namespace json_to_sql
{
    // данные выводимые из JSON
    public class SocialMediaPost
    {
        public string keyword { get; set; }
        public string group_name { get; set; }
        public string text { get; set; }
        public int num_likes { get; set; }
        public int num_shared { get; set; }
        public int num_comments { get; set; }
        public string date { get; set; }
        public string link { get; set; }
        public DateTime createdAt { get; set; } = DateTime.Now;
    }
}

