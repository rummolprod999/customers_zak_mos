import json
import urllib.parse
import urllib.request

import timeout_decorator

export_text = 'customers.txt'
customers = set()
url_list = 'https://old.zakupki.mos.ru/api/Cssp/Customer/PostQuery'
url_cus = 'https://old.zakupki.mos.ru/api/Cssp/Customer/GetEntity?id='


def main():
    get_customers_list()
    print(len(customers))
    get_customers()


@timeout_decorator.timeout(35)
def download_list(url, i):
    data = {
        "filter": {"treePathIds": 'null', "regionPaths": [".504."], "companyNameLike": 'null', "companyInnLike": 'null',
                   "companyOgrnLike": 'null', "companyKppLike": 'null', "showArchived": 'null', "registered": 'null',
                   "showChildren": 'null', "isWorksOnFz223": 'null'}, "take": "50", "skip": i,
        "order": [{"field": "id", "desc": 'true'}], "withCount": 'true'}
    data = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(url=url, data=data)
    handler = urllib.request.urlopen(req, timeout=30)
    page = handler.read().decode('utf-8')
    return page


@timeout_decorator.timeout(35)
def download_customer(i):
    url = f'{url_cus}{i}'
    req = urllib.request.Request(url=url)
    handler = urllib.request.urlopen(req, timeout=30)
    page = handler.read().decode('utf-8')
    return page


def get_customers():
    for cus in customers:
        try:
            get_customer(cus)
        except Exception as e:
            print(e)


def get_customer(id_cus):
    cus_page = download_customer(id_cus)
    if cus_page == 'null':
        return
    json_l = json.loads(cus_page)
    company_name = ''
    try:
        company_name = json_l['company']['name']
    except Exception as e:
        print(e)
    if company_name == '':
        return
    res_string = f'{company_name}\t'
    for pers in json_l['company']['contactInfos']:
        person = pers['fullName']
        email = pers['email']
        phones = []
        for ph in pers['phones']:
            phones.append(ph['phoneNumber'])
        phones = ', '.join(phones)
        res_string += f'{person}\t{email}\t{phones}\t'
    with open(export_text, 'a') as f:
        f.write(f"{id_cus}\t{res_string}\n")


def get_customers_list():
    max_skip = 2573 // 50 + 2
    for i in range(0, max_skip):
        try:
            get_page_customers(i)
        except Exception as e:
            print(e)


def get_page_customers(i):
    page = download_list(url_list, i)
    json_l = json.loads(page)
    for item in json_l['items']:
        customers.add(item['id'])


if __name__ == "__main__":
    main()
