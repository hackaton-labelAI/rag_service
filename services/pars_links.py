import requests
from bs4 import BeautifulSoup


def parse_links(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Ошибка доступа к странице: {response.status_code}")
        return {}

    soup = BeautifulSoup(response.content, 'html.parser')
    sections_dict = {}
    section_elements = soup.find_all('a')

    for element in section_elements:
        text = element.get_text(strip=True)
        link = element.get('href')

        if text.startswith('Раздел') and link and text not in sections_dict:
            sections_dict[text] = 'https://company.rzd.ru/ru/9353/page/105104?id=1604' + link

        if len(sections_dict) >= 12:
            break

    return sections_dict


# url = 'https://company.rzd.ru/ru/9353/page/105104?id=1604#7275'
# links = parse_links(url)
#
# print(links)