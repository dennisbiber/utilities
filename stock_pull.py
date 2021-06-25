import yfinance as yf
from datetime import date, timedelta
import yaml


def getTickerData(tickerSymbol, stock):
	tickerData = yf.Ticker(tickerSymbol)
	tickerDf = tickerData.history(period="max")
	print("")
	print(stock)
	print(tickerDf)
	print(tickerData.dividends)

def getConfig(file):
	print(file)
	return file


def main():
	config_path = "ticker_config.yaml"
	with open(config_path, "r") as file:
		config = yaml.load(file, Loader=yaml.FullLoader)
	for stock in config["stock_config"]:
		tickerSymbol = config["stock_config"][stock]["ticker_symbol"]
		getTickerData(tickerSymbol, stock)


if __name__ == "__main__":
	main()