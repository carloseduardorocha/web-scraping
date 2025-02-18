from playwright.sync_api import sync_playwright
import os
import csv
from dotenv import load_dotenv

load_dotenv()
url_site = os.getenv("URL_SITE")

def save_csv(data):
    try:
        os.makedirs('results', exist_ok=True)

        with open('results/products.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Name", "Image", "Link", "Category"])
            
            for item in data:
                writer.writerow([item["name"], item["image"], item["link"], item["category"]])
    except Exception as e:
        print(f"Error saving CSV: {e}")

def accept_cookies(page):
    try:
        page.locator('.banner-container .buttons-content button span:text("Permitir Todos")').click()
    except Exception as e:
        print(f"Error accepting cookies: {e}")

def get_data(page):
    data = []
    
    try:
        accept_cookies(page)

        page.wait_for_selector('.nav__item-products > .nav__link')
        page.click('.nav__item-products > .nav__link')

        page.wait_for_load_state('networkidle')

        categories          = page.locator('.section-all-products h2.t-heading').all()
        products_containers = page.locator('.section-all-products .products').all()

        for index, category_element in enumerate(categories):
            category_name = category_element.inner_text().strip()
            products      = products_containers[index].locator('.product').all()

            for product in products:
                name  = product.locator('.product__title').inner_text().strip()
                image = product.locator('.product__img').get_attribute('src')
                link  = product.locator('.u-link-absolute').get_attribute('href')

                data.append({
                    "name": name,
                    "image": url_site + image,
                    "link": link,
                    "category": category_name
                })

        return data
    except Exception as e:
        print(f"Error extracting data: {e}")
        return []

def main():
    if not url_site:
        print("Error: URL_SITE not configured in the .env file.")
        return
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            page = browser.new_page()
            page.goto(url_site)

            data = get_data(page)
            save_csv(data)

            browser.close()
    except Exception as e:
        print(f"Error during the process: {e}")

if __name__ == "__main__":
    main()
