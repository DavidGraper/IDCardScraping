import json

import selenium
import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import mysql.connector

import time
import datetime
import pandas as pd

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


def processnullabledate(inputstring):

    if inputstring == "":
        return "NULL"
    else:
        yearstring = inputstring[6:10]
        datestring = inputstring[3:5]
        monthstring = inputstring[0:2]
        return "'{0}-{1}-{2}'".format(yearstring, monthstring, datestring)


def update_idcardinfo(updatedidcardinfo):
    mydb = mysql.connector.connect(host="localhost",
                                   user="root",
        password="",
        database="biologydb"
    )

    mycursor = mydb.cursor()

    sql = "INSERT INTO UAlbanyIDCards (ualbanyempid, name, startdate, enddate, comment, createdate, "\
            "operatorname, membertype, nameofgroup) " \
            "VALUES ('{0}', '{1}', {2}, {3}, '{4}', {5}, '{6}', '{7}', '{8}')"

    for item in updatedidcardinfo["data"]:

        # Ignore headers
        if item["ualbanyempid"] == "PIK":
            continue

        # Process data row
        ualbanyempid = item['ualbanyempid']
        name = item['name']
        startdate = processnullabledate(item["startdate"])
        enddate = processnullabledate(item['enddate'])
        comment = item['comment']
        createdate= processnullabledate(item['createdate'])
        operatorname = item['operatorname']
        membertype = item['membertype']
        nameofgroup = item['nameofgroup']

        sql1 = sql.format(ualbanyempid, name, startdate, enddate, comment, createdate, operatorname, membertype, nameofgroup)

        mycursor.execute(sql1)
        mydb.commit()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    print_hi('PyCharm')

    # Diagnostic

    # # Database update part
    #
    # f = open("output.json", "r")
    # string1 = f.read()
    #
    # string1 = string1.replace("\n", "")
    #
    # object1 = json.loads(string1)
    #
    # update_idcardinfo(object1)
    #
    # exit()


    # urlpage = 'https://groceries.asda.com/search/yogurt'

    # urlpage = 'https://quotes.toscrape.com'

    urlpage = 'https://idcard.albany.edu/admin/patrongroups/patrongroups.php'
    print(urlpage)
    driver = selenium.webdriver.Firefox()

    driver.get(urlpage)


    print("Situate yourself on main page")
    print("Select first group and enter group name")
    nameofgroup = input("Group Name")

    list1 = []

    while nameofgroup != "quit":

        ualbanyids = driver.find_elements(By.CLASS_NAME, 'td-PIK')
        names = driver.find_elements(By.CLASS_NAME, 'td-NAME')
        startdates = driver.find_elements(By.CLASS_NAME, 'td-GROUPEFFECTIVE')
        enddates = driver.find_elements(By.CLASS_NAME, 'td-GROUPEXPIRE')
        comments = driver.find_elements(By.CLASS_NAME, 'td-THECOMMENT')
        createdates = driver.find_elements(By.CLASS_NAME, 'td-CREATEDATE')
        operatornames = driver.find_elements(By.CLASS_NAME, 'td-OPERATORNAME')
        membertypes = driver.find_elements(By.CLASS_NAME, "td-MEMBERTYPE")

        #- elements = driver.find_elements(By.CLASS_NAME, 'author')


        counter = 0
        for ualbanyid in ualbanyids:
            tempdict = {"nameofgroup": nameofgroup}
            tempdict["ualbanyempid"] = ualbanyid.text
            tempdict["name"] = names[counter].text
            tempdict["startdate"] = startdates[counter].text
            tempdict["enddate"] = enddates[counter].text
            tempdict["comment"] = comments[counter].text
            tempdict["createdates"] = createdates[counter].text
            tempdict["operatornames"] = operatornames[counter].text
            tempdict["membertype"] = membertypes[counter].text

            list1.append(tempdict)
            counter += 1

            # driver.execute_script("wi=ndow.scrollTo(0,document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenofPage;")

        nameofgroup = input("Enter next name of group")

    f = open("output.json", "a")
    for item in list1:
        f.write(json.dumps(item, indent=2))
    f.close()
