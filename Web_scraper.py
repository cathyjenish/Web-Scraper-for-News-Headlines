import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import re
import sys
import argparse

def scrape_news_headlines(url="https://www.bbc.com/news", output_file=None):
    """
    Scrape news headlines from a news website and save to a text file
    
    Args:
        url (str): URL of the news website to scrape
        output_file (str): Name of the output file to save headlines
    
    Returns:
        list: List of scraped headlines
    """
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"headlines_{timestamp}.txt"
    
    print(f"🌐 Scraping headlines from: {url}")
    
    try:
        # Add headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Fetch HTML
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        if response.status_code != 200:
            print(f"❌ Failed to retrieve the web page. Status code: {response.status_code}")
            return []
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract headlines
        headlines = []
        
        # Common patterns for news headlines
        headline_selectors = [
            'h1', 'h2', 'h3',  # Standard heading tags
            '.headline', '.title',  # Common classes
            '[data-testid*="headline"]',  # BBC specific
            '.gs-c-promo-heading__title',  # BBC specific
            '.media__title',  # BBC specific
            'a[data-testid="internal-link"] h3',  # BBC specific
        ]
        
        # Try different selectors to find headlines
        for selector in headline_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                # Filter out short or irrelevant text
                if text and len(text) > 15 and text not in headlines:
                    # Remove common navigation/footer text
                    if not any(skip in text.lower() for skip in ['more', 'follow', 'watch', 'also in', 'most watched', 'bbc']):
                        headlines.append(text)
        
        # Also try to find headlines in anchor tags with specific patterns
        links = soup.find_all('a', href=True)
        for link in links:
            text = link.get_text(strip=True)
            if text and len(text) > 20 and text not in headlines:
                # Check if it looks like a headline
                if re.search(r'[A-Z][a-z].*[a-z]', text) and len(text.split()) > 3:
                    headlines.append(text)
        
        # Remove duplicates and limit to top headlines
        headlines = list(dict.fromkeys(headlines))[:50]  # Get top 50 unique headlines
        
        if not headlines:
            print("⚠️  No headlines found. The website structure might have changed.")
            return []
        
        # Save to .txt file
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(f"News Headlines Scraped from {url}\n")
            file.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            file.write("=" * 80 + "\n\n")
            
            for i, headline in enumerate(headlines, start=1):
                file.write(f"{i}. {headline}\n")
        
        print(f"✅ Successfully saved {len(headlines)} headlines to '{output_file}'")
        return headlines
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return []
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        return []

def main():
    """Main function to handle command line arguments and run the scraper"""
    parser = argparse.ArgumentParser(description='Scrape news headlines from websites')
    parser.add_argument('--url', '-u', default='https://www.bbc.com/news',
                        help='URL of the news website to scrape (default: BBC News)')
    parser.add_argument('--output', '-o', help='Output file name (default: headlines_TIMESTAMP.txt)')
    
    args = parser.parse_args()
    
    print("📰 News Headlines Web Scraper")
    print("=" * 40)
    
    # Scrape headlines
    headlines = scrape_news_headlines(args.url, args.output)
    
    if headlines:
        print("\n📋 Top Headlines:")
        print("-" * 40)
        for i, headline in enumerate(headlines[:10], 1):
            print(f"{i}. {headline}")
        
        print(f"\n💾 Full list saved to: {args.output or 'headlines_TIMESTAMP.txt'}")
    else:
        print("❌ No headlines were scraped.")

if __name__ == "__main__":
    main()
