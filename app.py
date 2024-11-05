from flask import Flask,render_template,request,redirect, url_for, flash
import google.generativeai as genai
import os
import numpy as np
import textblob

from flask_mysqldb import MySQL
import yfinance as yf
import pandas as pd

model = genai.GenerativeModel("gemini-1.5-flash")
##api = os.getenv("MAKERSUITE")
api = 'AIzaSyB4mcXssvqksJlPhVaAkHBfCu-K76X0k1M'
genai.configure(api_key=api)

app = Flask(__name__)

@app.route("/",methods=["GET","POST"])
def index():
    return(render_template("index.html"))

@app.route("/prediction_DBS",methods=["GET","POST"])
def prediction_DBS():
    return(render_template("prediction_DBS.html"))

@app.route("/prediction_result_DBS",methods=["GET","POST"])
def prediction_result_DBS():
    q = float(request.form.get("q"))
    r = (-50.6 * q) + 90.2
    return(render_template("prediction_result_DBS.html",r=r))

@app.route("/predict_creditability",methods=["GET","POST"])
def predict_creditability():
    return(render_template("predict_creditability.html"))

@app.route("/predict_result_creditability",methods=["GET","POST"])
def predict_result_creditability():
    q = float(request.form.get("q"))
    r = (-9.34111523e-05 * q) + 1.15201551
    r = np.where(r>=0.5,"Creditable", "Not Creditable")
    return(render_template("predict_result_creditability.html",r=r))

@app.route("/sentiment_analysis",methods=["GET","POST"])
def sentiment_analysis():
    return(render_template("sentiment_analysis.html"))

@app.route("/sentiment_analysis_result",methods=["GET","POST"])
def sentiment_analysis_result():
    q = request.form.get("q")
    r = textblob.TextBlob(q).sentiment
    return(render_template("sentiment_analysis_result.html",r=r))

@app.route("/faq",methods=["GET","POST"])
def faq():
    return(render_template("faq.html"))

@app.route("/q1",methods=["GET","POST"])
def q1():
    r = model.generate_content("How should I diversify my investment portfolio?")
    return(render_template("q1_reply.html",r=r))

@app.route("/q2",methods=["GET","POST"])
def q2():
    q = request.form.get("q")
    r = model.generate_content(q)
    return(render_template("q2_reply.html",r=r))

@app.route("/shareprice",methods=["GET","POST"])
def shareprice():
    stock_codes = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",'D05.SI','NVDA'] 
    stock_prices_df = get_stock_prices(stock_codes)
    stock_data = stock_prices_df.to_dict(orient="records")  # Convert DataFrame to dictionary for Jinja template
    return render_template("stock_prices.html", stock_data=stock_data)

# Function to get stock prices
def get_stock_prices(stock_codes):
    stock_data = []
    for code in stock_codes:
        stock = yf.Ticker(code)
        stock_info = stock.history(period="1d")
        info = stock.info
        if not stock_info.empty:
            latest_price = stock_info["Close"].iloc[-1]
            longName = info.get("longName")
            stock_data.append({"Stock Code": code ,"Stock Name": longName,"Latest Price": latest_price})
        else:
            stock_data.append({"Stock Code": code, "Latest Price": "N/A"})
    
    return pd.DataFrame(stock_data)

@app.route("/stock_detail",methods=["GET","POST"])
def stock_query():
    stock_code = request.form.get("stock_code")
    financial_metrics = get_stock_metrics(stock_code)
    r = model.generate_content("current market sentiment for Apple stock price")
    return render_template("stock_detail.html", stock_code=stock_code, metrics=financial_metrics, Market_Analaysis=r )

@app.route("/stock/<stock_code>")
def stock_detail(stock_code):
    # Get key financial metrics for the stock
    financial_metrics = get_stock_metrics(stock_code)
    r = model.generate_content("current market sentiment for Apple stock price")
    return render_template("stock_detail.html", stock_code=stock_code, metrics=financial_metrics, Market_Analaysis=r )


# Function to get detailed financial metrics for a stock
def get_stock_metrics(stock_code):
    stock = yf.Ticker(stock_code)
    info = stock.info
    financial_metrics = {
        "Company": info.get("longName"),
        "Market Price": info.get("regularMarketPrice"),
        "Market Cap": info.get("marketCap"),
        "PE Ratio": info.get("trailingPE"),
        "EPS": info.get("trailingEps"),
        "Dividend Yield": info.get("dividendYield"),
        "Revenue": info.get("totalRevenue"),
        "Gross Profit": info.get("grossProfits"),
        "Net Income": info.get("netIncomeToCommon"),
        "Free Cash Flow": info.get("freeCashflow"),
        "52 Week High": info.get("fiftyTwoWeekHigh"),
        "52 Week Low": info.get("fiftyTwoWeekLow"),
    }
    return financial_metrics

@app.route("/stockquery",methods=["GET","POST"])
def stockquery():
    return(render_template("stock_query.html"))


if __name__ == "__main__":
    app.run()
