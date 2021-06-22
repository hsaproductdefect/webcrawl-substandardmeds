"""
Organisation: Vigilance and Compliance Branch, Health Products Regulation Group, Health Sciences Authority, Singapore
Last Updated Date: 9 March 2021
"""
Script containing all the commonly used functions for the web crawler
"""

from bs4 import BeautifulSoup
from googletrans import Translator
from urllib.parse import urljoin

from PIL import Image 
from pdf2image import convert_from_path

import pytesseract 
import os 
import string 
import csv
import datetime
import requests
import random
import re
import time

def scrape_webpage(url):
    """
    Given URL, retrieve source code from the webpage

    Input: URL (string)
    Output: Clean HTML code of the website specified by URL (BS4 object)

    """
    html_code = requests.get(url, timeout=(10,42))
    clean_html = BeautifulSoup(html_code.text, "html.parser")
    return clean_html

def extract_url_layer1(BASE_URL, html_code_bs4, element_name, attribute_name, attribute_value):
    """
    Given source code and target, retrieve URLs from the webpage. For the most straightforward case

    Input: source code + specific element and attribute value to get URLs from (BS4 object, strings)
    Output: url_list - a list of all the URLs for further parsing (list of strings)

    """
    selected_content = html_code_bs4.find(element_name,{attribute_name: attribute_value})
    url_list_raw = selected_content.find_all("a", href=True)
    url_list = [urljoin(BASE_URL,url["href"]) for url in url_list_raw]

    return url_list

def keep_new_urls(filename, url_list):
    """
    Check if there are new URLs. If there are, return only the new URLs
    
    Input: CSV filename with previously scraped URLs, URL list
    Output: URL list containing links that are new and yet to be scraped
    """
    if len(url_list) == 0:
        print("No links found!")
        return 0

    if os.path.isfile(os.getcwd() + "/../results/" + filename):
        data = read_in_csv(os.getcwd() + "/../results/" + filename)

        if data != []:
            latest_url = data[0][14]

            if latest_url == url_list[0]:
                print("Website is not scraped as database is up to date.")
                return 0

            else:
                try:
                    url_list = url_list[:url_list.index(latest_url)] # only keep the new urls
                    print('Found new URLs!')
                except ValueError:
                    url_list = url_list

        else:
            print(".csv file exists but is empty. Proceeding to scrape the website.")
    else:
        print('.csv not found, scraping all links')

    return url_list

def update_metadata_csv(index, df):
    """
    Update the last scraped datetime for the corresponding webpage
    """
    df.iloc[index, -1] = datetime.datetime.now()
    return df

def read_in_csv(filename):
    """
    Read in the .csv file, given filename
    """
    with open(filename, encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        data = [r for r in reader]
        data.pop(0)

        if data == []:
            print(filename + " is empty!")
    
    return data

def write_to_csv(data, target_directory, filename):
    """
    Write the final data to the respective CSV file.
    
    Input: data to be written (list of lists, mixed type)
    Output: csv file 
    """
    if data == []:
        print("Data input is an empty list! .csv file is not written.")
        return 

    if not re.match('^\d\d\d\d-\d\d-\d\d.csv$', filename):
        try:
            old_data = read_in_csv(target_directory + filename)
        except FileNotFoundError:
            old_data = []

    with open(target_directory + filename, 'w', newline="", encoding='utf-8-sig') as f:
        wr = csv.writer(f)
        wr.writerow(("Agency", "Country", "Webpage", "Date", "Title", "Category", "Issue / Background (combined)", "Nature of Issue", "Products affected", "HSA's Product Registration","Affected Company Name", "Is this Case Related to Local Therapeutic Product Defect(s)?", "Preliminary Assessment", "Estimated Priority", "Url", "Date scraped"))
        wr.writerows(data)
        if not re.match('^\d\d\d\d-\d\d-\d\d.csv$', filename) and old_data != []:
            wr.writerows(old_data)

def isEnglish(s):
    """
    Check whether string s is in English, returns True or False
    """
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        print('not English')
        return False
    else:
        return True

def isChinese(s):
    """
    Check whether string s is in Chinese, returns True or False
    """
    if re.findall(r'[\u4e00-\u9fff]+', s):
        return True
    else:
        return False 

def malay_to_english(foreign_text):
    """
    Performs translation from Malay to English using googletrans library
    """
    try:
        translator = Translator()
        english_text = translator.translate(foreign_text).text
    except:
        print("Unable to translate! Using foreign text.")
        english_text = foreign_text

    return english_text

def chinese_to_english(foreign_text):
    """
    Performs translation from Chinese to English using googletrans library
    """ 
    try:
        translator = Translator()
        english_text = translator.translate(foreign_text).text
        print(english_text)
    except:
        print("Unable to translate! Using foreign text.")
        english_text = foreign_text

    return english_text

def clean_text(dirty_text):
    """
    Only keep alnum and spaces 
    """
    cleaned_text = ''.join([i for i in dirty_text if (i.isalnum() or i == ' ' or i in string.punctuation or i == '\n')]) # exclude = ['â–¼']
    cleaned_text = ' '.join(cleaned_text.split()) # resolves double space
  
    if len(cleaned_text) > 30000: #CSV cells cannot store more than 30000 characters
        cleaned_text = "[truncated] " + cleaned_text[:30000]
        truncation_flag = 1
    else:
        truncation_flag = 0

    return (cleaned_text, truncation_flag)

def get_title(source_code_subset, element_name, attribute_name, attribute_value, language='english'):
    """
    Remove leading and trailing spaces + translates + cleans 
    Assumes title doesn't need to be shorterned
    """
    try:
        if element_name == 0:
            title_raw = source_code_subset
        elif element_name == 'a' and attribute_name == 0 and attribute_value == 0: # case when the title is the URL href text
            title_raw = source_code_subset.find(element_name)
        else:
            title_raw = source_code_subset.find(element_name, {attribute_name:attribute_value})
        
        title_text = title_raw.get_text().strip()

    except AttributeError:
        print("Title can't be scrapped!")
        title_text = '-'

    if language == 'chinese' and isChinese(title_text):
        time.sleep(3) # To avoid too many requests error
        title_text = chinese_to_english(title_text)
        
    if language == 'malay':
        time.sleep(3) # To avoid too many requests error
        title_text = malay_to_english(title_text)
    
    (title, truncation_flag) = clean_text(title_text) # title won't go beyond 30k so can ignore
    return title
  
def get_link(source_code_subset, BASE_URL):
    """
    Input: HTML code, Original URL
    Output: URL (string)
    """
    try: 

        link_raw = source_code_subset.find("a", href=True)
        link = urljoin(BASE_URL, link_raw["href"])
        link = link.strip()
        link = link.replace(' ','%20')
        return link
    
    except NameError:
        print("Unable to get link!")
        return 0

def get_date(source_code_subset, element_name, attribute_name, attribute_value, date_regex):
    """
    Read in date and return a datetime object of the date 
    There will be a need to parse the date
    If date is more than 30 days ago, return 1 for old_news_flag

    Input: 
    Output: A tuple of (date, old_news_flag)
    """
    try: 
        if element_name == 0:
            date_raw = source_code_subset
        elif attribute_name == 0 and attribute_value == 0:
            date_raw = source_code_subset.find(element_name)
        else:
            date_raw = source_code_subset.find(element_name, {attribute_name:attribute_value})
        
        try:
            date_text = date_raw.get_text().strip()
        except AttributeError:
            return (0, 0)
        
        try:
            date_datetime = datetime.datetime.strptime(date_raw.get_text().strip(), date_regex)
        except ValueError: # usually because of unconverted data (e.g. extra words other than the dates)
            date_regex_reformatted = 'date_regex' + date_regex.replace(' ', '').replace('/', '').replace('%', '_').replace('-', '').replace(',', '')
            date_search_result = re.search(eval(date_regex_reformatted), date_text).group()
            if date_search_result:
                date_datetime = datetime.datetime.strptime(date_search_result, date_regex)
            else: # can't find a date
                return (0, 0)
        date = date_datetime.strftime("%Y/%m/%d")

        if datetime.datetime.today().year != date_datetime.year or (datetime.datetime.today() - date_datetime).days > 30:
            return (date, 1)
        else:
            return (date, 0)
    
    except NameError:
        print('Unable to scrape date from current URL')
        return (0,0)

def ocr_for_pdf(filename):
    """
    Given a PDF file, extract the text from the file.
    
    Input: PDF file
    Output: Text in PDF
    """
    

    """Converting PDF to images""" 
    filename = os.path.abspath(filename)
    pages = convert_from_path(filename, 500) # Store all the pages of the PDF in a variable 

    image_counter = 1 # Counter to store images of each page of PDF to image 
    for page in pages: # Iterate through all the pages stored above 
        """Declaring filename for each page of PDF as JPG. For each page, filename will be PDF page n -> page_n.jpg"""
        img_filename = filename[:-4] + "_page_" + str(image_counter) + ".jpg"
        page.save(img_filename, 'JPEG') # Save the image of the page in system 
        image_counter = image_counter + 1 # Increment the counter to update filename 
    
    """Recognizing text from the images using OCR""" 
    filelimit = image_counter - 1 # Variable to get count of total number of pages 
    case_description_text = ''
    
    """Iterate from 1 to total number of pages"""
    for i in range(1, filelimit + 1): 
        img_filename = filename[:-4] + "_page_" + str(i) + ".jpg" # Set filename to recognize text from, creates page_1.jpg to n 
        text = str(((pytesseract.image_to_string(Image.open(img_filename))))) # Recognize the text as string in image using pytesserct 
        text = text.replace('-\n', '') + ' '
        case_description_text += text

        if i == 2: # don't read in too much, else take too long
            break

    case_description_text = case_description_text.strip()
    return case_description_text

def extract_information_layer2_pdf(title, agency, webpage, date, url):
    """
    Given a PDF link for the second layer, download and extarct the case description text from PDF.
    
    Input: Link to PDF and other details of the webpage
    Output: Case description text
    """
    try:
        filename = download_layer2_pdf(title, agency, webpage, date, url)

        import tika
        tika.initVM()
        from tika import parser

        body_text_raw = parser.from_file(filename)
        body_text = body_text_raw["content"]

        malay_website_list = ["Malay_agency"]
        if body_text:
            body_text = body_text.strip()
            if agency in malay_website_list:
                print("List match")
                translated_text = malay_to_english(body_text)
                (case_description_text, truncation_flag) = clean_text(translated_text)
            elif agency == "Chinese_agency":
                translated_text = chinese_to_english(body_text)
                (case_description_text, truncation_flag) = clean_text(translated_text)
            else:
                (case_description_text, truncation_flag) = clean_text(body_text)
            
            return case_description_text

        else: # no text extracted, probably means only images in PDF. need OCR
            ocr_case_description_text = ocr_for_pdf(filename)
            
            if ocr_case_description_text:
                if agency in malay_website_list:
                    print("List match")
                    translated_text = malay_to_english(ocr_case_description_text)
                    (case_description_text, truncation_flag) = clean_text(translated_text)
                else:
                    (case_description_text, truncation_flag) = clean_text(ocr_case_description_text)                
                return case_description_text

            else:
                print('Unable to extract any text from PDF')
                return '-'

    except NameError:
        print('Unable to get PDF file from Layer 2...')
        return '-'

def download_layer2_pdf(title, agency, webpage, date, url):
    """
    Download the PDF link and save it in a local folder.
    
    Input: Link to PDF and other details of the webpage
    Output: Saves PDF in the corresponding directory
    """
    try:
        url = url.replace(' ','%20')
        
        title_cleaned = title.replace('\n','_').replace('\r','_').translate(str.maketrans({a:None for a in string.punctuation})).replace(' ','_')[:100]
        date_cleaned = date.replace('/','_')
        country = agency.split('-')[1].strip()

        pdf_folder_directory_higher = '../results/pdf/' + country + '/'
        if not os.path.exists(pdf_folder_directory_higher):
            print('folder ' + pdf_folder_directory_higher + ' not found, creating it...')
            os.makedirs(pdf_folder_directory_higher)

        pdf_folder_directory = '../results/pdf/' + country + '/' + webpage + '/'
        if not os.path.exists(pdf_folder_directory):
            print('folder ' + pdf_folder_directory + ' not found, creating it...')
            os.makedirs(pdf_folder_directory)
        
        filename = pdf_folder_directory + date_cleaned + '_' + title_cleaned + '.pdf'
        r = requests.get(url, stream=True)
        with open(filename, 'wb') as f:
            f.write(r.content)
        
        return filename

    except NameError:
        print('Unable to obtain PDF file from layer 2 URL!')
        return 0
    
def get_description(source_code_subset, element_name, attribute_name, attribute_value, language='english'):
    """
    Given source code and target, download the description from webpage.

    Input: source code + specific element and attribute value to get description.
    Output: Complete case description text in second layer
    """
    try: 
        if element_name == 0:
            description_raw = source_code_subset
        elif attribute_name == 0 and attribute_value == 0:
            description_raw = source_code_subset.find(element_name)
        else:
            description_raw = source_code_subset.find(element_name, {attribute_name:attribute_value})
        if not description_raw: # nothing scraped
            return (0,0,0,0)

        description_raw_table_check = description_raw.find_all('table')

        if description_raw_table_check:
            for table in description_raw_table_check:
                table.decompose() # remove tables
            table_present_flag = 1
        else:
            table_present_flag = 0

        description_raw_style_check = description_raw.find_all('style')

        if description_raw_style_check:
            for style in description_raw_style_check:
                style.decompose() # remove <style> blocks

        description_raw_script_check = description_raw.find_all('script')

        if description_raw_script_check:
            for script in description_raw_script_check:
                script.decompose() # remove <script> blocks

        unprocessed_text = description_raw.get_text().strip()
        (description_cleaned, truncation_flag) = clean_text(unprocessed_text) # truncates, but if < 30k no difference

        if language == 'english':
            return (description_cleaned, table_present_flag, truncation_flag, unprocessed_text)
        elif language == 'chinese': # there will be cases when 'truncated' in inside but should be okay 
            description_translated = chinese_to_english(description_cleaned)[:30000] # need to truncate again after translation 
            if len(description_cleaned) > 30000 or len(description_translated) > 30000:
                description_translated = "[truncated] " + description_translated
                truncation_flag = 1
            return (description_translated, table_present_flag, truncation_flag, unprocessed_text)
        elif language == 'malay':
            description_translated = malay_to_english(description_cleaned)[:30000] # need to truncate again after translation 
            if len(description_cleaned) > 30000 or len(description_translated) > 30000:
                description_translated = "[truncated] " + description_translated
                truncation_flag = 1
            return (description_translated, table_present_flag, truncation_flag, unprocessed_text)
        else:
            print('Invalid language selected!')
    except NameError:
        print('No long description found!')
        return (0,0,0,0)
     
def generate_pdf_from_url(title, url, agency, webpage, date):
    """
    Given a URL of the webpage, convert it and download as PDF file.
    
    Input: Link to PDF and other details of the webpage
    Output: Saves PDF in the corresponding directory
    """
    try: 
        if 'pdf' == url.split('.')[-1]:
            print("The webpage is a PDF file. Cannot use pdfkit. Using requests.")
            download_layer2_original_pdf(title, url, agency, webpage, date)
            return

        title_cleaned = title.replace('\n','_').replace('\r','_').translate(str.maketrans({a:None for a in string.punctuation})).replace(' ','_')[:100]
        date_cleaned = date.replace('/','_')
        country = agency.split('-')[1].strip()

        original_pdf_folder_directory_higher = '../results/original_pdf/' + country + '/'
        if not os.path.exists(original_pdf_folder_directory_higher):
            print('folder ' + original_pdf_folder_directory_higher + ' not found, creating it...')
            os.makedirs(original_pdf_folder_directory_higher)

        original_pdf_folder_directory = '../results/original_pdf/' + country + '/' + webpage + '/'
        if not os.path.exists(original_pdf_folder_directory):
            print('folder ' + original_pdf_folder_directory + ' not found, creating it...')
            os.makedirs(original_pdf_folder_directory)

        try:
            import pdfkit
            path_wkthmltopdf = '../wkhtmltopdf/bin/wkhtmltopdf.exe'
            config =pdfkit.configuration(wkhtmltopdf = path_wkthmltopdf)
            #option : disable-javascript option to expand checklists/drop downs/etc in page. Eg: TGA Compmed page
            options = {'quiet':'','disable-javascript':''}
            pdfkit.from_url(url,original_pdf_folder_directory + date_cleaned + '_' + title_cleaned[0:30] + '_'+ title_cleaned[-15:] + '_' + str(random.randint(0,100)) + '.pdf',configuration=config, options = options)
        except Exception:
            print("Error Occured in generate_pdf_from_url")
    
    except NameError:
        print('.pdf file not generated for ' + agency + ' ' + webpage)
        print(title)

    return

def download_layer2_original_pdf(title, url, agency, webpage, date):
    """
    Download the PDF link and save it in a local folder.
    
    Input: Link to PDF and other details of the webpage
    Output: Saves PDF in the corresponding directory
    """
    title_cleaned = title.replace('\n','_').replace('\r','_').translate(str.maketrans({a:None for a in string.punctuation})).replace(' ','_')[:100]
    date_cleaned = date.replace('/','_')
    country = agency.split('-')[1].strip()

    original_pdf_folder_directory_higher = '../results/original_pdf/' + country + '/'
    if not os.path.exists(original_pdf_folder_directory_higher):
        print('folder ' + original_pdf_folder_directory_higher + ' not found, creating it...')
        os.makedirs(original_pdf_folder_directory_higher)

    original_pdf_folder_directory = '../results/original_pdf/' + country + '/' + webpage + '/'
    if not os.path.exists(original_pdf_folder_directory):
        print('folder ' + original_pdf_folder_directory + ' not found, creating it...')
        os.makedirs(original_pdf_folder_directory)
    
    filename = original_pdf_folder_directory + date_cleaned + '_' + title_cleaned + '.pdf'
    r = requests.get(url, stream=True)
    with open(filename, 'wb') as f:
        f.write(r.content)
    
    return

def generate_txt_case_description(title, case_desc, agency, webpage, date):
    """
    CSV files has a character limit, so when there's >30k characters, we will generate a txt of the case description instead
    
    Input: Title, case description and other details of webpage
    Output: Saves the raw case description in a text file
    """
    try:
        title_cleaned = title.replace('\n','_').replace('\r','_').translate(str.maketrans({a:None for a in string.punctuation})).replace(' ','_')[:100]
        date_cleaned = date.replace('/','_')
        country = agency.split('-')[1].strip()

        long_case_description_folder_directory_higher = '../results/long_case_description/' + country + '/'
        if not os.path.exists(long_case_description_folder_directory_higher):
            print('folder ' + long_case_description_folder_directory_higher + ' not found, creating it...')
            os.makedirs(long_case_description_folder_directory_higher)

        long_case_description_pdf_folder_directory = '../results/long_case_description/' + country + '/' + webpage + '/'
        if not os.path.exists(long_case_description_pdf_folder_directory):
            print('folder ' + long_case_description_pdf_folder_directory + ' not found, creating it...')
            os.makedirs(long_case_description_pdf_folder_directory)
        
        with open(long_case_description_pdf_folder_directory + date_cleaned + '_' + title_cleaned[0:30] + '.txt', 'w', encoding="utf-8") as f:
            f.write(case_desc)
    except NameError:
        print('.txt file not generated for ' + agency + ' ' + webpage)
        print(title)
    
    return
