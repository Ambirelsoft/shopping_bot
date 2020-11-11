import json
from urllib.request import Request, urlopen
import urllib.parse
from bs4 import BeautifulSoup

import requests

cookies = {}


def set_cookies(response) -> None:
    # set response cookie for some query
    cookies.update(response.cookies.get_dict())


def add_to_cart(session, variant_id):
    url = 'https://www.notre-shop.com/cart/add.js'
    data = {'id': variant_id}
    result = session.post(url=url, json=data, cookies=cookies)
    set_cookies(result)
    cart_token = result.cookies.get_dict()['cart']
    return cart_token


def get_total_price(session, checkout_token):
    url = "https://www.notre-shop.com/6240605/checkouts/{}".format(
        checkout_token)
    result = session.get(url, cookies=cookies)
    soup = BeautifulSoup(result.content, 'html.parser')
    price = soup.find_all(
        'span', attrs={'class': 'payment-due__price'})[0].text
    total_price = ''
    for symbol in price:
        try:
            int(symbol)
            total_price += symbol
        except:
            pass
    return total_price


def process_keyboard(keyword: str) -> str:
    new_keyword = ''
    for elem in keyword:
        if elem == ' ' or elem == '/':
            elem = '-'
        new_keyword += elem
    return new_keyword


def search_for_keyword(session, keyword: str) -> str:
    url = "https://www.notre-shop.com/products/{}".format(
        process_keyboard(keyword))
    result = session.get(url)
    set_cookies(result)
    if result.status_code == 404:
        raise KeyError
    return url


def checkout(session, cart_token):
    url = 'https://www.notre-shop.com/checkout'
    result = session.get(url=url, cookies=cookies)
    set_cookies(result)
    a = result.cookies.get_dict()
    return result.cookies.get_dict()['tracked_start_checkout']


def get_variant_id(product_item_link, size):
    cookies.update(
        {'shopify_recently_viewed': product_item_link.split('/')[-1].lower()})
    cookies.update({'shopify_pay_redirect': 'pending'})
    req = Request(product_item_link)
    html_page = urlopen(req)
    soup = BeautifulSoup(html_page, "lxml")
    result = soup.find_all('option')
    for elem in result:
        if str(elem.text).strip() == size:
            return elem.attrs['data-id']


def set_other_cookies(session):
    cookies.update({'__kla_id': 'eyIkcmVmZXJyZXIiOnsidHMiOjE2MDQ4Mzk0NjcsInZhbHVlIjoiIiwiZmlyc3RfcGFnZSI6Imh0dHBzOi8vd3d3Lm5vdHJlLXNob3AuY29tLyJ9LCIkbGFzdF9yZWZlcnJlciI6eyJ0cyI6MTYwNDgzOTQ2NywidmFsdWUiOiIiLCJmaXJzdF9wYWdlIjoiaHR0cHM6Ly93d3cubm90cmUtc2hvcC5jb20vIn19'})
    cookies.update({'wisepops_session': '%7B%22arrivalOnSite%22%3A%222020-11-08T08%3A46%3A45.542Z%22%2C%22mtime%22%3A%222020-11-08T08%3A46%3A52.901Z%22%2C%22pageviews%22%3A3%2C%22popups%22%3A%7B%7D%2C%22src%22%3Anull%2C%22utm%22%3A%7B%7D%7D',
                    })
    cookies.update({'_landing_page': '%2F'})


