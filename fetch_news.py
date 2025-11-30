import os
import json
import requests
from datetime import datetime

# Configuration
API_KEY = os.environ.get('NEWS_API_KEY')
OUTPUT_FILE = 'data/daily_news.json'

def fetch_health_news():
    if not API_KEY:
        print("No API Key found. Generating static fallback data.")
        return generate_fallback_data()

    # Try fetching with query 'health' in Arabic first, then general health category
    # Adding User-Agent is crucial for some APIs
    headers = {'User-Agent': 'HealthApp/1.0'}
    
    # Strategy 1: Search for "صحة" (Health) in Arabic
    url = f"https://newsapi.org/v2/everything?q=صحة&language=ar&sortBy=publishedAt&apiKey={API_KEY}"
    
    try:
        print(f"Fetching news from: {url.replace(API_KEY, 'HIDDEN')}")
        response = requests.get(url, headers=headers)
        data = response.json()
        
        articles = []
        if data.get('status') == 'ok':
            articles = data.get('articles', [])
            print(f"Found {len(articles)} articles with query 'صحة'")
        else:
            print(f"API Error (Strategy 1): {data}")

        # Strategy 2: If no articles, try 'health' category in Arabic (Top Headlines)
        if not articles:
            print("Strategy 1 failed or empty. Trying Strategy 2 (Top Headlines - Health - AR)...")
            url2 = f"https://newsapi.org/v2/top-headlines?category=health&language=ar&apiKey={API_KEY}"
            response2 = requests.get(url2, headers=headers)
            data2 = response2.json()
            if data2.get('status') == 'ok':
                articles = data2.get('articles', [])
                print(f"Found {len(articles)} articles with Strategy 2")
            else:
                print(f"API Error (Strategy 2): {data2}")

        # Strategy 3: If still empty, try 'health' category in English (as last resort, but filtered)
        if not articles:
             print("Strategy 2 failed or empty. Trying Strategy 3 (Top Headlines - Health - EN)...")
             url3 = f"https://newsapi.org/v2/top-headlines?category=health&language=en&apiKey={API_KEY}"
             response3 = requests.get(url3, headers=headers)
             data3 = response3.json()
             if data3.get('status') == 'ok':
                 articles = data3.get('articles', [])
                 print(f"Found {len(articles)} articles with Strategy 3")

        if articles:
            # Filter out articles with no image or removed content
            valid_articles = [
                a for a in articles 
                if a.get('urlToImage') and a.get('title') and '[Removed]' not in a['title']
            ]
            
            return {
                "updated_at": datetime.now().isoformat(),
                "tip": "نصيحة اليوم: حافظ على نشاطك البدني وتناول غذاء متوازن.",
                "articles": valid_articles[:10] # Top 10 valid articles
            }
        else:
            print("All strategies failed to find articles.")
            return generate_fallback_data()
            
    except Exception as e:
        print(f"Error fetching news: {e}")
        return generate_fallback_data()

def generate_fallback_data():
    print("Using Fallback Data")
    return {
        "updated_at": datetime.now().isoformat(),
        "tip": "نصيحة اليوم: شرب الماء بانتظام يساعد على تحسين التركيز والطاقة.",
        "articles": [
            {
                "title": "فوائد الصيام المتقطع للصحة العقلية",
                "description": "دراسات جديدة تؤكد دور الصيام في تحسين الوظائف الإدراكية.",
                "url": "https://www.google.com/search?q=فوائد+الصيام+المتقطع",
                "urlToImage": "https://images.unsplash.com/photo-1544367563-12123d8965cd?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"
            },
            {
                "title": "أهمية النوم الجيد للمناعة",
                "description": "النوم لمدة 7-8 ساعات يعزز جهاز المناعة بشكل كبير.",
                "url": "https://www.google.com/search?q=أهمية+النوم",
                "urlToImage": "https://images.unsplash.com/photo-1511295742362-92c96b504802?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"
            }
        ]
    }

if __name__ == "__main__":
    news_data = fetch_health_news()
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2)
    
    print(f"Successfully updated {OUTPUT_FILE}")
