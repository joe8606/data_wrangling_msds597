import requests
from bs4 import BeautifulSoup
import csv
import time
import random
import os
from urllib.parse import urljoin

# Set HTTP headers to simulate a real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

BASE_URL = "https://www.wayfair.com/keyword.php"
WAYFAIR_DOMAIN = "https://www.wayfair.com"

# Convert inline CSS width to a star rating (0 to 5)
def get_star_rating(star_element):
    try:
        width = star_element.get('style', '').split('width:')[1].split('%')[0]
        return round(float(width) / 20, 1)
    except Exception:
        return "N/A"

# Scrape product data across multiple result pages
def get_products(query="blender", max_pages=2):
    all_products = []
    current_page = 1

    while current_page <= max_pages:
        params = {'keyword': query, 'curpage': current_page}
        print(f"[INFO] Scraping listing page {current_page}...")
        response = requests.get(BASE_URL, headers=HEADERS, params=params)

        if response.status_code != 200:
            print(f"[ERROR] Failed to load page {current_page}, status code: {response.status_code}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')

        product_titles = soup.select('h2[data-test-id="ListingCard-ListingCardName-Text"]')
        prices = soup.select('span[data-test-id="PriceDisplay"]')
        reviews = soup.select('div[data-enzyme-id="ListingCard-ListingCardReviewStars-Reviews-reviewCount"]')
        star_elements = soup.select('div[data-enzyme-id="ListingCard-ListingCardReviewStars-Reviews-rating"]')

        if not product_titles:
            print(f"[INFO] No products found on page {current_page}.")
            break

        for i in range(len(product_titles)):
            title_elem = product_titles[i]
            title = title_elem.get_text(strip=True) if title_elem else "N/A"
            price = prices[i].get_text(strip=True) if i < len(prices) else "N/A"
            review = reviews[i].get_text(strip=True) if i < len(reviews) else "N/A"
            star_rating = get_star_rating(star_elements[i]) if i < len(star_elements) else "N/A"

            parent_link = title_elem.find_parent("a")
            product_url = urljoin(WAYFAIR_DOMAIN, parent_link["href"]) if parent_link and parent_link.has_attr("href") else "N/A"

            all_products.append({
                "title": title,
                "price": price,
                "reviews": review,
                "star_rating": star_rating,
                "url": product_url
            })

        current_page += 1
        time.sleep(random.uniform(1.5, 2.5))  # Avoid being blocked

    return all_products

# Save the scraped data to a CSV file inside /dat
def save_products(products, filename=r"C:\rutgers\Data Wrangling\data_wrangling_msds597\dat\wayfair_{}_bs4_products.csv".format(query)):
    folder = os.path.dirname(filename)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "price", "reviews", "star_rating", "url"])
        writer.writeheader()
        writer.writerows(products)
    print(f"[DONE] Saved {len(products)} products to {filename}")


# Main execution
if __name__ == "__main__":
    query = "sofa"  # Change to any keyword you want
    pages = 200         # Change number of pages to scrape
    products = get_products(query, pages)
    save_products(products)
