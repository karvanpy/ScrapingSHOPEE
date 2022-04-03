import requests
import pandas as pd
from about import greetings
from datetime import datetime 
from tabulate import tabulate

class SHOPEEScraper:
    greetings()
    def __init__(self):
        self.keywords = None
        self.limit = 60
        pass

    def fetch(self, url_api):
        self.url = url_api

        self.params = {
            "by": "relevancy",
            "keyword": self.keywords,
            "limit": self.limit,
            "newest": 0,
            "order": "desc",
            "page_type": "search",
            "scenario": "PAGE_GLOBAL_SEARCH",
            "version": 2
        }

        self.headers = {
            'sec-ch-ua': '"(Not(A:Brand";v="8", "Chromium";v="99", "Google Chrome";v="99"',
            'sec-ch-ua-platform': "Linux",
            "referer": f"https://shopee.co.id/search?keyword={self.keywords}",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.35 Safari/537.36"
        }

        self.response = requests.get(self.url, params=self.params, headers=self.headers)

        return self.response

    def get_products(self, response):    
        # response = fetch_api(keyword, limit)

        self.items = response.json()["items"]
        self.products = []

        for order, item in enumerate(self.items):
            self.products.append({
                "product"       : self.items[order]["item_basic"]["name"],
                "seller"        : self.get_shop_info(self.items[order]["shopid"])["name"],
                "price"         : self.items[order]["item_basic"]["price"] / 100000,
                "sold"          : self.items[order]["item_basic"]["sold"],
                "stock"         : self.items[order]["item_basic"]["stock"],
                "shop_location" : self.items[order]["item_basic"]["shop_location"],
                "is_verified"   : self.items[order]["item_basic"]["shopee_verified"]
            })
            # print(f"[+][{order}] {items[order]}")

        try:
            self.show_results()
        except Exception as e:
            print(e)
        finally:
            print()
            print( "[~] Scraping finished!")
            print(f"[~] Total Products: {len(self.products)}")
            
        return self.products

    def get_shop_info(self, shop_id):
        self.seller_info = requests.get(f'https://shopee.co.id/api/v4/product/get_shop_info?shopid={shop_id}').json()["data"]
        return self.seller_info

    def save_to(self, file_format="csv"):
        print(f"There are {self.limit} items will save!")
        time_scrape = datetime.now().strftime("%m%d%Y_%H%M%S")

        df = pd.DataFrame(self.products)

        file_name = f"result_{self.keywords}_{time_scrape}"


        if file_format == "csv":
            file_name += ".csv"
            df.to_csv(file_name, index=False)
            print(f"[~] Result saved to '{file_name}'")
        elif file_format == "excel":
            file_name += ".xlsx"
            df.to_excel(file_name, index=False)
            print(f"[~] Result was saved to '{file_name}'")
    
    def show_results(self):
        df = pd.DataFrame(self.products)
        df.index += 1
        if self.products:
            print(df.head())
            print(df.tail())

def main():
    shp = SHOPEEScraper()
    url_api  = "https://shopee.co.id/api/v4/search/search_items"

    shp.keywords = input("[~] Keywords : ")
    print("-> Counting how much items has available ...")
    response = shp.fetch(url_api)
    products_available = response.json()["adjust"]["count"]
    print(f'-> Keywords "{shp.keywords}" has {products_available} products!')

    shp.limit    = input("[~] Total of product you want to scrape? : ")
    print("-> Start to scrape ...")
    response = shp.fetch(url_api)
    products = shp.get_products(response)
    
    try:
        ask =             input("[~] Do you want save the results? (y/n): ").lower()
        if ask == 'y':
            file_format = input("[~] File format? (csv/excel)           : ").lower()
            shp.save_to(file_format=file_format)
        elif ask == 'n':
            # shp.show_results()
            pass
    except Exception as e:
        print(e)
    finally:
        print("[~] Program Finished")
        
if __name__ == "__main__":
    main()