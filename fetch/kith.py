import time
import requests
from urllib.request import Request, urlopen
import urllib.parse
from bs4 import BeautifulSoup
import json

cookies = {}


def set_cookies(response) -> None:
    # set response cookie for some query
    cookies.update(response.cookies.get_dict())


def get_data_about_product(product_item_link: str, size: str, quantity: int) -> str:
    # get data about product to add to cart

    req = Request(product_item_link)
    html_page = urlopen(req)
    soup = BeautifulSoup(html_page, "lxml")
    result = soup.find_all('option')
    value = ''
    for item in result:
        if item.text.strip() == size and item['value'] != size:
            value = item['value']
            break
    return 'properties%5Bupsell&option-0={}&id={}&quantity={}'.format(size, value, quantity)


def remove_backspace(keyword: str) -> str:
    # replace all backspace on plus for query
    new_keyword = ''
    for elem in keyword:
        if elem == ' ':
            elem = '+'
        new_keyword += elem
    return new_keyword


def search_for_keyword(keyword: str) -> str:
    # get product link from search on site
    keyword = remove_backspace(keyword)
    url = 'https://www.searchanise.com/getresults?api_key=3J2M9Q3r7i&q={}&sortBy=relevance&sortOrder=desc&restrictBy%5Bquantity%5D=1%7C&startIndex=0&maxResults=48&items=true&pages=true&categories=true&suggestions=true&queryCorrection=true&suggestionsMaxResults=3&pageStartIndex=0&pagesMaxResults=20&categoryStartIndex=0&categoriesMaxResults=20&facets=false&facetsShowUnavailableOptions=false&ResultsTitleStrings=2&ResultsDescriptionStrings=0&output=jsonp&callback=jQuery224011380430002526187_1604172407351&_=1604172407352"'.format(
        keyword)
    headers = {
        "credentials": "omit",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "referrer": "https://kith.com/",
        "mode": "cors"
    }

    response = requests.get(url=url, headers=headers)
    product_item_link = response.text
    index = product_item_link.find('"link"') + 8
    result = ''
    for i in range(index, len(product_item_link)):
        if product_item_link[i] == '\"':
            break
        if product_item_link[i] != '\\':
            result += product_item_link[i]
    return result


def add_to_cart(product_item_link: str, size: str, quantity: str) -> str:
    # add product to cart and get cookies - cart token
    headers = {
        "credentials": "include",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Content-type": "application/x-www-form-urlencoded",
        "Cache-Control": "max-age=0",
        "referrer": product_item_link,
        "mode": "cors"
    }

    response = requests.post(
        url='https://kith.com/cart/add.js', headers=headers, cookies=cookies, data=get_data_about_product(product_item_link, size, quantity))
    set_cookies(response)
    return 'added to cart'


def get_data_from_cart(product_item_link: str) -> str:
    # get data for query getting hash cart
    url = "https://kith.com/cart.js"
    headers = {
        "credentials": "include",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.5",
        "X-Requested-With": "XMLHttpRequest",
        "referrer": product_item_link,
        "mode": "cors"
    }

    response = requests.get(headers=headers, url=url, cookies=cookies)
    return response.text


def form_data_for_get_hash(query_data: str) -> str:
    # process data for query get hash

    data = 'MerchantCartToken={}&CountryCode=RU&CurrencyCode=RUB&CultureCode=ru&MerchantId=583&ClientCartContent='.format(
        cookies['cart'])
    data += urllib.parse.quote(query_data)
    return data


def get_cart_hash(query_data: str) -> str:
    # get hash for getting cart token
    url = "https://gepi.global-e.com/Checkout/GetCartToken"
    headers = {
        "credentials": "omit",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Content-type": "application/x-www-form-urlencoded",
        "referrer": "https://kith.com/",
        "mode": "cors"
    }
    data = form_data_for_get_hash(query_data)

    response = requests.post(url=url, headers=headers, data=data)
    response = json.loads(response.text.replace("'", '"'))
    return response['Hash']


