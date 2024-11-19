from bs4 import BeautifulSoup
import os
import json
import requests
import pandas as pd
import matplotlib.pyplot as plt
import locale




articles_by_category = {
    "politique": [
        "https://fr.hespress.com/politique",
    ],
    "economie": [
        "https://fr.hespress.com/economie",  
    ],
    "sport": [
        "https://fr.hespress.com/sport",  
    ],
    "societe": [
        "https://fr.hespress.com/societe",  
    ],
    "monde": [
        "https://fr.hespress.com/monde",  
    ],
     "culture": [
        "https://fr.hespress.com/culture",  
    ],
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}





def scrap_comments(article_url):
    """
    Scrape comments for a given article URL.
    """
    print(f"Scraping comments from: {article_url}")
    response = requests.get(article_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch {article_url}. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    comments_list = soup.find("ul", class_="comment-list")
    if not comments_list:
        print(f"No comments found for {article_url}")
        return []

    comments = []
    for comment in comments_list.find_all("li", class_="comment"):
        try:
            author = comment.find("span", class_="fn").text.strip()
            date = comment.find("div", class_="comment-date").text.strip()
            text = comment.find("div", class_="comment-text").p.text.strip()
            comments.append({
                "author": author,
                "date": date,
                "text": text
            })
        except AttributeError:
            # Skip comments with missing data
            continue

    print(f"Scraped {len(comments)} comments from {article_url}")
    return comments

def scrap_articles_by_category(category):
    if category not in articles_by_category:
        print(f"Category '{category}' not found!")
        return

    # Initialize an empty list to store scraped data
    articles_data = []

    # Fetch the first URL from the category's list
    url = articles_by_category[category][0]
    print(f"Scraping articles from: {url}")

    # Make a GET request to the website
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch {url}. Status code: {response.status_code}")
        return

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all articles in the HTML structure
    articles = soup.find_all("div", class_="col-12 col-sm-6 col-md-6 col-xl-4")

    # Extract data for each article
    for article in articles:
        try:
            title = article.find("h3", class_="card-title").text.strip()
            link = article.find("a", class_="stretched-link")["href"].strip()
            date = article.find("small", class_="text-muted time").text.strip()
            
            # Scrape comments for the article
            comments = scrap_comments(link)
            
            # Store the extracted data in a dictionary
            articles_data.append({
                "title": title,
                "url": link,
                "date": date,
                "comments": comments,
            })
        except AttributeError:
            # Skip articles with missing data
            continue

    # Save the scraped data to a JSON file
    filename = f"{category}.json"

    # Load existing data if the file already exists
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as json_file:
            existing_data = json.load(json_file)
    else:
        existing_data = []

    # Merge the new data with existing data, avoiding duplicates
    existing_urls = {article["url"] for article in existing_data}
    new_articles = [article for article in articles_data if article["url"] not in existing_urls]

    # Update the existing data with new articles
    existing_data.extend(new_articles)

    # Save the updated data back to the file
    with open(filename, "w", encoding="utf-8") as json_file:
        json.dump(existing_data, json_file, ensure_ascii=False, indent=4)

    print(f"Scraped {len(new_articles)} new articles and updated {filename}.")

# Example usage
scrap_articles_by_category("politique")

def analyze_data(category):
    """
    Analyze scraped data: total articles, total comments, and comment evolution by date.
    """
    filename = f"{category}.json"
    if not os.path.exists(filename):
        print(f"No data file found for category '{category}'. Run scraping first!")
        return None

    with open(filename, "r", encoding="utf-8") as json_file:
        articles_data = json.load(json_file)

    # Total number of articles
    total_articles = len(articles_data)

    # Flatten all comments into a single list
    all_comments = [
        {
            "date": comment["date"],
            "text": comment["text"],
            "author": comment["author"]
        }
        for article in articles_data
        for comment in article.get("comments", [])
    ]
    total_comments = len(all_comments)

    # Convert comments to a DataFrame for analysis
    comments_df = pd.DataFrame(all_comments)
    if not comments_df.empty:
        locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")  # Use "fr_FR.UTF-8" or "French_France" based on your system.

        # Parse dates directly
        comments_df["date"] = pd.to_datetime(comments_df["date"], format="%A %d %B %Y - %H:%M", errors="coerce")
        # Standardize the date format (if needed) and count comments by date
        comments_by_date = comments_df.groupby(comments_df["date"].dt.date).size().reset_index(name="count")
    else:
        comments_by_date = pd.DataFrame(columns=["date", "count"])

    print(f"Total Articles: {total_articles}")
    print(f"Total Comments: {total_comments}")
    print(f"Comment Evolution:\n{comments_by_date}")

    return {
        "total_articles": total_articles,
        "total_comments": total_comments,
        "comments_by_date": comments_by_date
    }

scrap_articles_by_category("politique")
analysis = analyze_data("politique")
if analysis:
    print(f"Total Articles: {analysis['total_articles']}")
    print(f"Total Comments: {analysis['total_comments']}")
    print("Comments by Date:")

    print(analysis["comments_by_date"])

