# scraper.py
import requests
from bs4 import BeautifulSoup

def scrape_articles(username, password):
    login_url = 'https://32beatwriters.com/login/'
    blog_url = 'https://32beatwriters.com/our-blog/'

    session = requests.Session()

    login_payload = {
        'log': username,
        'pwd': password,
        'wp-submit': 'Log In',
        'redirect_to': blog_url,
        'testcookie': '1'
    }

    response = session.post(login_url, data=login_payload)

    if 'Log Out' in response.text:
        print("Login successful!")
    else:
        print("Login failed!")
        return []

    response = session.get(blog_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    articles = soup.find_all('h1', class_='elementor-heading-title elementor-size-default')

    article_data = []

    for article in articles:
        title = article.text
        article_url = 'https://32beatwriters.com/article/' + title.replace(' ', '-').lower()

        article_response = session.get(article_url)
        article_soup = BeautifulSoup(article_response.content, 'html.parser')

        content_sections = article_soup.find_all('p', class_='has-medium-font-size')

        for section in content_sections:
            team_name = section.strong.text if section.strong else None
            content = section.find_next_sibling('p').text if section.find_next_sibling('p') else None

            article_data.append({
                'title': title,
                'url': article_url,
                'team': team_name,
                'content': content
            })

    return article_data
