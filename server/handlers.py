from fetch.kith import search_for_keyword, add_to_cart, get_data_from_cart, get_cart_hash, send_payment_data, send_payment_data, save_order, pay_order, get_cart_token, send_shiping_data

# тут все сырое. Нужно переделывать. Суть : получить json с фронта и обработать его функциями из fetch


def kitch(products, contacts):
    # FIXME
    logs = []
    for item in products:
        try:
            product = search_for_keyword(
                item['keyboard'])
            added = add_to_cart(product, item['size'], item['quntity'])
            if added is Exception:
                raise added
            data = get_data_from_cart(product)
            cart_hash = get_cart_hash(data)
            token = get_cart_token(cart_hash)
            send_shiping_data(token, contacts['firstName'], contacts['lastName'], contacts['lastName'], contacts['firstName'],
                              contacts['tel'], contacts['city'], contacts['zip'], contacts['email'])
            send_payment_data(token)
            save_order(token, contacts['firstName'], contacts['firstName'], contacts['email'], contacts['firstName'],
                       contacts['firstName'], contacts['city'], contacts['zip'], contacts['tel'])
            pay_link = pay_order(token)
            logs.append(pay_link)
        except Exception as ex:
            print(repr(ex))
            logs.append(repr(ex))
    return logs


def process_data(data):
    products = []
    contacts = {}
    for key, value in data.items():
        if key == "kitch":
            products = value
        elif key == "contacts":
            contacts = value
    logs = kitch(products, contacts)
    print(logs)
    return logs
