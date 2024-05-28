import pandas as pd
import numpy as np
import math
from datetime import datetime, timedelta

# CSV 파일의 경로 설정
file_path = '/home/djpark/2024-05-01-upbit-BTC-book.csv'

# CSV 파일 읽기
df = pd.read_csv(file_path)

# 매초마다 오더북 데이터이므로 타임스탬프를 기준으로 그룹화
df['timestamp'] = pd.to_datetime(df['timestamp'])
df.set_index('timestamp', inplace=True)

# 필요한 컬럼만 남기기
df = df[['price', 'quantity', 'type']]

# 특정 시간 범위 설정 (0:00 ~ 3:00)
start_time = pd.Timestamp('2024-05-01 00:00:00')
end_time = pd.Timestamp('2024-05-01 03:00:00')
df = df.loc[start_time:end_time]

# 그룹화하여 각 초별로 데이터 처리
grouped = df.groupby(df.index)

# 결과를 저장할 리스트
results = []

# 실행 중 메시지 표시
print("Program running...")

# 초기 변수 설정
ratio = 0.1
level = 10
interval = 1
decay = math.exp(-1.0/interval)

prevBidQty = 0
prevAskQty = 0
prevBidTop = 0
prevAskTop = 0
bidSideAdd = 0
bidSideDelete = 0
askSideAdd = 0
askSideDelete = 0
bidSideTrade = 0
askSideTrade = 0
bidSideFlip = 0
askSideFlip = 0
bidSideCount = 0
askSideCount = 0

for timestamp, group in grouped:
    # 매수(bid)와 매도(ask) 분리
    bids = group[group['type'] == 0]
    asks = group[group['type'] == 1]

    # 총 매수와 매도 양 계산
    total_bids = bids['quantity'].sum()
    total_asks = asks['quantity'].sum()

    # 최상위 매수와 매도 가격 계산 (빈 경우 대비)
    best_bid = bids['price'].max() if not bids.empty else None
    best_bid_q = bids['quantity'].max() if not bids.empty else None # top level bid의 수량
    best_ask = asks['price'].min() if not asks.empty else None
    best_ask_q = asks['quantity'].min() if not asks.empty else None # top level ask의 수량

    # 중간 가격 계산(mkt버전)
    if best_bid is not None and best_ask is not None:
        mid_price = ((best_bid*best_ask_q) + (best_ask*best_bid_q))/(best_bid_q + best_ask_q)
    else:
        mid_price = None

    # book-delta 계산
    if mid_price is not None:
        if total_bids > prevBidQty:
            bidSideAdd += 1
            bidSideCount += 1
        if total_bids < prevBidQty:
            bidSideDelete += 1
            bidSideCount += 1
        if total_asks > prevAskQty:
            askSideAdd += 1
            askSideCount += 1
        if total_asks < prevAskQty:
            askSideDelete += 1
            askSideCount += 1

        if best_bid < prevBidTop:
            bidSideFlip += 1
            bidSideCount += 1
        if best_ask > prevAskTop:
            askSideFlip += 1
            askSideCount += 1

        if bidSideCount == 0:
            bidSideCount = 1
        if askSideCount == 0:
            askSideCount = 1

        bidBookV = (-bidSideDelete + bidSideAdd - bidSideFlip) / (bidSideCount**ratio)
        askBookV = (askSideDelete - askSideAdd + askSideFlip) / (askSideCount**ratio)
        tradeV = (askSideTrade / askSideCount**ratio) - (bidSideTrade / bidSideCount**ratio)
        book_delta = askBookV + bidBookV + tradeV

        bidSideCount = int(bidSideCount * decay)  # exponential decay
        askSideCount = int(askSideCount * decay)
        bidSideAdd = int(bidSideAdd * decay)
        bidSideDelete = int(bidSideDelete * decay)
        askSideAdd = int(askSideAdd * decay)
        askSideDelete = int(askSideDelete * decay)
        bidSideTrade = int(bidSideTrade * decay)
        askSideTrade = int(askSideTrade * decay)
        bidSideFlip = int(bidSideFlip * decay)
        askSideFlip = int(askSideFlip * decay)

        prevBidQty = total_bids
        prevAskQty = total_asks
        prevBidTop = best_bid
        prevAskTop = best_ask

    # book-imbalance 계산
    if total_bids > 0 and total_asks > 0:
        quant_v_bid = bids['quantity'] ** ratio
        price_v_bid = bids['price'] * quant_v_bid
        quant_v_ask = asks['quantity'] ** ratio
        price_v_ask = asks['price'] * quant_v_ask

        askQty = quant_v_ask.sum()
        bidPx = price_v_bid.sum()
        bidQty = quant_v_bid.sum()
        askPx = price_v_ask.sum()

        book_price = ((askQty * bidPx) / bidQty) + ((bidQty * askPx) / askQty)
        book_price /= (bidQty + askQty)

        book_imbalance = (book_price - mid_price) / interval

    # 결과 저장
    results.append({
        'timestamp': timestamp,
        'mid_price': mid_price,
        'book-imbalance-0.1-10-1': book_imbalance if 'book_imbalance' in locals() else None,
        'book-delta-v1-0.1-10-1': book_delta if 'book_delta' in locals() else None,
        
      
    })

# 결과 데이터프레임 생성
results_df = pd.DataFrame(results)

# CSV 파일로 저장
results_df.to_csv('2024-05-01-upbit-BTC-feature.csv', index=False)

# 완료 메시지 표시
print("Done!")