from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import csv


def scrape_channels(href, result=None):
    if result is None:
        result = []
    chrome_options = Options()
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")

    url = f"https://uk.tgstat.com{href}"

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    wait = WebDriverWait(driver, 1)

    button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Показать больше')]")))
    div_list = None
    while button:
        driver.execute_script("arguments[0].click();", button)
        try:
            button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Показать больше')]")))
        except TimeoutException as e:
            soup = BeautifulSoup(driver.page_source, "html.parser")
            div_list = soup.find_all('div', class_="col-12 col-sm-6 col-md-4")
            button = None
    driver.quit()

    for i in div_list:
        href = i.find_all('a')
        name = i.find_all('div', class_='font-16 text-dark text-truncate')
        for e in zip(href, name):
            text = e[0].text.strip().split('\n')
            channel_name = text[0]
            tgstat_url = e[0].get('href')
            tg_link = url_formatter(tgstat_url.split('/')[-1])
            result.append((channel_name, tgstat_url, tg_link))
    return result


def url_formatter(string):
    if '@' in string:
        return f"https://t.me/{string.replace('@', '')}"
    else:
        return f'https://t.me/joinchat/{string}'


def save_channels(all_channels, filename):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(all_channels)
    return


def read_channels(filename, checkpoint, all_channels=None):
    if all_channels is None:
        all_channels = []

    with open(filename, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if checkpoint is not None:
                if str(row) != checkpoint[1]:
                    continue
                else:
                    all_channels.append(row)
                    checkpoint = None
            else:
                all_channels.append(row)

    return all_channels

