# by pubins.taylor
# automates the downloading of RoS Projections based on user input
# v1
#   working version which saves csv
# init: 2022APR16
# lastUpdate: 2122APR19

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common import exceptions
from selenium.webdriver.common.by import By
import os
import glob
import time
import pandas as pd
from enum import Enum


class Projections(Enum):
    DC_RoS = "rfangraphsdc"
    ZiPS_RoS = "rzips"
    ATC = "atc"


class StatGrp(Enum):
    HIT = 'bat'
    PIT = 'pit'


def dir_builder(dirDownload: str = "root") -> os.path:
    """
    :param dirDownload: String representation of the desired directory to
    download.  If nothing passed, defaults to the project's root directory.

    :return: the os.path which is a string

    Builds a directory on the user preference.

    The function also removes any previously downloaded files found in the same directory with the same naming
    convention.
    """
    outputPath: os.path
    projectRoot = os.path.dirname(__file__)
    files = glob.glob(projectRoot + "/csvs/*.csv")
    # for f in files:
    #     if f.__contains__("FanGraphs"):
    #         os.remove(f)
    if dirDownload == "root":
        outputPath = projectRoot + '/csvs'
    elif dirDownload.startswith('C:\\') or dirDownload.startswith('/Users'):
        outputPath = dirDownload
    else:
        AssertionError()

    return outputPath


def driver_config(dirDownload: os.path) -> webdriver:
    options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": dirDownload}
    # example: prefs = {"download.default_directory" : "C:\Tutorial\down"};
    options.add_experimental_option("prefs", prefs)
    # options.headless = True
    # Set the load strategy so that it does not wait for adds to load
    caps = DesiredCapabilities.CHROME
    caps["pageLoadStrategy"] = "none"
    driver = webdriver.Chrome(options=options, desired_capabilities=caps)
    return driver


def url_builder(projections: [Projections], pos: [StatGrp] = [StatGrp.HIT, StatGrp.PIT]) -> [{str: str}]:
    """
    :param projections: A list of Projections enums representing the desired FanGraphs projection options
    :param pos: A list of position groups. Either hitters, pitchers, or both.  Defaults to both
    :return: A list of dictionary items.  The list represents the URL objects and the dict is keyed by the URL id which
    is used to save the file with the proper naming convention and keyed by the fgURL which is the URL link.
    Builds URLs based on user need.
    """
    urls = []
    for grp in pos:
        for proj in projections:
            fgURL = "https://www.fangraphs.com/projections.aspx?pos=all&stats=" + grp.value + "&type=" + \
                    proj.value + "&team=0&lg=all&players=0"
            fg = {"id": proj.value + "_" + grp.value, "fgURL": fgURL}
            urls.append(fg)

    return urls


def download_csv(dirDownload: os.path, projections: [Projections],
                 pos: [StatGrp] = [StatGrp.HIT, StatGrp.PIT]) -> [os.path]:
    """
    :param driver: a Selenium webdriver
    :param dirDownload: os.path of the desired download directory
    :param projections: the list of desired projections are used to pass directly to the url_builder() func
    :param pos: the list of desired pos groups are used to pass directly to the url_builder() func
    :return: a list of os.path strings used to represent the file locations
    This function gets an HTML page using the Selenium driver, clicks on the Export Data (csv) button, and renames
    the files appropriately.
    """
    locCSVs = []  # location of .csvs
    # FGs are the dictionary items
    FGs = url_builder(projections=projections, pos=pos)
    for fg in FGs:
        driver = driver_config(dirDownload=dirDownload)
        driver.get(fg["fgURL"])
        # Wait a reasonable time that a person would take
        driver.implicitly_wait(15)
        # Scrolling down the page helps get to the file more reliably
        driver.execute_script("window.scrollTo(0, 200)")
        try:
            # hard sleep
            time.sleep(2)
            # Wait a reasonable time that a person would take
            driver.implicitly_wait(15)
            # Wait until the element to download is available and then stop loading
            driver.find_element(By.LINK_TEXT, "Export Data").click()
            time.sleep(2)
        except exceptions as e:
            print(e.message)

        # get all the .csv files in the download directory
        files = glob.glob(dirDownload + "/*.csv")
        for f in files:
            # the file will always download as 'FanGraphs Leaderboard.csv'
            if f.__contains__("FanGraphs"):
                newFileName = fg["id"]  # part of the URL object group
                # remove old files
                for removable in files:
                    if removable.__contains__(newFileName):
                        os.remove(removable)
                newDownloadPath = dirDownload + "/" + newFileName + ".csv"
                os.rename(f, newDownloadPath)
                locCSVs.append(newDownloadPath)
                print(fr"successfully downloaded {newFileName} to {dirDownload}")
                driver.close()
                break

    return locCSVs


def print_csvs(files: [os.path]):
    for f in files:
        df = pd.read_csv(f)
        # axis 1 means columns, inplace means no need for df reassignment
        df.dropna(axis=1, inplace=True)
        print(df)


if __name__ == "__main__":
    optProjs = [p for p in Projections]
    # Print out your options
    for i in range(len(optProjs)):
        print(str(i + 1) + ":", optProjs[i].name)

    # Take user input and get the corresponding item from the list
    inpProjs = int(input("Choose a projection system: "))
    if inpProjs in range(1, len(optProjs)):
        inpProjs = optProjs[inpProjs - 1]
    else:
        print("Invalid input!")

    optDirs = ["/Users/Shared/Baseball HQ/regseason", "root"]
    # Print out your options
    for i in range(len(optDirs)):
        print(str(i + 1) + ":", optDirs[i])

    # Take user input and get the corresponding item from the list
    inpDirs = int(input("Choose a projection system: "))
    if inpDirs in range(1, len(optDirs)):
        inpDirs = optDirs[inpDirs - 1]
    else:
        print("Invalid input!")
    dirDownload = dir_builder(dirDownload=inpDirs)
    files = download_csv(dirDownload=dirDownload, projections=[inpProjs])
    print_csvs(files)
