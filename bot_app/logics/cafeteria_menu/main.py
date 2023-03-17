import os
import requests
import json
from datetime import date

from dotenv import load_dotenv
load_dotenv()

from bs4 import BeautifulSoup
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


TODAY = date.today()
TODAY_STR = str(TODAY).replace('-', '.')

url = 'https://www.kookmin.ac.kr/user/unLvlh/lvlhSpor/todayMenu/index.do'
channel_id = os.environ.get('CAFETERIA.CHANNEL_ID')
slack_bot_token = os.environ.get('SLACK_BOT_TOKEN')

client = WebClient(slack_bot_token)

if __name__ == '__main__':
    response = requests.get(url)

    contents = ['*<오늘의 밥>*', '=' * 100]

    if response.status_code != 200:
        pass
    else:
        html = response.text
        soup: BeautifulSoup = BeautifulSoup(html, 'html.parser')
        cont_sections = soup.find_all('div', 'table_wrap scroll_table food_table')
        
        # K-Bob+ 제외
        for cont_section in cont_sections[:-1]:
            title = cont_section.find('caption').get_text()
            suffix_idx = title.find(' 메뉴 테이블')
            title = title[len('국민대학교 '):suffix_idx]

            contents.append(f"[{title}]")

            days = cont_section.find_all('th')[1:]
            for day_idx, day_str in enumerate(map(lambda x: x.get_text()[:-3], days)):
                if day_str == TODAY_STR:
                    break
            
            corner_trs = cont_section.find('tbody').find_all('tr')
            for corner_tr in corner_trs:
                corner_tds = corner_tr.find_all('td')
                corner_name = corner_tds[0].get_text()

                menu = corner_tds[day_idx].get_text().strip()
                if not menu or menu.startswith('※ 운영시간'):
                    continue
                else:
                    menu = menu.replace('\n', ' ')
                    menu = menu.replace('0원', '0원, ')
                    contents.append(f"- {corner_name}: {menu}")
            
            contents.append('-' * 100)
        
        message = '\n'.join(contents)

        try:
            result = client.chat_postMessage(channel=channel_id, text=message, parse='mrkdwn')
        except SlackApiError as e:
            print(f"Error: {e}")