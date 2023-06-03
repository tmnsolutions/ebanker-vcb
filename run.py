import os

# run crawl.py
if (not os.path.isfile("page.html")):
    print("page.html not existed, running crawl.py")
    with open("crawl.py") as f:
        exec(f.read())

# run run.py
if (os.path.isfile("page.html")):
    print("Running parse.py")
    with open("parse.py") as f:
        exec(f.read())
    os.remove("page.html")
