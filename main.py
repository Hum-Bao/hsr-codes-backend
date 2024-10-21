import requests
import json
import os
import gitpush
from bs4 import BeautifulSoup

URL = "https://www.prydwen.gg/star-rail/"
PATH = os.path.dirname(os.path.abspath(__file__))
RAW_TXT = "codes_RAW.txt"
JSON_TXT = "codes_JSON.json"

def main():
    request = requests.get(URL)
    soup = BeautifulSoup(request.content, 'html.parser')
    raw_text(soup)
    json_format(soup)
    gitpush.push(PATH, RAW_TXT, JSON_TXT)


def raw_text(soup):
    codes = soup.find_all('p', class_='code')
    f = open(PATH + "/" + RAW_TXT, "w", encoding="utf-8")
    for s in codes:
        temp = s.text
        if temp.find("NEW!") != -1:
            temp = temp.replace("NEW!", "").strip()
        if(s == codes[-1]):
            f.write(temp)
        else:
            f.write(temp + "\n")
        
def json_format(soup):
    codes = soup.find('div', class_='codes')
    code_arr = codes.find_all('p', class_='code')
    date_arr = codes.find_all('p', class_='date')
    json_str = "{ \"gift codes\": ["
    for c, d in zip(code_arr, date_arr):
        json_str += "{\"code\": \"" + c.text.replace("NEW!", "") + "\","
        json_str += "\"date\": \"" + d.text.replace("Released on ", "") + "\"},"
    json_str = json_str[:-1]
    json_str += "]}"
    json_data = json.loads(json_str)
    with open(PATH + "/" + JSON_TXT, "w", encoding="utf-8") as f:
        json.dump(json_data,f, ensure_ascii=False, indent=4)

main()