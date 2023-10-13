import json
import re

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

    for item in updatedidcardinfo:
        # for item in updatedidcardinfo["data"]:

        # Ignore headers
        if item["ualbanyempid"] == "PIK":
            continue

        # Process data row
        ualbanyempid = item['ualbanyempid']
        name = item['name']
        startdate = processnullabledate(item["startdate"])
        enddate = processnullabledate(item['enddate'])
        comment = item['comment']
        createdate = processnullabledate(item['createdate'])
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
    # Database update part
    choice = input("1 for webscrape, 2 for data upload")
    #
    if choice=="1":

        urlpage = 'https://idcard.albany.edu/admin/patrongroups/patrongroups.php'
        print(urlpage)
        driver = selenium.webdriver.Firefox()

        driver.get(urlpage)


        # Get list of groups to scrape
        idcardgroups = []
        with open("idcardgroupnames.txt", 'r') as groupnames:
            for groupname in groupnames:
                pattern = r"^\d+ (.*)"
                match = re.search(pattern, groupname)
                idcardgroups.append(match.groups()[0])

        list1 = []

        for idcardgroup in idcardgroups:
            print("Position yourself at group '{0}' and then type '1' to continue".format(idcardgroup))

            if len(input("Continue?  ")) > 0:
                nameofgroup = idcardgroup
            else:
                break

            # print("Situate yourself on main page")
            # print("Select first group and enter group name")
            # nameofgroup = input("Group Name")

            # while nameofgroup != "quit":

            ualbanyids = driver.find_elements(By.CLASS_NAME, 'td-PIK')
            names = driver.find_elements(By.CLASS_NAME, 'td-NAME')
            startdates = driver.find_elements(By.CLASS_NAME, 'td-GROUPEFFECTIVE')
            enddates = driver.find_elements(By.CLASS_NAME, 'td-GROUPEXPIRE')
            comments = driver.find_elements(By.CLASS_NAME, 'td-THECOMMENT')
            createdate = driver.find_elements(By.CLASS_NAME, 'td-CREATEDATE')
            operatorname = driver.find_elements(By.CLASS_NAME, 'td-OPERATORNAME')
            membertype = driver.find_elements(By.CLASS_NAME, "td-MEMBERTYPE")

            # - elements = driver.find_elements(By.CLASS_NAME, 'author')

            counter = 0
            for ualbanyid in ualbanyids:
                tempdict = {"nameofgroup": nameofgroup}
                tempdict["ualbanyempid"] = ualbanyid.text
                tempdict["name"] = names[counter].text
                tempdict["startdate"] = startdates[counter].text
                tempdict["enddate"] = enddates[counter].text
                tempdict["comment"] = comments[counter].text
                tempdict["createdate"] = createdate[counter].text
                tempdict["operatorname"] = operatorname[counter].text
                tempdict["membertype"] = membertype[counter].text

                list1.append(tempdict)
                counter += 1

                # driver.execute_script("wi=ndow.scrollTo(0,document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenofPage;")

            # nameofgroup = input("Enter next name of group")

            # Write out to JSON file at end
            f = open("output_tmp.json", "a")
            for item in list1:
                f.write(json.dumps(item, indent=4))
            f.close()

        with open("sample.json", "w") as outfile:
            json.dump(list1, outfile, skipkeys=False, ensure_ascii=True, check_circular=True,
                      allow_nan=True, cls=None, indent=None, separators=None)



    else:

        f = open("sample.json", "r")
        string1 = f.read()

        string1 = string1.replace("\n", "")

        object1 = json.loads(string1)

        update_idcardinfo(object1)

