from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pytesseract
import time
import os
import datetime
from dotenv import dotenv_values

config = dotenv_values(".env")

accountNo = config["ACCOUNT_NO"]
username = config["USERNAME"]
password = config["PASSWORD"]

# first day of three months ago
today = datetime.date.today()
fromDate = (today - datetime.timedelta(days=60)).replace(day=1).strftime("%d/%m/%Y")
toDate = "" # today

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, slow_mo=50)
    page = browser.new_page()
    page.goto("https://www.vietcombank.com.vn/Ibanking20/")
    page.locator("#aspnetForm > div.form-row > div.col-5 > div > div.imageCapcha").screenshot(path="captcha.png")

    loginSuccess = False
    maxRetry = 5
    while maxRetry > 0:
        page.fill("#ctl00_Content_Login_TenTC", username)
        page.fill("#ctl00_Content_Login_MatKH", password)
        # wait for the captcha to reload
        time.sleep(1)
        page.locator("#aspnetForm > div.form-row > div.col-5 > div > div.imageCapcha").screenshot(path="captcha.png")
        captcha = pytesseract.image_to_string("captcha.png", config="-c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        # trim space and new line
        captcha = captcha.strip()
        print("Captcha solved: '" + captcha + "'")
        print("Captcha length: " + str(len(captcha)))
        if len(captcha) != 6:
            page.click("#ctl00_Content_Login_Captcha_Reload")
            print("Captcha is not 6 characters long. Retrying...")
            continue
        
        # check if first character is A-Z0-9
        if not captcha[0].isalnum():
            page.click("#ctl00_Content_Login_Captcha_Reload")
            print("Captcha first character is not alphanumeric. Retrying...")
            continue

        page.fill("#ctl00_Content_Login_ImgStr", captcha)
        page.click("#ctl00_Content_Login_LoginBtn")
        time.sleep(3)
        hasError = page.is_visible("#ctl00_Content_Login_CaptchaValidator")
        if not hasError:
            loginSuccess = True
            print("Login success")
            break
        maxRetry -= 1

    if not loginSuccess:
        print("Login failed")
        browser.close()
        exit()

    # click the text which contains the account number
    page.click("//a[contains(text(), '"+accountNo+"')]")

    # account overview screen
    page.click("#ctl00_Content_TransactionDetail_TxtFromDate")
    page.fill("#ctl00_Content_TransactionDetail_TxtFromDate", fromDate)

    page.click("#ctl00_Content_TransactionDetail_TxtToDate")
    page.fill("#ctl00_Content_TransactionDetail_TxtToDate", toDate)
    # click text "Lãi cộng dồn" to discard date picker
    page.click("//label[contains(text(), 'Lãi cộng dồn')]")

    page.click("#TransByDate")

    time.sleep(2)

    # save html to file
    with open("page.html", "w", encoding="utf-8") as f:
        f.write(page.content())

    browser.close()

# clean up
os.remove("captcha.png")