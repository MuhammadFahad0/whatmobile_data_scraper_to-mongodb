import json

import openpyxl as openpyxl
import requests
from bs4 import BeautifulSoup
import pymongo


myClient = pymongo.MongoClient("mongodb+srv://detailmobile65:L2PcRKlQA2UJFDXd@cluster0.qsgcfl3.mongodb.net/")
myDb = myClient["MobileDetail"]
myCol = myDb["Samsung"]


mainLink = "https://www.whatmobile.com.pk/Samsung_Mobiles_Prices"

mainSoupLink = BeautifulSoup(requests.get(mainLink).content, "html.parser")

mobileLink = mainSoupLink.find('div', {'class': 'mobiles'})

mobileList = mobileLink.find_all("a", {'class': 'BiggerText'}, href=True)

AllMobileDetails = dict()
mobileIndex = 0
for link in mobileList:
    wb = openpyxl.Workbook()
    sheet = wb.active
    soupLink = BeautifulSoup(requests.get("https://www.whatmobile.com.pk/" + link["href"]).content, "html.parser")
    details = {}
    mobileName = soupLink.find('h2', {'class': 'Heading1'})

    if mobileName.text == " Top Mobile Phones ":
        break

    details["Company"] = "Samsung"
    details["MobileName"] = mobileName.text.replace("detailed specifications", "")

    columns = soupLink.findAll('tr')
    for column in columns:
        try:
            td = ""
            th = str(column.find("th").text).replace("\n", "").replace("\xa0", "").replace(" ", "")

            if len(column.findAll("td")) > 1:
                td = str(column.findAll("td")[1].text).replace("\n", "").replace("\xa0", "")
            else:
                td = str(column.findAll("td")[0].text).replace("\n", "").replace("\xa0", "")

            if th == "":
                details["Extra"] = details["Extra"] + " , " + td
            else:
                details[th] = td
        except:
            print("Error : " + str(column.find("th")))

    details["Weight"] = int(details["Weight"].replace(" ", "").replace("g", ""))

    details["Size"] = float(details["Size"].replace("Inches", "").replace(" ", ""))

    Price = details["Price"].replace("Price in Rs: ", "").replace("Price in USD: ", "").replace(",", "")

    v = Price.split(" ")

    if len(v) == 2:
        details["PriceRs"] = int(v[0])
        details["PriceUSD"] = int(v[1].replace("$", ""))

    if "Yes" in details["Card"]:
        details["Card"] = 1
    else:
        details["Card"] = 0

    if "Yes" in details["NFC"]:
        details["NFC"] = 1
    else:
        details["NFC"] = 0

    if "Yes" in details["Torch"]:
        details["Torch"] = 1
    else:
        details["Torch"] = 0

    details.pop('Ratings', None)

    index = 0
    for detail in details:
        index = index + 1
        sheet.cell(row=index, column=1).value = str(detail)
        sheet.cell(row=index, column=2).value = str(details[detail])

        if str(detail) in AllMobileDetails:
            AllMobileDetails[str(detail)][mobileIndex] = str(details[detail])
        else:
            AllMobileDetails[str(detail)] = {}
            AllMobileDetails[str(detail)][mobileIndex] = str(details[detail])

    mobileIndex = mobileIndex + 1

    # wb.save(str(details["MobileName"]) + ".xlsx")
    # jsonConverted = json.dumps(details)
    x = myCol.insert_one(details)
    print(x.inserted_id)


wb = openpyxl.Workbook()
sheet = wb.active

index = 1
for MobileDetail in AllMobileDetails:

    sheet.cell(column=index, row=1).value = MobileDetail
    for Mobile in AllMobileDetails[MobileDetail]:
        sheet.cell(column=index, row=Mobile + 2).value = str(AllMobileDetails[MobileDetail][Mobile])
    index = index + 1

wb.save(str("all") + ".xlsx")


def linkToMapWhatMobile():
  print("Hello from a function")