import streamlit as st 
import pandas as pd 
import base64
import matplotlib.pyplot as plt 
import yfinance as yf 

st.title('S&P 500 App')

st.markdown("""
	This app retrieves the list of **S&P 500 ** companies from Wikipedia and its corresponding stock closing price.
	* **Python libraries used:** streamlit, pandas, base64, matplotlib, yfinance
	* **Data Source:** [Wikipedia](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies).
	""")

st.sidebar.header('User Input Features')

# Web scraping of S&P 500 data
@st.cache
def load_data():
	url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
	html = pd.read_html(url, header = 0)
	df = html[0]
	return df

df = load_data()
sector = df.groupby('GICS Sector')

# Sidebar - user selects sector
sorted_sector_unique = sorted( df['GICS Sector'].unique() )
selected_sector = st.sidebar.multiselect('Sectors', sorted_sector_unique, sorted_sector_unique)

# Filter data for sectors that are selected by user
df_selected_sector = df[ (df['GICS Sector'].isin(selected_sector)) ]

st.header('List of Companies in Selected Sectors')
st.write('Data Dimension: ' + str(df_selected_sector.shape[0]) + ' rows and ' + str(df_selected_sector.shape[1]) + ' columns.')
st.dataframe(df_selected_sector)

# Download S&P 500 data
def filedownload(df):
	csv = df.to_csv(index=False)
	b64 = base64.b64encode(csv.encode()).decode() 
	href = f'<a href="data:file/csv;base64,{b64}" download="SP500.csv">Download CSV File</a>'
	return href

st.markdown(filedownload(df_selected_sector), unsafe_allow_html=True)

data = yf.download(
		tickers = list(df_selected_sector[:10].Symbol),
		period = "ytd",
		interval = "1d",
		group_by = "ticker",
		auto_adjust = True,
		prepost = True,
		threads = True,
		proxy = None
	)

# Plot closing price of each company that was selected
def price_plot(symbol):
	df = pd.DataFrame(data[symbol].Close)
	df['Date'] = df.index
	plt.fill_between(df.Date, df.Close, color='skyblue', alpha=0.3)
	plt.plot(df.Date, df.Close, color='skyblue', alpha=0.8)
	plt.xticks(rotation=90)
	plt.title(symbol, fontweight='bold')
	plt.xlabel('Date', fontweight='bold')
	plt.ylabel('Closing Price', fontweight='bold')
	st.set_option('deprecation.showPyplotGlobalUse', False)
	return st.pyplot()


number_company = st.sidebar.slider('Number of Companies', 1, 5)

st.header('Stock Closing Price')
for i in list(df_selected_sector.Symbol)[:number_company]:
	price_plot(i)
