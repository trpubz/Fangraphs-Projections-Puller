# by pubins.taylor
# automates the downloading of RoS Projections based on user input
# v0.9
#   working version which prints pandas df to console
#   TODO: clean up columns with "-1" for conversion to JSON export
# init: 2022APR16
# lastUpdate: 2022APR19

from Stats import StatGrp
from Projections import Projections
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common import exceptions
from selenium.webdriver.common.by import By
import os
import glob
import time
import pandas as pd


def dir_builder(dirDownload: str = "root") -> os.path:
    outputPath: os.path
    projectRoot = os.path.dirname(__file__)
    files = glob.glob(projectRoot + "/csvs/*.csv")
    for f in files:
        if f.__contains__("FanGraphs"):
            os.remove(f)
    if dirDownload == "root":
        outputPath = projectRoot + '/csvs'
    elif dirDownload.startswith('C:\\') or dirDownload.startswith('/Users'):
        outputPath = os.path(dirDownload)
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
    urls = []
    for grp in pos:
        for proj in projections:
            fgURL = "https://www.fangraphs.com/projections.aspx?pos=all&stats=" + grp.value + "&type=" + \
                    proj.value + "&team=0&lg=all&players=0"
            fg = {"id": proj.value + "_" + grp.value, "fgURL": fgURL}
            urls.append(fg)

    return urls


def download_csv(driver: webdriver, dirDownload: os.path, projections: [Projections],
                 pos: [StatGrp] = [StatGrp.HIT, StatGrp.PIT]) -> [str]:
    locCSVs = []
    FGs = url_builder(projections=projections, pos=pos)
    for fg in FGs:
        driver.get(fg["fgURL"])
        time.sleep(2)
        # Wait a reasonable time that a person would take
        driver.implicitly_wait(5)
        # Scrolling down the page helps get to the file more reliably
        driver.execute_script("window.scrollTo(0, 200)")
        try:
            # Wait a reasonable time that a person would take
            driver.implicitly_wait(15)
            # Wait until the element to download is available and then stop loading
            driver.find_element(By.LINK_TEXT, "Export Data").click()
            # driver.switch_to.active_element()
            # driver.find_element(By.LINK_TEXT, "Save").click()
            print("got 'em all")
        except exceptions as e:
            print(e.message)
        # dropdownButton = driver.find_element(By.CSS_SELECTOR, "button.rcbActionButton")
        # Fangraphs has ads that cause the page to appear to continue loading
        # driver.execute_script("window.stop();")
        # dropdownButton.click()
        # options = Select(driver.find_element(By.CSS_SELECTOR, "ul.rcbList"))
        # options.select_by_visible_text("1000")
        # get the files in the download directory
        files = glob.glob(dirDownload + "/*.csv")
        for f in files:
            # the file will always download as 'FanGraphs Leaderboard.csv'
            if f.__contains__("FanGraphs"):
                newFileName = fg["id"]
                for removable in files:
                    if removable.__contains__(newFileName):
                        os.remove(removable)
                fileDownloaded = dirDownload + "/" + newFileName + ".csv"
                os.rename(f, fileDownloaded)
                locCSVs.append(fileDownloaded)
                break

    return locCSVs


def print_csvs(files: [os.path]):
    for f in files:
        df = pd.read_csv(f)
        print(df)


if __name__ == "__main__":
    dirDownload = dir_builder()
    driver = driver_config(dirDownload=dirDownload)
    files = download_csv(driver=driver, dirDownload=dirDownload, projections=[Projections.DC_RoS])
    print_csvs(files)
    driver.quit()
