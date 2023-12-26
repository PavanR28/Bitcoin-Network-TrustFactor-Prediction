import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm

BASE_URL = 'https://www.bitcoin-otc.com/'

def get_soup(url):
    page = requests.get(url)
    return BeautifulSoup(page.text, 'lxml')

def extract_table_headers(table):
    return [th.text for th in table.find_all("th")]

def extract_inner_table_headers(inner_table):
    return [th.text for th in inner_table.find_all("th")]

def extract_table_data(table, headers, data_frame):
    for row in tqdm(table.find_all("tr")[1:]):
        row_data = [td.text for td in row.find_all("td")]
        inner_url = BASE_URL + row.find_all("td")[1].a['href']
        inner_table = get_soup(inner_url).find("table", {"class": "datadisplay sortable"})
        for inner_row in inner_table.find_all("tr")[1:]:
            inner_row_data = [td.text for td in inner_row.find_all("td")]
            data_frame = data_frame.append(dict(zip(headers + extract_inner_table_headers(inner_table), row_data + inner_row_data)), ignore_index=True)
    return data_frame

url = BASE_URL + 'viewratings.php'
soup = get_soup(url)
table1 = soup.find("table", {"class": "datadisplay sortable"})

headers = extract_table_headers(table1)
print(headers)

node_data = pd.DataFrame(columns=headers)
network_data = pd.DataFrame()

for row in tqdm(table1.find_all("tr")[1:]):
    row_data = [td.text for td in row.find_all("td")]
    inner_url = BASE_URL + row.find_all("td")[1].a['href']
    inner_table = get_soup(inner_url).find("table", {"class": "datadisplay sortable"})
    network_data = extract_table_data(inner_table, headers, network_data)
    node_data = node_data.append(dict(zip(headers, row_data)), ignore_index=True)

print(node_data.head(5))
print()
print(network_data.head(5))

node_data.to_csv("nodes.csv", index=False)
network_data.to_csv("network.csv", index=False)
