from bs4 import BeautifulSoup
import urllib.parse
import requests
cookies = {}


def set_cookies(response) -> None:
    # set response cookie for some query
    cookies.update(response.cookies.get_dict())


def search_for_keyboard(keyboard: str):
    headers = {
        'authority': 'uk.octobersveryown.com',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 YaBrowser/20.9.3.136 Yowser/2.5 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'accept-language': 'ru,en;q=0.9',
    }

    params = (('q', keyboard),)
    response = requests.get(
        'https://uk.octobersveryown.com/search', headers=headers, params=params)
    soup = BeautifulSoup(response.content, 'html.parser')
    product_link = 'https://uk.octobersveryown.com' + soup.find_all(
        'p', attrs={'class': 'product-title'})[0].findNext().attrs['href']
    set_cookies(response)
    return product_link


def process_size(option):
    size = option.split()[0]
    return size.lower()


def search_variant_id(product_link, size):
    response = requests.get(product_link)
    set_cookies(response)
    soup = BeautifulSoup(response.content, 'html.parser')
    options = soup.find_all('option')
    for option in options:
        find_size = process_size(option.text.strip())
        if str(find_size) == str(size):
            try:
                variant_id = option.attrs['value']
                return variant_id
            except:
                pass


def add_to_cart(variant_id):
    headers = {
        'authority': 'uk.octobersveryown.com',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'x-requested-with': 'XMLHttpRequest',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 YaBrowser/20.9.3.136 Yowser/2.5 Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://uk.octobersveryown.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'accept-language': 'ru,en;q=0.9',
    }

    data = {
        'id': variant_id
    }
    response = requests.post('https://uk.octobersveryown.com/cart/add.js',
                             headers=headers, data=data, cookies=cookies)
    set_cookies(response)


def get_checkout_url():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://uk.octobersveryown.com',
        'Connection': 'keep-alive',
        'Referer': 'https://uk.octobersveryown.com/cart',
        'Upgrade-Insecure-Requests': '1',
        'TE': 'Trailers',
    }

    data = {
        'updates[]': '1',
        'checkout': 'CHECKOUT'
    }
    response = requests.post(
        'https://uk.octobersveryown.com/cart', headers=headers, cookies=cookies, data=data)
    set_cookies(response)
    return response.url


def send_shipping_data(checkout_url, email, first_name, last_name, address1, city, country, zip_code, phone):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://uk.octobersveryown.com',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'TE': 'Trailers',
    }
    data = [
        ('_method', 'patch'),
        ('previous_step', 'contact_information'),
        ('step', 'shipping_method'),
        ('checkout[email]', email),
        ('checkout[buyer_accepts_marketing]', '0'),
        ('checkout[shipping_address][first_name]', ''),
        ('checkout[shipping_address][first_name]', first_name),
        ('checkout[shipping_address][last_name]', ''),
        ('checkout[shipping_address][last_name]', last_name),
        ('checkout[shipping_address][address1]', ''),
        ('checkout[shipping_address][address1]', address1),
        ('checkout[shipping_address][address2]', ''),
        ('checkout[shipping_address][address2]', ''),
        ('checkout[shipping_address][city]', ''),
        ('checkout[shipping_address][city]', city),
        ('checkout[shipping_address][country]', ''),
        ('checkout[shipping_address][country]', country),
        ('checkout[shipping_address][province]', ''),
        ('checkout[shipping_address][zip]', ''),
        ('checkout[shipping_address][zip]', zip_code),
        ('checkout[shipping_address][phone]', ''),
        ('checkout[shipping_address][phone]', phone),
        ('checkout[remember_me]', 'false'),
        ('checkout[remember_me]', '0'),
        ('checkout[client_details][browser_width]', '1519'),
        ('checkout[client_details][browser_height]', '503'),
        ('checkout[client_details][javascript_enabled]', '1'),
        ('checkout[client_details][color_depth]', '24'),
        ('checkout[client_details][java_enabled]', 'false'),
        ('checkout[client_details][browser_tz]', '-180'),
    ]
    response = requests.post(
        checkout_url, headers=headers, cookies=cookies, data=data)


def start():
    # найти товар по ключу
    product_link = search_for_keyboard('MARIGOLD TARTAN PLAID SHIRT')
    # получить вариант айди по размеру из html. Нужно для передачи в запрос добавления в корзину
    variant_id = search_variant_id(product_link, 'small')
    # добавить товар в корзину
    cart = add_to_cart(variant_id)
    # получить уникальный урл заказа
    checkout_url = get_checkout_url()
    # отправить данные о доставке
    send_shipping_data(checkout_url, 'test@gmail.com', 'test',
                       'test', '4 test', 'Berlin', 'Germany', 10115, '+19995559955')
    # вывести на фронт шаг оплаты на сайте (не реализовано)
