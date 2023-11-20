import time
import psycopg2
import requests
from bs4 import BeautifulSoup

# BASE_URL = "https://www.zonebourse.com/bourse/indices/"
# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
# }
#
# # Fetch the HTML content
# response = requests.get(BASE_URL, headers=headers)
# soup = BeautifulSoup(response.content, 'html.parser')
#
# # Extract the links from the targeted selector
# links = [a['href'] for a in soup.select("a.link.link--blue.table-child--middle.align-top")]
#
# # Print the extracted links
# for link in links:
#     print(link)
from bs4 import BeautifulSoup
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from test import insert_into_db


class ZoneBourseScraper:
    BASE_URL = "https://www.zonebourse.com/"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    def __init__(self, email, password):
        self.email = email
        self.password = password
        options = Options()
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def accept_cookies(self):
        try:
            cookies_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept')]")))
            cookies_button.click()
        except:
            pass

    def login(self):
        self.driver.get(self.BASE_URL)
        self.accept_cookies()

        connexion_button = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.d-none.d-sm-block.htLog')))
        connexion_button.click()

        email_field = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="login"]')))
        email_field.send_keys(self.email)

        password_field = self.driver.find_element(By.CSS_SELECTOR, 'input[name="password"]')
        password_field.send_keys(self.password)

        valider_button = self.driver.find_element(By.CSS_SELECTOR, 'input.hlSubmit[value="Valider"]')
        valider_button.click()

    def extract_indice_links(self):
        self.driver.get(self.BASE_URL + "bourse/indices/")
        self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.link.link--blue.table-child--middle.align-top")))
        return [a.get_attribute('href') for a in
                self.driver.find_elements(By.CSS_SELECTOR, "a.link.link--blue.table-child--middle.align-top")]

    def scrape_index_composition(self, link):
        self.driver.get(link + "composition/")
        time.sleep(10)

        last_length = 0
        while True:
            self.driver.execute_script("window.scrollBy(0, window.innerHeight);")
            time.sleep(3)
            component_links = [a.get_attribute('href') for a in self.driver.find_elements(By.CSS_SELECTOR,
                                                                                          'a.link.link--blue.table-child--middle.align-top')]
            if len(component_links) == last_length:
                break
            last_length = len(component_links)

        return component_links

    def get_page_content(self, url):
        response = requests.get(url, headers=self.HEADERS)
        return BeautifulSoup(response.content, 'html.parser')

    def scrape_details(self, component_url):
        soup = self.get_page_content(component_url)

        # Locate the elements based on the provided selector
        elements = soup.select('h2.m-0.badge.txt-b5.txt-s1')

        ticker, isin = None, None

        if elements:
            # Extract the ticker from the 0th element
            ticker = elements[0].text.strip() if len(elements) > 0 else None

            # Extract the ISIN from the 1st element
            isin = elements[1].text.strip() if len(elements) > 1 else None

        # Extract the name based on the HTML structure you provided
        name_element = soup.select_one('div.title.title__primary > a')
        if name_element:
            name = ''.join(name_element.stripped_strings)  # This will give you "LVMH"
        else:
            name = None

        return ticker, isin, name

    def insert_into_db(self,isin, name, ticker):
        # Ensure data is a list of tuples
        # Establish a database connection
        conn = psycopg2.connect(host="localhost", database="Neoma", user="postgres", password="Heigbaunhf22")
        cursor = conn.cursor()


        cursor.execute("SELECT * FROM stocks WHERE tickers=%s", (ticker,))

        if cursor.fetchone() is None:
            # Insert the new stock details into the database
            cursor.execute("INSERT INTO stocks (name, tickers, isin) VALUES (%s, %s, %s)", (name, ticker, isin))
            conn.commit()

        # Close the cursor and connection
        cursor.close()
        conn.close()

    def run(self):
        self.login()
        links = self.extract_indice_links()

        for link in links:
            component_links = self.scrape_index_composition(link)
            print(f"Extracted {len(component_links)} links for {link}")

            for component_link in component_links:
                ticker, isin, name = self.scrape_details(component_link)
                if isin:
                    print(f"Details for {component_link}: Ticker: {ticker}, ISIN: {isin}, Name: {name}")
                    self.insert_into_db(name, ticker, isin)  # Wrap the tuple in a list

        self.driver.quit()

if __name__ == "__main__":
    scraper = ZoneBourseScraper("Hugo.lemonnier02@gmail.com", "&qyHE#$fz$p2j+H")
    scraper.run()
