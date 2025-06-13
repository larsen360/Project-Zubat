pip install -r requirements.txt
import time
import os

URL = 'https://www.pokemoncenter.com/category/trading-card-game/elite-trainer-boxes'
HEADERS = {
    'User-Agent': 'Mozilla/5.0'
}

SEEN_FILE = 'seen_products.txt'

# Indlæs tidligere set produkter fra fil
def load_seen_products():
    if not os.path.exists(SEEN_FILE):
        return set()
    with open(SEEN_FILE, 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f if line.strip())

# Gem nyt produkt til fil
def save_seen_product(name):
    with open(SEEN_FILE, 'a', encoding='utf-8') as f:
        f.write(name + '\n')

# Start med at læse den tidligere historik
seen_products = load_seen_products()

def check_for_new_etb():
    response = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')

    products = soup.find_all('a', class_='product-card-title')

    found_new = False
    for product in products:
        name = product.get_text().strip()
        if 'Elite Trainer Box' in name and 'Pokemon Center' in name:
            if name not in seen_products:
                print(f"NY: {name}")
                print(f"Link: https://www.pokemoncenter.com{product['href']}")
                seen_products.add(name)
                save_seen_product(name)
                found_new = True

    if not found_new:
        print("Ingen nye ETB'er fundet.")

if __name__ == '__main__':
    while True:
        check_for_new_etb()
        time.sleep(60 * 5)  # Tjek hvert 5. minut