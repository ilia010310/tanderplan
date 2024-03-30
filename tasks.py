from celery import Celery
import requests
import xmltodict
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

app = Celery('tasks')
app.conf.broker_url = 'redis://localhost:6379/0'
app.conf.update(
    broker_connection_retry_on_startup=True,
)


@app.task
def collect_links(url: str):
    page = requests.get(url, auth=('user', 'pass'))
    soup = BeautifulSoup(page.text, 'html.parser')
    base_url = 'https://zakupki.gov.ru/'
    containers_print = soup.find_all(class_="registry-entry__header")
    links_list = []

    for container in containers_print:
        links = container.find_all('a')

        link = links[1]
        if link:
            relative_url = link['href']
            absolute_url = urljoin(base_url, relative_url)
            links_list.append(absolute_url)
            collect_date_from_xml.delay(absolute_url)



@app.task
def collect_date_from_xml(link: str):
    xml_link = re.sub(r'\bview\b', 'viewXml', link)

    def find_value_by_tag(xml_dict, target_tag):
        '''Функция для нахождения значения
        определенного ключа(target_tag) любой вложенности'''

        if isinstance(xml_dict, dict):
            # Проверяем, есть ли у текущего словаря ключ, соответствующий целевому тегу
            if target_tag in xml_dict:
                return xml_dict[target_tag]
            # Если ключа нет, продолжаем поиск во всех значениях словаря
            for value in xml_dict.values():
                result = find_value_by_tag(value, target_tag)
                if result:
                    return result
        return

    headers = {
        'User-Agent': 'Mozilla/5.0',
    }
    response = requests.get(xml_link, auth=('user', 'pass'), headers=headers)

    if response.status_code == 200:
        xml_data = response.text

        xml_dict = xmltodict.parse(xml_data)
        date_and_time = find_value_by_tag(xml_dict, 'publishDTInEIS')
        print(link, '-', date_and_time)
    else:
        print(f"Ошибка при получении данных. Код состояния: {response.status_code}")
