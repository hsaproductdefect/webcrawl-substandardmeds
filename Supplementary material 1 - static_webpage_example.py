"""
Script to scrape data from Product Recall Webpage
"""
import datetime
import time

import utils # Custom script containing all the common functions used to extract data from multiple webpages

"""URL to scrape"""
BASE_URL = "<*https://www.agency.com/recall*>"


def extract_information_layer1(BASE_URL, html_code_bs4, element_name, attribute_name, attribute_value):
    """
    Given source code and target, retrieve URLs from the webpage

    Input: source code + specific element and attribute value to get URLs from (BS4 object, strings)
    Output: url_list - a list of all the URLs for further parsing (list of strings)

    """
    selected_content = html_code_bs4.find(element_name,{attribute_name: attribute_value})

    search_results = selected_content.find_all('li', {'class':'gem-c-document-list__item '})
    if not search_results:
        search_results = selected_content.find_all('li', {'class':'gem-c-document-list__item'})

    title_list = []
    url_list = []
    date_list = []
    short_desc_list = []
    
    """Loop through the results list and extract details for every alert"""
    for result in search_results:
        url = utils.get_link(result, BASE_URL)
        title = utils.get_title(result, 'a', 'class', 'gem-c-document-list__item-title ')
        if title == '-':
            title = utils.get_title(result, 'a', 'class', 'gem-c-document-list__item-title')
            print('Got title on the 2nd try!')
        (date, old_news_flag) = utils.get_date(result, 'time', 0,0, '%d %B %Y')
        short_desc = utils.get_title(result, 0,0,0)

        """Filter alerts that have been already crawled"""
        if old_news_flag == 0:
            url_list.append(url)
            title_list.append(title)
            date_list.append(date)
            short_desc_list.append(short_desc)
        else:
            print("Skipping old news...")
            break
    
    information_tuple = (title_list, url_list, date_list, short_desc_list)
    return information_tuple

def extract_information_layer2(html_code_bs4):
    """
    Given the html source code of the second layer, extract the detailed case description of the alert along with other attributes.
    
    Input: Source code of the second layer
    Output: Tuple containing title and detailed case description of the alert
    """

    title = utils.get_title(html_code_bs4, 'h1', 'class', 'gem-c-title__text gem-c-title__text--long')
    subtitle = utils.get_title(html_code_bs4, 'p', 'class', 'gem-c-lead-paragraph ')
    (case_description_text, table_present_flag, truncation_flag, unprocessed_text) = utils.get_description(html_code_bs4, 'div', 'class', 'gem-c-direction-ltr')

    information_tuple = (title, subtitle, case_description_text, unprocessed_text)
    return information_tuple

"""Main function"""
def <*main_agency_recall*>(filename):
    
    agency = "drug agency"
    country = "country x"
    webpage = "product recall"
    
    """Get the HTML source code and first layer information"""
    webpage_bs4_layer1 = utils.scrape_webpage(BASE_URL)
    (title_list, url_list, date_list, short_desc_list) = extract_information_layer1(BASE_URL, webpage_bs4_layer1, "ol", "class", "gem-c-document-list gem-c-document-list--no-underline")

    """Scraping of actual webpage"""
    layer2_data = []
    status_or_urls = utils.keep_new_urls(filename, url_list)
    if status_or_urls:
        for i, url in enumerate(status_or_urls):
            print("Taking a 10 seconds break per URL, as requested by agency.")
            time.sleep(10)

            print("Scraping from: " + url)
            webpage_bs4_layer2 = utils.scrape_webpage(url)
            (title, subtitle, case_description_text, unprocessed_text) = extract_information_layer2(webpage_bs4_layer2)

            date = date_list[i]
            title = title_list[i]
            category = "-"
            issuebg = title + ' ' + subtitle + ' ' + short_desc_list[i] + ' ' + case_description_text
            nature_of_issue = utils.perform_text_classification(issuebg)
            products_affected = "-"
            affected_company_name = "-"
            url = url 

            """Collate all the info to save in a CSV file"""
            complete_csv_info = (agency, country, webpage, date, title, category, issuebg, nature_of_issue, products_affected, affected_company_name, url, datetime.datetime.now().strftime('%Y/%m/%d'))
            """Save the webpage as PDF for future reference"""
            utils.generate_pdf_from_url(title, url, agency, webpage, date) 
            """Save the raw webpage text in a text file since a CSV cell cannot store more than 30000 characters"""
            utils.generate_txt_case_description(title, unprocessed_text, agency, webpage, date)
        
            layer2_data.append(complete_csv_info)
    return layer2_data

if __name__ == "__main__":
    main_agency_recall('agency_recall.csv')
