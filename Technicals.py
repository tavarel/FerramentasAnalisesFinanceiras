import yfinance
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta



stock = yfinance.Ticker("AAPL")
ticker = 'AAPL'


def beta(stock, benchmark):
    stock = yfinance.Ticker(stock)
    benchmark = yfinance.Ticker(benchmark)
    # 5 years of data
    stock_data = stock.history(period="5y")
    benchmark_data = benchmark.history(period="5y")
    # Calculate returns
    stock_returns = stock_data["Close"].pct_change().dropna()
    benchmark_returns = benchmark_data["Close"].pct_change().dropna()
    # Calculate covariance of stock vs benchmark
    covariance = stock_returns.cov(benchmark_returns)
    # Calculate variance of benchmark
    variance = benchmark_returns.var()
    # Calculate beta
    beta = covariance / variance
    return beta

def print_52week_high_low(ticker):
    # Carrega dados para o último ano
    end_date = datetime.today()
    start_date = end_date - timedelta(weeks=52)
    data = yfinance.download(ticker, start=start_date, end=end_date, progress=False)

    # Encontra o 52 week high e low
    week_high = data['High'].max()
    week_low = data['Low'].min()

    # Encontra as datas correspondentes e formata
    high_date = data['High'].idxmax().strftime('%d/%m/%Y')
    low_date = data['Low'].idxmin().strftime('%d/%m/%Y')

    print(f"{ticker} - 52 Week High: {week_high:.2f} em {high_date}")
    print(f"{ticker} - 52 Week Low: {week_low:.2f} em {low_date}")


def print_current_price_and_moving_average(ticker):
    # Define o período para os últimos 50 dias
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)

    # Baixa os dados do ticker para o período especificado
    data = yfinance.download(ticker, start=start_date, end=end_date, progress=False)

    # Calcula a média móvel de fechamento para 50 dias
    moving_average = data['Close'].mean()

    # Obtém o preço de fechamento mais recente
    current_price = data['Close'].iloc[-1]

    # Imprime os valores com duas casas decimais
    print(f"{ticker} - Preço Atual: {current_price:.2f}")
    print(f"{ticker} - Media Movel de 365 Dias: {moving_average:.2f}")

def print_current_and_average_volume(ticker):
    # Define o período para os últimos 50 dias
    end_date = datetime.today()
    start_date = end_date - timedelta(days=50)

    # Baixa os dados do ticker para o período especificado
    data = yfinance.download(ticker, start=start_date, end=end_date, progress=False)

    # Calcula o volume médio
    average_volume = data['Volume'].mean()

    # Obtém o volume de negociação mais recente
    current_volume = data['Volume'].iloc[-1]

    # Imprime os valores
    print(f"{ticker} - Volume Atual: {current_volume}")
    print(f"{ticker} - Volume Medio (ultimos 50 dias): {average_volume:.0f}")
    

def plot_price_and_moving_average(ticker):
    # Carrega dados dos últimos 5 anos
    end_date = datetime.today()
    start_date = end_date - timedelta(weeks=5*52)
    data = yfinance.download(ticker, start=start_date, end=end_date, progress=False)

    # Calcula a média móvel
    moving_average = data['Close'].rolling(window=365).mean()

    # Plota o gráfico
    plt.figure(figsize=(12,6))
    plt.plot(data['Close'], label='Preço de Fechamento')
    plt.plot(moving_average, label='Média Móvel de 365 Dias', color='orange')
    plt.title(f'Preço de Fechamento e Média Móvel de {ticker}')
    plt.xlabel('Data')
    plt.ylabel('Preço')
    plt.legend()
    plt.show()

# Beta
print(f"Beta da acao e {beta("AAPL", "^GSPC"):.3f}")

# 52 Week High/Low
print_52week_high_low(ticker)

# Current Price and Moving Average
print_current_and_average_volume('AAPL')

# Plot 
plot_price_and_moving_average('AAPL')
