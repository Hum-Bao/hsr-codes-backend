import os
import gitpush
import requests
from bs4 import BeautifulSoup
import time
from dotenv import load_dotenv

PATH = os.path.dirname(os.path.abspath(__file__))
RAW_TXT = "codes_RAW.txt"
EXPIRED_TXT = "codes_EXP.txt"

codes_set = set()
expired_set = set()
load_dotenv()


def get_website_html():
    # URLs to check for codes
    url_dict = {
        "prydwen": "https://www.prydwen.gg/star-rail/",
        "gamesradar": "https://www.gamesradar.com/honkai-star-rail-codes-redeem/",
        "game8": "https://game8.co/games/Honkai-Star-Rail/archives/410296",
        "pcgamer": "https://www.pcgamer.com/honkai-star-rail-codes/",
        "eurogamer": "https://www.eurogamer.net/honkai-star-rail-codes-livestream-active-working-how-to-redeem-9321",
        "fandom": "https://honkai-star-rail.fandom.com/wiki/Redemption_Code",
    }

    requests_dict = {}
    for key, value in url_dict.items():
        requests_dict[key] = BeautifulSoup(requests.get(value).content, "html.parser")
    return requests_dict


def retrieve_codes():
    requests_dict = get_website_html()

    for key, value in requests_dict.items():
        match key:
            case "prydwen":
                codes = value.find_all("p", class_="code")
                for code in codes:
                    code_text = code.text
                    if code_text.find("NEW!") != -1:
                        code_text = code_text.replace("NEW!", "").strip()
                    codes_set.add(code_text)
            case "gamesradar":
                strong_tags = value.find_all("strong")
                for code_text in strong_tags:
                    if " " not in code_text.text and code_text.text != "":
                        codes_set.add(code_text.text)
            case "game8":
                code_list = value.find("ul", class_="a-list")
                for code_text in code_list.find_all("a", class_="a-link"):
                    if "Credit" not in code_text.text and " " not in code_text.text:
                        codes_set.add(code_text.text)
            case "pcgamer":
                # Remove all del tags as pcgamer uses <strong> tags inside of <del> tags,
                # making a simple <strong> search impossible
                del_tags = value.find_all("del")
                for tag in del_tags:
                    tag.decompose()

                strong_tags = value.find_all("strong")
                for tag in strong_tags:
                    code_text = tag.text.strip()
                    if code_text.isupper() and len(code_text) > 5:
                        codes_set.add(code_text)
            case "eurogamer":
                strong_list = value.find_all("strong")
                for code_text in strong_list:
                    if " " not in code_text.text and code_text.text.isupper():
                        codes_set.add(code_text.text)
            case "fandom":
                # Remove expired codes
                old_codes = value.find_all("td", class_="bg-old")
                for old_code in old_codes:
                    old_code.parent.decompose()

                codes = value.find_all("code")
                for code_text in codes:
                    codes_set.add(code_text.text.upper())
            case _:
                return


def main():
    global expired_set
    expired_set = set(line.strip() for line in open(PATH + "/" + EXPIRED_TXT))
    retrieve_codes()
    remove_expired()
    verify_codes()
    remove_expired()
    write_codes()
    write_expired()
    gitpush.push(PATH, RAW_TXT)


def verify_codes():
    base_url = (
        "https://sg-hkrpg-api.hoyoverse.com/common/apicdkey/api/webExchangeCdkey?"
    )

    lang = "en"
    game_biz = "hkrpg_global"
    region = "prod_official_usa"
    url = (
        base_url
        + "lang="
        + lang
        + "&game_biz="
        + game_biz
        + "&uid="
        + os.getenv("uid", "")
        + "&region="
        + region
        + "&cdkey="
    )

    cookies = {
        "token": "account_mid_v2="
        + os.getenv("account_mid_v2", "")
        + "; "
        + "account_id_v2="
        + os.getenv("account_id_v2", "")
        + "; "
        + "cookie_token_v2="
        + os.getenv("cookie_token_v2", "")
    }

    # {'retcode': 0, 'message': 'OK', 'data': {'msg': 'Redeemed successfully'}}
    # {'data': None, 'message': 'Redemption code expired.', 'retcode': -2001}
    # {"data": None, "message": "Redemption code has already been used", "retcode": -2018}
    # {'data': None, 'message': 'Redemption code has already been used', 'retcode': -2017}

    for code in codes_set:
        get_request = requests.get((url + code), cookies=cookies)
        if (
            "OK" not in get_request.text
            and "-2018" not in get_request.text
            and "-2017" not in get_request.text
        ):
            print("EXPIRED: " + code)
            print(get_request.text)
            expired_set.add(code)
        else:
            print("VALID: " + code)
            print(get_request.text)
        time.sleep(20)
    return


def remove_expired():
    global codes_set
    codes_set.difference_update(expired_set)
    return


def write_expired():
    f = open(PATH + "/" + EXPIRED_TXT, "w", encoding="utf-8")
    for exp in expired_set:
        f.write(exp + "\n")
    f.truncate(f.tell() - len(os.linesep))
    f.close()
    return


def write_codes():
    f = open(PATH + "/" + RAW_TXT, "w", encoding="utf-8")
    # Sort codes to allow for consistent ordering when pushing to GitHub
    for code in sorted(codes_set):
        f.write(code + "\n")
    f.truncate(f.tell() - len(os.linesep))
    f.close()
    return


main()
