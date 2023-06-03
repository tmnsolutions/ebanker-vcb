from bs4 import BeautifulSoup
import csv
from dotenv import dotenv_values

config = dotenv_values(".env")
savePath = config["SAVE_PATH"] if "SAVE_PATH" in config else "transactions.csv"
accountNo = config["ACCOUNT_NO"]

# delete old data
with open(savePath, "w", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["AccountNo", "TransactionDate", "RefNo", "Amount", "Description", "Type"])

# load html file
with open("page.html", "r") as f:
    html = f.read()
    soup = BeautifulSoup(html, "html.parser")
    trs = soup.css.select("#tbTranHis tbody > tr")

    #loop through trs in reversed order, so that the oldest transaction is at the bottom
    for tr in reversed(trs):
        # get td
        cells = tr.find_all("td")
        # get text of td at index 0
        transactionDate =  cells[0].get_text()
        refNo =  cells[1].get_text()
        debit =  cells[2].get_text() 
        credit =  cells[3].get_text() 
        description = cells[4].get_text()
        type = "Dr" if debit != "" else "Cr"
        amount = debit if debit != "" else credit
        amount = amount.replace(",", "").replace(" VND", "")
        
        # write to csv
        with open(savePath, "a", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([accountNo, transactionDate, refNo, amount, description, type])
