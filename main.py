import time
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import csv
import os.path
from zoneinfo import ZoneInfo


def fetch_parking_page(id):
    url = f"https://www.ahuzot.co.il/Parking/ParkingDetails/?ID={id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as e:
        raise
    else:
        return response.text

def find_parking_status(parking_page):
    soup = BeautifulSoup(parking_page, "html.parser")
    td = soup.find('td', class_='ParkingDetailsTable')
    img_tag = td.find('img') if td else None
    if img_tag:
        image_url = img_tag.get('src')
        if image_url and image_url.endswith('panui.png'):
            return 'available'
        elif image_url:
            return 'full'
    return None

def find_parking_name(parking_page):
    soup = BeautifulSoup(parking_page, "html.parser")
    td = soup.find('td', class_='ParkingTableHeader')
    span = td.find('span', class_='Title') if td else None
    if span:
        return span.text.strip()
    return None

def find_parking_addr(parking_page):
    soup = BeautifulSoup(parking_page, "html.parser")
    td = soup.find('td', class_='ParkingTable')
    main_text = td.find('span', class_='MainText') if td else None
    if main_text:
        address_b = main_text.find('b')
        if address_b:
            address = address_b.text.strip()
            return address
    return None

def write_parking_status(id, res):
    name, addr, status = None, None, None
    try:
        parking_page = fetch_parking_page(id)
        name = find_parking_name(parking_page)
        addr = find_parking_addr(parking_page)
        status = find_parking_status(parking_page)
    except Exception as e:
        print(e)
    finally:
        with open(os.path.join('db', 'parkings_statuses.csv'), 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=res.keys())
            now = datetime.now(ZoneInfo("Asia/Jerusalem"))
            writer.writerow({'datetime': now.strftime("%Y-%m-%d %H:%M:%S.%f"), 'parking_id': id, 'parking_name': name, 'parking_address': addr, 'parking_status': status})

def main():
    res = {'datetime': None, 'parking_id': None, 'parking_name': None, 'parking_address': None, 'parking_status': None}
    # with open('parkings_statuses.csv', 'w', newline='', encoding='utf-8') as f:
    #     writer = csv.DictWriter(f, fieldnames=res.keys())
    #     writer.writeheader()

    for id in [42, 94, 45]:
        write_parking_status(id, res)


if __name__ == '__main__':
    prev = datetime.now()
    main()
    while True:
        time.sleep(10)
        if (datetime.now() - prev).total_seconds() > 5*60:
            prev = datetime.now()
            main()