from bs4 import BeautifulSoup
import requests
import csv

def scrape_categories():
    url = 'https://uk.tgstat.com'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/113.0.0.0 Safari/537.36'
    }
    r = requests.get(url, headers=headers)
    html_doc = r.text
    soup = BeautifulSoup(html_doc, 'html.parser')
    div_list = soup.find_all('div', class_="card border m-0")

    category_names = div_list[1].find_all('a')
    category_count = div_list[1].find_all('div', class_='col col-3 text-right font-12 text-muted text-truncate')
    categories = get_categories(category_names, category_count, sort_by='popular')
    return categories


def get_categories(category_names, category_count, result=None, sort_by=None):
    if result is None:
        result = []
    for i in zip(category_names, category_count):
        name = i[0].text.strip()
        href = i[0].get('href')
        count = int_formatter(i[1].text.strip())
        result.append((name, href, count))

    if sort_by is None:
        return result
    elif sort_by == 'popular':
        return sorted(result, key=lambda x: x[2], reverse=True)


def int_formatter(string):
    if 'k' in string:
        return int(string.replace('k', '00').replace('.', ''))
    else:
        return int(string)


def save_categories(all_categories, filename):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(all_categories)
    return


def read_categories(filename, all_categories=None):
    if all_categories is None:
        all_categories = []
    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            all_categories.append((row[0], row[1], int(row[-1])))
    return all_categories