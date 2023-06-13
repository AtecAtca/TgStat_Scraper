from bs4 import BeautifulSoup
import requests

class ChannelNotFound(Exception):
    pass

class AuthorisationError(Exception):
    pass


def scrape_info(channel_data, category, channel_info=None, channel_url=None):
    if channel_info is None:
        channel_info = {
            'CATEGORY': category,
            'NAME': channel_data[0],
            'DESCRIPTION': None,
        }
    if channel_url is None:
        channel_url = {
            'TGSTAT_URL': channel_data[1],
            'TELEGRAM_URL': channel_data[2]
        }

    url = channel_url['TGSTAT_URL']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/113.0.0.0 Safari/537.36'
    }

    stats = scrape_stats(url, headers)
    return channel_info | stats | channel_url


def scrape_stats(url, headers, description=None):
    if description is None:
        description = {
            'DESCRIPTION': None,
        }


    url = url + '/stat'
    r = requests.get(url, headers=headers)
    html_doc = r.text
    soup = BeautifulSoup(html_doc, 'html.parser')

    is_authorised(soup)
    is_exist(soup)

    description_div = soup.find_all(class_="col-12 col-sm-7 col-md-8 col-lg-6")
    p_tag = description_div[0].find('p', class_='card-text')
    if p_tag is not None:
        description['DESCRIPTION'] = p_tag.get_text(separator='\n').strip()

    geolang = get_geolang(description_div[0].text)
    general_stats = get_general_stats(soup)
    return description | general_stats | geolang


def get_geolang(string, geolang=None):
    if geolang is None:
        geolang = {
            'LOCATION': None,
            'LANGUAGE': None
        }

    description = string.split('\n')
    try:
        geolang_index = description.index('Гео и язык канала:')
    except ValueError as e:
        raise ChannelNotFound
    else:
        geolang['LOCATION'] = description[geolang_index+1].strip().replace(',', '')
        geolang['LANGUAGE'] = description[geolang_index+2].strip()
        return geolang


def get_general_stats(soup, general_stats=None):
    if general_stats is None:
        general_stats = {
            'SUBSCRIBERS_TOTAL': None,
            'ERR': None
        }

    div = soup.find_all('div', class_='position-absolute text-uppercase text-dark font-12')
    for i in div:
        text = i.text.strip()
        if text == 'подписчики':
            parent_div  = i.parent
            h2_tag = parent_div.find_all('h2', class_='text-dark')
            general_stats['SUBSCRIBERS_TOTAL'] = int(h2_tag[0].text.strip().replace(' ', ''))

        elif text == 'вовлеченность подписчиков (ERR)':
            parent_div  = i.parent
            h2_tag = parent_div.find_all('h2', class_='text-dark text-right')
            try:
                general_stats['ERR'] = h2_tag[0].text.strip()
            except IndexError as e:
                general_stats['ERR'] = None

    return general_stats


def is_exist(soup):
    div_tag = soup.find_all('div', class_='card cta-box bg-danger text-white mx-n3 mt-n3')
    if div_tag != []:
        raise ChannelNotFound


def is_authorised(soup):
    div_tag = soup.find_all('div', class_='container-fluid px-2 px-md-3')
    div_text = div_tag[0].get_text().strip()

    if div_tag != [] and 'Требуется авторизация' in div_text:
        raise AuthorisationError
