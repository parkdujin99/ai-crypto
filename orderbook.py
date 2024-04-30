
import time
import requests
import pandas as pd

# CSV 파일 헤더
CSV_HEADER = 'price│quantity│type│timestamp\n'

while True:
    # 빗썸 API로부터 BTC 오더북 데이터 가져오기
    btc_response = requests.get('https://api.bithumb.com/public/orderbook/BTC_KRW/?count=5')
    btc_book = btc_response.json()
    btc_data = btc_book['data']
    btc_bids = pd.DataFrame(btc_data['bids']).apply(pd.to_numeric)
    btc_asks = pd.DataFrame(btc_data['asks']).apply(pd.to_numeric)
    btc_bids['type'] = 0
    btc_asks['type'] = 1

    # 빗썸 API로부터 ETH 오더북 데이터 가져오기
    eth_response = requests.get('https://api.bithumb.com/public/orderbook/ETH_KRW/?count=5')
    eth_book = eth_response.json()
    eth_data = eth_book['data']
    eth_bids = pd.DataFrame(eth_data['bids']).apply(pd.to_numeric)
    eth_asks = pd.DataFrame(eth_data['asks']).apply(pd.to_numeric)
    eth_bids['type'] = 0
    eth_asks['type'] = 1

    # BTC 오더북 데이터를 CSV 파일에 저장
    btc_df = pd.concat([btc_bids, btc_asks], ignore_index=True)
    btc_df['timestamp'] = pd.Timestamp.now()
    btc_df = btc_df[['price', 'quantity', 'type', 'timestamp']]  # 헤더 순서 지정
    btc_df.to_csv("./book-2024-04-29-bithumb-btc.csv", index=False, header=False, mode='a', sep='│', encoding='utf-8-sig')

    # ETH 오더북 데이터를 CSV 파일에 저장
    eth_df = pd.concat([eth_bids, eth_asks], ignore_index=True)
    eth_df['timestamp'] = pd.Timestamp.now()
    eth_df = eth_df[['price', 'quantity', 'type', 'timestamp']]  # 헤더 순서 지정
    eth_df.to_csv("./book-2024-04-29-bithumb-eth.csv", index=False, header=False, mode='a', sep='│', encoding='utf-8-sig')

    # 4.9초간 대기
    time.sleep(4.9)
