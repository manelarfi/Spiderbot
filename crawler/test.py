from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=options)
driver.get("https://quotes.toscrape.com/js/")
time.sleep(3)  # Give JS time to render

print(driver.page_source[:1000])  # Print part of the HTML
driver.quit()