def get_order_url(cart_hash: str) -> str:
    # get url for order
    now_time = str(time.time()).replace('.', '')[0:11]
    url = "https://gepi.global-e.com/Checkout/GetQueuedData?hash={}&jsoncallback=callback_{}".format(
        cart_hash, now_time)
    return url


def get_cart_token(cart_hash: str) -> str:
    # get cart token
    url = get_order_url(cart_hash)
    payload = {}

    response = requests.request("GET", url, data=payload).text
    time.sleep(2)
    response = requests.get(url, data=payload)
    set_cookies(response)
    response = response.text.split(')')[0].split('(')[1]
    response = json.loads(response)
    return response['CartToken']


def send_shiping_data(cart_token, first_name, last_name, address1, address2, phone, city, zip_code, email) -> str:
    # send shiping data
    url = "https://fs.global-e.com/checkoutv2/handleaction"
    headers = {
        "credentials": "include",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0",
        "Accept": "text/html, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.5",
        "Content-Type": "application/json; charset=utf-8",
        "cultureid": "1033",
        "X-Requested-With": "XMLHttpRequest"
    }
    data = {"Action": 1, "Token": cart_token, "ShippingCountryID": "159",
            "ShippingMethodID": "1776", "CultureID": "1033", "BillingData":
            {"FirstName": first_name, "LastName": last_name, "Address1": address1,
             "Address2": address2, "Phone": phone, "CountryId": "159", "City": city, "Zip": zip_code, "Email": email},
            "ShippingData": None, "City": city, "IsCollectionPoints": False, "BillingSameAsShipping": True}

    response = requests.post(url=url, headers=headers,
                             json=data, cookies=cookies)
    return response.text


def send_payment_data(cart_token) -> str:
    # send data about payment method
    url = "https://fs.global-e.com/checkoutv2/handleaction"
    headers = {
        "credentials": "include",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0",
        "Accept": "text/html, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.5",
        "Content-Type": "application/json; charset=utf-8",
        "cultureid": "1033",
        "X-Requested-With": "XMLHttpRequest"
    }
    data = {"Action": 3, "Token": cart_token, "ShippingMethodID": 1776,
            "IsSameDayDispatchChecked": False, "SelectedPaymentMethodID": 4, "ShippingCountryID": 159}

    response = requests.post(url=url, headers=headers,
                             json=data, cookies=cookies)
    return response.text


