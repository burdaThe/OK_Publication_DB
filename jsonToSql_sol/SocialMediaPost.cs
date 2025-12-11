using System;
using System.Collections.Generic;

namespace json_to_sql
{
    // данные выводимые из JSON
    public class SocialMediaPost
    {
        public string keyword { get; set; }
        public string name { get; set; }
        public string text { get; set; }
        public int numLikes { get; set; }
        public int numShared { get; set; }
        public int numComments { get; set; }
        public string date { get; set; }
        public string link { get; set; }
        public DateTime createdAt { get; set; } = DateTime.Now;
    }
}

