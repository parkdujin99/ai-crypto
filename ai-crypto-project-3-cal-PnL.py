import pandas as pd
import numpy

# CSV파일을 데이터프레임으로 읽어오기.
trades = pd.read_csv('ai-crypto-project-3-live-btc-krw.csv')

# side를 buy/sell multiplier로 변환
trades['multiplier'] = trades['side'].apply(lambda x: -1 if x == 0 else 1)

# PnL계산
trades['pnl'] = trades['quantity'] * trades['multiplier'] * trades['price'] - trades['fee']

#처음 PnL설정하기(첫 거래의 PnL)
accumulated_pnl = trades.iloc[0]['pnl']

#결과 저장을 위한 데이터프레임 생성
output = pd.DataFrame(columns=['timestamp', 'quantity', 'price', 'fee', 'amount', 'side', 'pnl', 'accumulated_pnl'])


#각 행의 PnL을 계산하고 원래 feature들과 같이 저장
for index, row in trades.iterrows():
    if index == 0:
        output = output.append({'timestamp': row['timestamp'], 'quantity': row['quantity'], 'price': row['price'],
                                 'fee': row['fee'], 'amount': row['amount'], 'side': row['side'],
                                 'pnl': row['pnl'], 'accumulated_pnl': row['pnl']}, ignore_index=True)
    else:
        accumulated_pnl += row['pnl']
        output = output.append({'timestamp': row['timestamp'], 'quantity': row['quantity'], 'price': row['price'],
                                 'fee': row['fee'], 'amount': row['amount'], 'side': row['side'],
                                 'pnl': row['pnl'], 'accumulated_pnl': accumulated_pnl}, ignore_index=True)
        

output = output.append({'accumulated_pnl': accumulated_pnl}, ignore_index=True)

# 데이터 프레임을 csv파일로 저장
output.to_csv('ai-crypto-project-3-PnL.csv', index=False)