def save_order(cart_token, first_name, last_name, email, address1, address2, city, zip_code, phone) -> str:
    # save order on site
    url = "https://fs.global-e.com/checkoutv2/save"
    data = '''CheckoutData.CartToken={}
    &CheckoutData.CultureID=1033&CheckoutData.IsVirtualOrder=False
    &CheckoutData.ExternalData.CurrentGatewayId=6
    &CheckoutData.ExternalData.AllowedCharsRegex=%5E%5BA-Za-z0-9%2C%22%22%5Cs%40%26%25%24%23%5C*%5C(%5C)%5C%5B%5C%5D._%5C-%5Cs%5C%5C%2F%5D*%24&CheckoutData.ExternalData.UnsupportedCharactersErrorTipTimeout=15000
    &CheckoutData.EnableUnsupportedCharactersValidation=True
    &CheckoutData.BillingFirstName={}
    &CheckoutData.BillingLastName={}
    &CheckoutData.Email={}&CheckoutData.BillingCountryID=159
    &CheckoutData.BillingAddress1={}
    &CheckoutData.BillingAddress2={}
    &CheckoutData.BillingCity={}
    &CheckoutData.BillingCountyID=
    &CheckoutData.BillingZIP={}
    &CheckoutData.BillingStateID=
    &CheckoutData.BillingPhone={}&CheckoutData.OffersFromMerchant=true
    &CheckoutData.OffersFromMerchant=false
    &CheckoutData.ShippingType=ShippingSameAsBilling
    &CheckoutData.ShippingFirstName=
    &CheckoutData.ShippingLastName=
    &CheckoutData.ShippingCountryID=159
    &CheckoutData.ShippingAddress1=
    &CheckoutData.ShippingAddress2
    =&CheckoutData.ShippingCity=
    &CheckoutData.ShippingCountyID=
    &CheckoutData.ShippingZIP=
    &CheckoutData.ShippingStateID=
    &CheckoutData.ShippingPhone=
    &CheckoutData.SelectedShippingOptionID=1776
    &CheckoutData.SelectedTaxOption=3
    &CheckoutData.StoreID=0&CheckoutData.AddressVerified=true
    &CheckoutData.SelectedPaymentMethodID=4
    &CheckoutData.CurrentPaymentGayewayID=11
    &CheckoutData.MerchantID=583&CheckoutData.MultipleAddressesMode=false
    &CheckoutData.MerchantSupportsAddressName=false
    &CheckoutData.MultipleAddressesMode=true
    &CheckoutData.MultipleAddressesMode=true
    &CheckoutData.MultipleAddressesMode=true
    &CheckoutData.MultipleAddressesMode=true
    &CheckoutData.CollectionPointZip=
    &CheckoutData.UseAvalara=false
    &CheckoutData.IsAvalaraLoaded=false
    &CheckoutData.IsUnsupportedRegion=
    &CheckoutData.IsShowTitle=false
    &CheckoutData.IsBillingSavedAddressUsed=false
    &CheckoutData.IsShippingSavedAddressUsed=false
    &CheckoutData.SaveBillingCountryOnChange=false
    &CheckoutData.OffersFromMerchant=true
    &CheckoutData.DoLightSave=false
    &CheckoutData.OffersFromMerchant=true
    &CheckoutData.OffersFromMerchant=true'''.format(cart_token, urllib.parse.quote(first_name),
                                                    urllib.parse.quote(last_name), urllib.parse.quote(
        email), urllib.parse.quote(address1),
        urllib.parse.quote(address2), urllib.parse.quote(city), zip_code, urllib.parse.quote(phone))
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        'Origin': 'https://fs.global-e.com'}

    response = requests.post(url=url, headers=headers,
                             data=data, cookies=cookies)
    print(response.text)
    return response.text


