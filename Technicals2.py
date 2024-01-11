# Otimização de portifólio e alocação de ativos
import yfinance as yf
import pandas as pd
import math
import seaborn as sns
import matplotlib.pyplot as plt


acoes = ['KO', 'AAPL', 'META', 'TOTS3.SA', 'ITUB4.SA', 'BBDC4.SA']

acoes_df = pd.DataFrame()
for acao in acoes:
    acoes_df[acao] = yf.download(acao, start='2017-01-01')['Adj Close']
acoes_df.dropna(inplace=True)
acoes_df2 = acoes_df.copy()
acoes_df2 = acoes_df2.to_csv('acoes.csv')
acoes_df2 = pd.read_csv('acoes.csv', index_col='Date', parse_dates=True)

# Normalizando os dados das acoes_df
acoes_df_norm = acoes_df / acoes_df.iloc[0]

#print(acoes_df_norm.tail())

taxas_retorno = acoes_df.copy()
taxas_retorno = (taxas_retorno / taxas_retorno.shift(1) -1)

print('taxas_retorno')
print(taxas_retorno)

print('desvio padrao')
print(taxas_retorno.std() * 100) # desvio padrao}")

print('desvio padrao anualizado')
print(taxas_retorno.std() * math.sqrt(246)) # desvio padrao anualizado

print('media anualizada')
print(taxas_retorno.mean() * 246) # media anualizada

print('correlacao entre as acoes')
print(taxas_retorno.corr()) # correlacao entre as acoes

print('covariancia entre as acoes')
print(taxas_retorno.cov()) # covariancia entre as acoes

plt.figure(figsize=(8,8))
sns.heatmap(taxas_retorno.corr(), annot=True, cmap='coolwarm')


