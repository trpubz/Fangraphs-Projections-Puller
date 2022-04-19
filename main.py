# by pubins.taylor
# automates the downloading of RoS Projections based on user input


from Stats import StatGrp
from Projections import Projections
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import os
from bs4 import BeautifulSoup
import pandas as pd
# from selenium.webdriver.chrome.options import Options as ChromeOpitons
# from selenium.common.exceptions import *
from selenium.webdriver.common.by import By


def dir_builder(dirDownload: str = "root") -> os.path:
    outputPath: os.path
    if dirDownload == "root":
        projectRoot = os.path.dirname(os.path.dirname(__file__))
        outputPath = os.path.join(projectRoot, 'lib/csvs')
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
    driver = webdriver.Chrome(options=options,desired_capabilities=caps)
    return driver


def url_builder(projections: [Projections], pos: [StatGrp] = [StatGrp.HIT, StatGrp.PIT]) -> [str]:
    urls = []
    for grp in pos:
        for proj in projections:
            fgURL = "https://www.fangraphs.com/projections.aspx?pos=all&stats=" + grp.value + "&type=" + \
                    proj.value + "&team=0&lg=all&players=0"
            urls.append(fgURL)

    return urls


def download_csv(webdriver: webdriver, projections: [Projections], pos: [StatGrp] = [StatGrp.HIT, StatGrp.PIT]):
    fgURLS = url_builder(projections=projections, pos=pos)
    for fgURL in fgURLS:
        # Wait a reasonable time that a person would take
        wait = WebDriverWait(driver, 10)
        driver.get(fgURL)
        # Scrolling down the page helps get to the file more reliably
        driver.execute_script("window.scrollTo(0, 200)")
        dropdownButton = driver.find_element(By.CSS_SELECTOR, "button.rcbActionButton")
        # Wait until the element to download is available and then stop loading
        # Fangraphs has ads that cause the page to appear to continue loading
        driver.execute_script("window.stop();")
        dropdownButton.click()
        options = Select(driver.find_element(By.CSS_SELECTOR, "ul.rcbList"))
        options.select_by_visible_text("1000")


def print_csvs(dirDownload: os.path):
    df = pd.read_csv(dirDownload)
    print(df)


if __name__ == "__main__":
    dirDownload = dir_builder()
    driver = driver_config(dirDownload=dirDownload)
    download_csv(webdriver=driver, projections=[Projections.DC_RoS])
    print_csvs(dirDownload=dirDownload)
    driver.quit()