def pay_order(cartToken) -> str:
    # get payment link
    url = "https://fs.global-e.com/Payments/GetPaymentFormParametersV2"
    headers = {
        "credentials": "include",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0",
        "Accept": "text/html, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.5",
        "Content-Type": "application/json; charset=utf-8",
        "cultureid": "1033",
        "X-Requested-With": "XMLHttpRequest"
    }
    data = {"paymentMethodId": 4, "cartToken": cartToken, "machineId": "0400p0K0NBddpWYXk1Rjuv1iJgWxIe7xNABi4fWLoKuCjDO1I7X1XkVbR56yHWIulRE2G351wfp+MZWAa+qm7VSS+5sZhQDshHSvULHursuudujzOyAVXY9dOImyPk/jhpVjiK5kRyHDdgGuap1kCs/3zAKUaoVZuERGMVX5qqOtgGHGSKEVXX0NvatW7zepYQR+6QUDqugXYYeM/P8l/YckxNagR+wrhtnGDIKINVrQrNLcRehbfBGuVwB7Zazj3KJbuZFchGeVJ9QNczN14q3lywh3sf2PehRXzj2EVbG43hrxwUJvdekrQtebRcG2+TZFbazR87feXj4F7PqEEHOtLa6xraOOHRWfcUJLSeiXEU4c5liAtxprcmIRq1rS8V2bJXfBNacN7f66azT6SdrSdfgqhnKLkKSn5dzgojLfFGvY6Cb2Pd9pAvT9o4EX2cJhgriaMoAypQuyPr0t8ztVFisjUV4dJsOym9ceHDKRCiK4xI1RTIYC8ouD71qCKcmZqa+c5UMfdLNXqLz+1vlqUAr9dE2jcfl0wgroQBfpyuIxKQ6D/SmUQZKprRlxkddQVTw2C4oQ2p7A55kYfO334Y+Mvqo0Vk8dHWRNT5X44krUUDrD47A1Og/HKDxJ7GVDQ1iq1uTKn16ydOxt+NhYlHxYzHV+I3i5diCZhvCP7lumIif/iDuMCcLUB69g4E97xS9GTGQ/PXFotJL2HHLeKMCq9DH/qIFm6XNHeKh/DF9tKemmFtzTRdFj+gRfPB481PXpN4zl2IQd/tZS2Kh2ROMIIApB8QUcVG6QOLISOHQO0+r+OXJLS1TDSLoO5541pqenrHyiDh1WC4Z0KPmWF1wL43cCLwVlOe0RxWZbWQztoAqKG6u/6pKetslI3IixYH1H5YVrp931cG5K8TAEkP8V8c+YhydhouMC+WQLqLHkbAxyEijNfQl2Y1Y/iacvJIgSaTKjMP0lQXiswK7viWF8hRwW7Jsss29L0sFkQPnkjHloApNDPIFOfqX9KhrdBlIOn3E5YIdc6njJgQh/4vXJiqy0MXMQOxLdmoenKqOSBBWhu07LmRdt5U4CpewIj2qku3ZkvzlNGQrSvitEtP2gutXD3D+VjXOee1yaDxciKug0+fq4xP2vFnup4QVZJMaWOr1dWZjaXqOvX6vrLi4e/71zUkq39uEtbjul6aqzx4OFCd79SwES/cJL9+lBnvYvTTRsK71YmNk0m3uC3iw+Jld00Kp8V+xdkUvJmSuTQKA1/WzgaQalR6tq92sLtG+eLgK9ponIlmaUSV2CjK+JB4CfhpnjLJdkRO+fBjqcU0hcKJmgoTLznquSFalWBN7GaDYQ2iKysRqfEatYuwnoooi+v0kaleFFg3SnwvgGkbPaleERU5bxIz+15A9VVdG/+c6dIyq9R0G9Uv1IAvq8sRqQvy4U", "pmExtraData": None, "isNewWindow": False}

    response = requests.post(url=url, headers=headers,
                             json=data, cookies=cookies)
    response = json.loads(response.text)
    return response["Action"]


def start():
    # TEST data
    # функция , которую можно вызвать, чтоб отправить тестовые данные. Рузультат: ссылка на пейпал
    # вместо ссылки на пейпал надо вывести на фронт оплату картой. Предполагаю, во фрейме
    try:
        # поискать товар
        product = search_for_keyword(
            'Women Jackie Tank Bodysuit')
        # добавить в корзину
        added = add_to_cart(product, 'M', 1)
        if added is Exception:
            raise added
        # получить данные из корзины для отправки в заказ
        data = get_data_from_cart(product)
        # это хеш корзины, нужен для запроса в заказ
        cart_hash = get_cart_hash(data)
        # это токен корзины, тоже нужен для запроса в заказ
        token = get_cart_token(cart_hash)
        # отправка данных о доставке
        send_shiping_data(token, 'test', 'test', 'test', 'test',
                          '89999999999', 'Moscow', 308000, 'test@test.com')
        # отправка данных о способе оплаты
        send_payment_data(token)
        # сохранение (подтверждение) заказа
        save_order(token, 'test', 'test', 'test@test.com', 'test',
                   'test', 'Moscow', 308000, '89999999999')
        # получение ссылки на пейпал для оплаты
        pay_link = pay_order(token)
        print(pay_link)
        return pay_link

    except Exception as ex:
        print(repr(ex))
        return ex
