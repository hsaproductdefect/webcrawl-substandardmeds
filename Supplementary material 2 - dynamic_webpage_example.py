"""
Organisation: Vigilance and Compliance Branch, Health Products Regulation Group, Health Sciences Authority, Singapore
Last Updated Date: 9 March 2021
"""
Script to scrape data from Product Recall Webpage
"""
import datetime
import time

import utils # Custom script containing all the common functions used to extract data from multiple webpages

from bs4 import BeautifulSoup
from selenium import webdriver 
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

"""URL to scrape"""
BASE_URL = "<*https://www.agency.com/recall*>"


def extract_information_layer1(BASE_URL, html_code_bs4, element_name, attribute_name, attribute_value):
    """
    Given the html source code, extract the set of new alerts posted on the webpage along with other attributes.
    
    Input: Source code + specific element and attribute value to get URLs from (BS4 object, strings)
    Output: url_list - a list of all the URLs for further parsing (list of strings)
    """
    information_table = html_code_bs4.find(element_name,{attribute_name: attribute_value})
    information_table_body = information_table.find('tbody')

    table_rows = information_table_body.find_all('tr')
    
    date_list = []
    url_list = []
    product_name_list = []
    company_name_list = []
    short_desc_list = []
    
    """Loop through the table and extract details for every alert"""
    for row in table_rows:
        row_columns = row.find_all('td')
        (date, old_news_flag) = utils.get_date(row_columns[0], 0,0,0, '%m/%d/%Y')
        url = utils.get_link(row_columns[1], BASE_URL)
        product_name = utils.get_title(row_columns[1], 0,0,0) + ' ' + utils.get_title(row_columns[2], 0,0,0)
        company_name = utils.get_title(row_columns[4], 0,0,0)
        short_desc = utils.get_title(row_columns[3], 0,0,0)
        
        """Filter alerts that have been already crawled"""
        if old_news_flag == 0:
            date_list.append(date)
            url_list.append(url)
            product_name_list.append(product_name)
            company_name_list.append(company_name)
            short_desc_list.append(short_desc)
        else:
            print('Skipping old news...')
            break
    
    information_tuple = (date_list, url_list, product_name_list, company_name_list, short_desc_list)
    return information_tuple

def extract_information_layer2(html_code_bs4):
    """
    Given the html source code of the second layer, extract the detailed case description of the alert along with other attributes.
    Input: HTML source code of the second layer
    Output: Tuple containing title and detailed case description of the alert
    """
    title = utils.get_title(html_code_bs4, 'h1', 'class', 'content-title text-center')
    (case_description_text, table_present_flag, truncation_flag, unprocessed_text) = utils.get_description(html_code_bs4, 'div', 'class', 'col-md-8 col-md-push-2')
    
    information_tuple = (title, case_description_text, unprocessed_text)
    return information_tuple

"""Main function"""
def <*main_agency_recall*>(filename):

    agency = "drug agency"
    country = "country x"
    webpage = "product recall"
    
    """Initiate selenium web driver to dynamically load the webpage contents"""
    option = webdriver.ChromeOptions() # launch chrome 
    option.add_argument("--incognito")
    option.add_argument("--headless") # don't open, only run in background
    browser = webdriver.Chrome(executable_path='../chromedriver', options=option)
    print("loading javascript-generated content...")
    browser.implicitly_wait(20)
    browser.get(BASE_URL)

    timeout = 10
    try:
        element_present = EC.presence_of_element_located((By.CLASS_NAME, 'sorting_1'))
        WebDriverWait(browser, timeout).until(element_present)
    except TimeoutException:
        print("Timed out waiting for page to load")
    
    """Get the HTML soure code and first layer information"""
    html_code = browser.page_source
    webpage_bs4_layer1 = BeautifulSoup(html_code, "html.parser")
    (date_list, url_list, product_name_list, company_name_list, short_desc_list) = extract_information_layer1(BASE_URL, webpage_bs4_layer1, "table", "id", "DataTables_Table_0")

    """Scraping of actual webpage"""
    layer2_data = []
    status_or_urls = utils.keep_new_urls(filename, url_list)
    if status_or_urls:
        for i, url in enumerate(status_or_urls):

            print("Taking a 30 seconds break per URL, as requested by agency.")
            time.sleep(30)
            
            print("Scraping from: " + url)
            webpage_bs4_layer2 = utils.scrape_webpage(url)
            (title, case_description_text, unprocessed_text) = extract_information_layer2(webpage_bs4_layer2)
            
            date = date_list[i]
            title = title
            category = "-"
            issuebg = short_desc_list[i] + ' ' + case_description_text
            #nature_of_issue = utils.perform_text_classification(issuebg)
            nature_of_issue = "-"
            products_affected = product_name_list[i]
            affected_company_name = company_name_list[i]
            url = url 
            
            """Collate all the info to save in a CSV file"""
            complete_csv_info = (agency, country, webpage, date, title, category, issuebg, nature_of_issue, products_affected, hsa_product_registration, affected_company_name, related_case, preliminary_assessment, estimated_priority, url, datetime.datetime.now().strftime('%Y/%m/%d'))
            """Save the webpage as PDF for future reference"""
            utils.generate_pdf_from_url(title, url, agency, webpage, date) 
            """Save the raw webpage text in a text file since CSV cell cannot store more than 30000 characters"""
            utils.generate_txt_case_description(title, unprocessed_text, agency, webpage, date)
        
            layer2_data.append(complete_csv_info)
    return layer2_data

if __name__ == "__main__":
   main_agency_recall('agency_recall.csv')