def send_shipping_data(session, checkout_token, aut_token, email, first_name, last_name, address, city, country, province, zip_code, phone):
    url = "https://www.notre-shop.com/6240605/checkouts/{}".format(
        checkout_token)
    print(url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.notre-shop.com/',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://www.notre-shop.com',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'TE': 'Trailers',
    }
    body = [
        ('_method', 'patch'),

        ('previous_step', 'contact_information'),
        ('step', 'shipping_method'),
        ('checkout[email]', email),
        ('checkout[buyer_accepts_marketing]', '0'),
        ('checkout[buyer_accepts_marketing]', '1'),
        ('checkout[shipping_address][first_name]', ''),
        ('checkout[shipping_address][first_name]', first_name),
        ('checkout[shipping_address][last_name]', ''),
        ('checkout[shipping_address][last_name]', last_name),
        ('checkout[shipping_address][company]', ''),
        ('checkout[shipping_address][company]', ''),
        ('checkout[shipping_address][address1]', ''),
        ('checkout[shipping_address][address1]', address),
        ('checkout[shipping_address][address2]', ''),
        ('checkout[shipping_address][address2]', ''),
        ('checkout[shipping_address][city]', ''),
        ('checkout[shipping_address][city]', city),
        ('checkout[shipping_address][country]', ''),
        ('checkout[shipping_address][country]', country),
        ('checkout[shipping_address][province]', ''),
        ('checkout[shipping_address][province]', province),
        ('checkout[shipping_address][zip]', ''),
        ('checkout[shipping_address][zip]', zip_code),
        ('checkout[shipping_address][phone]', ''),
        ('checkout[shipping_address][phone]', phone),
        ('checkout[client_details][browser_width]', '1519'),
        ('checkout[client_details][browser_height]', '420'),
        ('checkout[client_details][javascript_enabled]', '1'),
        ('checkout[client_details][color_depth]', '24'),
        ('checkout[client_details][java_enabled]', 'false'),
        ('checkout[client_details][browser_tz]', '-180'),
    ]
    result = session.post(
        url=url, data=body, cookies=cookies, headers=headers)
    print(result.history)
    print('sucsess')


def get_payment_link(session, checkout_token, total_price):
    url = 'https://www.notre-shop.com/6240605/checkouts/{}'.format(
        checkout_token)
    print(url)
    print(cookies)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.notre-shop.com/',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://www.notre-shop.com',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'TE': 'Trailers',
    }
    data = [
        ('_method', 'patch'),
        ('previous_step', 'payment_method'),
        ('step', ''),
        ('s', ''),
        ('checkout[payment_gateway]', '8410607'),
        ('checkout[different_billing_address]', 'false'),
        ('checkout[remember_me]', 'false'),
        ('checkout[remember_me]', '0'),
        ('checkout[vault_phone]', ''),
        ('checkout[total_price]', total_price),
        ('complete', '1'),
        ('checkout[client_details][browser_width]', '1519'),
        ('checkout[client_details][browser_height]', '420'),
        ('checkout[client_details][javascript_enabled]', '1'),
        ('checkout[client_details][color_depth]', '24'),
        ('checkout[client_details][java_enabled]', 'false'),
        ('checkout[client_details][browser_tz]', '-180'),
    ]
    result = session.post(
        url, data=data, headers=headers, cookies=cookies)


def start():
    # выполнять все в одной сессии
    session = requests.Session()
    # добавить куки базовые для всех запросов
    set_other_cookies(session)
    # найти товар по ключю
    url = search_for_keyword(session, 'parka in grey')
    # для добавления в корзину нужно получить вариант айди. Он прям в html для каждого размера. Тут М это размер
    variant = get_variant_id(url, 'M')
    # получение токена корзины
    token = add_to_cart(session, variant)
    # отправить запрос на заказ и получить данные
    chek = checkout(session, token)
    # отправить данные о доставке
    send_shipping_data(session, chek, '123', 'test@gmail.com', 'test', 'test',
                       '2718+Lee+Meadows+Drive', 'Moody', 'United States', 'AL', 35004, '+1+999-555-9999')
    # получить итоговую стоимость заказанных товаров и передать ее потом в след.функцию
    total_price = get_total_price(session, chek)
    # получить ссылку на оплату. ФУНКЦИЯ РАБОТАЕТ НЕ ТАК КАК ОЖИДАЕТСЯ.
    # Должен происходить редирект. Не стала доделывать, так как пей пал все равно не нужен
    get_payment_link(session, chek, total_price)
