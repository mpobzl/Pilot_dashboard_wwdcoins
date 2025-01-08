import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from pandas.tseries.offsets import MonthEnd

# Função para baixar dados de câmbio
def download_currency_data(tickers, start_date, end_date):
    data = []
    columns = []
    for ticker in tickers:
        currency_data = yf.download(ticker, start=start_date, end=end_date)
        if not currency_data.empty:
            data.append(currency_data['Close'])
            columns.append(ticker)
    if data:
        return pd.concat(data, axis=1, keys=columns)
    else:
        raise ValueError("Nenhum dado foi baixado.")

# Configuração inicial
ticker_labels = {
    'USDBRL=X': 'Real (BRL)',
    'USDARS=X': 'Peso Argentino (ARS)',
    'USDMXN=X': 'Peso Mexicano (MXN)',
    'USDCNY=X': 'Yuan Chinês (CNY)',
    'USDINR=X': 'Rúpia Indiana (INR)',
}
tickers = list(ticker_labels.keys())

# Interface do Streamlit
st.title("Dashboard de Moedas Emergentes")
st.markdown("Análise das moedas de países emergentes (Brasil, Argentina, México, Índia e China)")

# Botões de seleção de período
period_option = st.selectbox(
    "Selecione o horizonte do período a ser analisado:",
    ["1 ano", "3 anos", "5 anos", "Desde 2019"]
)

# Mapear a seleção para datas
if period_option == "1 ano":
    start_date = '2023-01-01'
elif period_option == "3 anos":
    start_date = '2021-01-01'
elif period_option == "5 anos":
    start_date = '2019-01-01'
else:
    start_date = '2019-01-01'

end_date = pd.Timestamp.today().strftime('%Y-%m-%d')  # Atualiza até hoje

# Caixa de seleção para moedas
selected_currencies = st.multiselect(
    "Selecione as moedas para análise:",
    options=list(ticker_labels.values()),
    default=list(ticker_labels.values())  # Seleciona todas por padrão
)

# Filtrar tickers selecionados
selected_tickers = [ticker for ticker, label in ticker_labels.items() if label in selected_currencies]

# Baixar os dados
currency_data = download_currency_data(selected_tickers, start_date, end_date)
currency_data.columns = [ticker_labels[ticker] for ticker in selected_tickers]

# Calcular valores mensais médios
monthly_data = currency_data.resample(MonthEnd()).mean()

# Data mais recente
last_date = currency_data.index.max().strftime('%Y-%m-%d')

# Gráfico de Linha com Eixo Secundário para Peso Argentino
st.subheader("Gráfico de Linha: Valores Mensais Médios")
fig1, ax1 = plt.subplots(figsize=(12, 6))

for column in monthly_data.columns:
    if column != 'Peso Argentino (ARS)':
        ax1.plot(monthly_data.index, monthly_data[column], label=column)
    else:
        # Criar eixo secundário para o Peso Argentino
        ax2 = ax1.twinx()
        ax2.plot(monthly_data.index, monthly_data[column], color='orange', label='Peso Argentino (ARS)')
        ax2.set_ylabel("Taxa de Câmbio (ARS)")
        ax2.legend(loc="upper right")

ax1.set_xlabel("Data")
ax1.set_ylabel("Taxa de Câmbio (Outras Moedas)")
ax1.legend(loc="upper left")
ax1.grid()

# Adicionar data de atualização no rodapé
plt.figtext(0.5, -0.1, f"Dados atualizados em: {last_date}", ha="center", fontsize=10)

st.pyplot(fig1)

# Calcular variação YTD
ytd_data = currency_data.loc['2024-01-01':end_date]
ytd_variation = {}
for column in ytd_data.columns:
    start_value = ytd_data[column].iloc[0]
    end_value = ytd_data[column].iloc[-1]
    ytd_variation[column] = ((end_value - start_value) / start_value) * 100
ytd_df = pd.DataFrame.from_dict(ytd_variation, orient='index', columns=['Variação YTD (%)'])

# Gráfico de Barras
st.subheader("Gráfico de Barras: Variação Acumulada YTD 2024")
fig2, ax2 = plt.subplots(figsize=(10, 6))
ytd_df.plot(kind='bar', ax=ax2, color='skyblue', legend=False)
ax2.set_title("Variação Acumulada YTD 2024")
ax2.set_ylabel("Variação (%)")
ax2.set_xlabel("Moeda")
for container in ax2.containers:
    ax2.bar_label(container, fmt="%.2f%%", label_type="edge", fontsize=10, padding=3)
ax2.grid(axis='y', linestyle='--', alpha=0.7)

# Adicionar data de atualização no rodapé
plt.figtext(0.5, -0.1, f"Dados atualizados em: {last_date}", ha="center", fontsize=10)

st.pyplot(fig2)
