import bs4
import requests
import re
import pandas as pd
from datetime import date
import time

today = date.today()
today = today.strftime("%d%m%Y")
print(today)
area = "bermondsey"  # Search area
area = area.replace(" ", "-") # If there's space in the name, replaced with "-"
print(area)
radius = 1  # Miles. Options are 1/4, 1/2, 1, 3, 5, 10, 15, 20, 30, and 40
page_number = [2, 3, 4]  # we are only gettign search results from page 1, 2, 3, and 4

# --------------------------BS4 to scrap data -------------------#

first_page_url = f"https://www.zoopla.co.uk/for-sale/property/{area}/?page_size=500&view_type=list&q=Bermondsey%2C%20London&radius={radius}&results_sort=newest_listings&search_source=refine"


def grab_data_from_zoopla(url, page_number):
    response = requests.get(url)

    soup = bs4.BeautifulSoup(response.text, "html.parser")

    # Grab prices
    price_divs = soup.select("div[data-testid='listing-price'] p")

    # inside the div there are sometimes more than one p. E.g. <p>guide pirce</p> <p>£xxx,xxx</p>. Only keep prices.
    prices = []
    for price_div in price_divs:
        price = price_div.find(string=re.compile("^£|POA"))  # sometimes price is POA
        if price != None:
            prices.append(price)

    # Grab addresses
    address_ps = soup.select("p[data-testid='listing-description']")
    addresses = [address_p.get_text() for address_p in address_ps]

    # Grab sizes
    sizes_h2s = soup.select("h2[data-testid='listing-title']")
    sizes = [sizes_h2.get_text() for sizes_h2 in sizes_h2s]

    # Grab urls
    url_tags = soup.select("a[data-testid='listing-details-link']")
    urls = [f"zoopla.co.uk/{url_tag['href']}" for url_tag in url_tags]

    # check lens are all the same
    print(len(prices), len(addresses), len(sizes), len(urls))

    data = {}
    data = {"price": prices, "address": addresses, "size": sizes, "url": urls}

    # There are many other ways to make the dictionary
    # version 1
    # for i, (price, address, size) in enumerate(zip(prices, addresses, sizes)):
    #     data[i] = [price, address, size]

    # or version 2
    # data["price"] = prices
    # data["address"] = addresses
    # data["size"] = sizes
    # data["url"] = urls
    # print(data)

    df = pd.DataFrame.from_dict(data)
    df["page_number"] = page_number
    return df

# grabs data from first page
df = grab_data_from_zoopla(url=first_page_url, page_number=1)

# grabs data from other pages
for page in page_number:
    other_page_url = f"https://www.zoopla.co.uk/for-sale/property/{area}/?page_size=500&q=Bermondsey%2C%20London&radius={radius}&results_sort=newest_listings&search_source=refine&pn={page}"
    df_otherpage = grab_data_from_zoopla(url=other_page_url, page_number=page)
    df = pd.concat([df, df_otherpage])

df.to_excel(f"{area}_{today}.xlsx", index=False)

