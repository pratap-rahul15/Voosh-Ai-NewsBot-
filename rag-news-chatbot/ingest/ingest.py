import requests
from bs4 import BeautifulSoup
import os
import json
from urllib.parse import urljoin, urlparse, urlunparse

NEWS_URLS = [
    "https://www.bbc.com/news",
    "https://timesofindia.indiatimes.com/news",
    "https://indianexpress.com/section/india/",
    "https://www.hindustantimes.com/india-news",
    "https://www.livemint.com/latest-news"
]

OUTPUT_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Total articles to fetch
TARGET_ARTICLE_COUNT = 50 


def clean_url(url):
    """Remove query params/fragments (TOI/NDTV style)."""
    parsed = urlparse(url)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", "", ""))


def fetch_articles(url, seen, collected, target_count):
    """Fetch article links and content from a news page."""
    articles = []
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        links = [a["href"] for a in soup.find_all("a", href=True)]

        for link in links:
            if len(collected) + len(articles) >= target_count:
                break

            link = urljoin(url, link)
            link = clean_url(link)

            if not link.startswith("http"):
                continue
            if any(x in link for x in ["#","video","liveblog","photos","sports","cricket"]):
                continue
            if link in seen:
                continue
            seen.add(link)

            try:
                art_res = requests.get(link, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                art_res.raise_for_status()
                art_soup = BeautifulSoup(art_res.text, "html.parser")

                title = art_soup.find("h1").get_text(strip=True) if art_soup.find("h1") else "Untitled"
                paragraphs = [p.get_text(strip=True) for p in art_soup.find_all("p")]
                content = " ".join(paragraphs)

                if len(content) > 200:  # filter junk
                    articles.append({"title": title, "url": link, "content": content})

            except Exception as e:
                print(f"⚠️ Failed to fetch article {link}: {e}")
                continue

    except Exception as e:
        print(f" Failed to fetch page {url}: {e}")

    return articles


def main():
    all_articles = []
    seen = set()

    for site in NEWS_URLS:
        if len(all_articles) >= TARGET_ARTICLE_COUNT:
            break

        print(f" Scraping {site} ...")
        site_articles = fetch_articles(site, seen, all_articles, TARGET_ARTICLE_COUNT)
        all_articles.extend(site_articles)
        print(f" Collected {len(all_articles)} so far")

    output_path = os.path.join(OUTPUT_DIR, "articles.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_articles, f, indent=2, ensure_ascii=False)

    print(f"\n Done! Saved {len(all_articles)} articles to {output_path}")


if __name__ == "__main__":
    main()
