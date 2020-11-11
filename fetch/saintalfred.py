import requests
import urllib.parse
from bs4 import BeautifulSoup

cookies = {}


def set_cookies(response) -> None:
    # set response cookie for some query
    cookies.update(response.cookies.get_dict())


def search_for_keyword(session, keyword: str) -> str:
    url = 'https://www.saintalfred.com/search?q={}'.format(keyword)
    result = session.get(url)
    set_cookies(result)
    soup = BeautifulSoup(result.content, 'html.parser')
    product_link = 'https://www.saintalfred.com' + soup.find_all(
        'h3', attrs={'class': 'product-list-item-title'})[0].findNext().attrs['href']
    return product_link


def process_size(size):
    result = ''
    for i in range(4):
        try:
            int(size[i])
            result += size[i]
        except:
            if len(size) < 4:
                break
            elif size[i] == '.':
                result += size[i]
            else:
                break
    return result


def get_variant_id(session, product_link: str, size: str):
    html = session.get(product_link)
    set_cookies(html)
    soup = BeautifulSoup(html.content, 'html.parser')
    options = soup.find_all('option')
    for option in options:
        find_size = process_size(option.text.strip())
        if str(find_size) == str(size):
            try:
                variant_id = option.attrs['data-variant-id']
                return variant_id
            except:
                pass


def add_to_cart(session, variant_id):
    headers = {
        'authority': 'www.saintalfred.com',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'x-requested-with': 'XMLHttpRequest',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 YaBrowser/20.9.3.136 Yowser/2.5 Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.saintalfred.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.saintalfred.com/collections/nike-1/products/air-max-iii-2?variant=34668062310444',
        'accept-language': 'ru,en;q=0.9'
    }
    data = {
        'id': variant_id
    }
    response = session.post(
        'https://www.saintalfred.com/cart/add.js', headers=headers, data=data, cookies=cookies)
    print(response.text)


def get_login_page(session):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Referer': 'https://www.saintalfred.com/cart',
        'Upgrade-Insecure-Requests': '1',
        'TE': 'Trailers',
    }
    response = session.get(
        'https://www.saintalfred.com/checkout', headers=headers, cookies=cookies)
    set_cookies(response)
    return response.url


def get_checkout_url(login_page):
    checkout_page = login_page[55:].replace('%2F', '/')
    checkout_page = checkout_page.replace('%3A', '/')
    return checkout_page


def login(session, checkout_url, email, password):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://www.saintalfred.com',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    data = {
        'form_type': 'customer_login',
        'utf8': '\u2713',
        'customer[email]': email,
        'customer[password]': password,
        'checkout_url': checkout_url
    }
    response = session.post('https://www.saintalfred.com/account/login',
                            headers=headers, cookies=cookies, data=data)
    print(response.url)


def start():
    # добавить все в одну сессию
    session = requests.Session()
    # получить ссылку на товар по ключу
    product_link = search_for_keyword(session, 'AIR MAX III')
    # получить вариант айди по размеру для добавления товара в корзину
    variant_id = get_variant_id(session, product_link, '5')
    # добавить товар в корзину
    add = add_to_cart(session, variant_id)
    # получить уникальную страницу авторизации
    login_page = get_login_page(session)
    # вычленить из страницы логина страницу заказа
    checkout_url = get_checkout_url(login_page)
    # авторизоваться
    login(session, checkout_url, 'test@gmail.com', 'q123w456')
    # после авторизации сейчас идет на страницу капчи. нужно пройти капчу и продолжить заказ
