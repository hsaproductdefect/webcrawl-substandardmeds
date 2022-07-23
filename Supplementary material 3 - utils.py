# -*- coding: utf-8 -*-

"""
test for optimization
"""

"""
Commonly used functions
"""

## Import modules 

from bs4 import BeautifulSoup
import urllib
from urllib.parse import urljoin

import os
import string 
import csv
import datetime
import requests
import random
import re
import time



## Functions 

##used
def scrape_webpage(url):
    """
    Given URL, retrieve source code from the webpage

    Input: URL (string)
    Output: Clean HTML code of the website specified by URL (BS4 object)

    """

    html_code = requests.get(url, timeout=(10,42))
    #print(html_code)
    clean_html = BeautifulSoup(html_code.text, "html.parser")
    #print(clean_html)

    # write html_code to file
    cleanurl = url.replace('/','').replace(':','').replace('https','').replace('http','').replace('www.','').replace('?','').replace('%20','_')
    cleanurl = cleanurl[:100]

    #if url not in all_links: # will need to update when a new link is added
        #with open('../results/html/' + cleanurl + '.html', 'w', encoding='utf-8') as f:
            #f.write(html_code.text)

    return clean_html

'''
2022.03.10
add a new def to scrape HK website
'''
## used
def scrape_webpage_hk(url):
    res=requests.get(url)
    # print(res.encoding)
    encode_lang = str(res.apparent_encoding)
    # print(requests.utils.get_encodings_from_content(res.text))
    string=res.content.decode(encode_lang,'ignore') 
    html=BeautifulSoup(string,'html.parser')
    
    return html

## used
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

## used
def keep_new_urls(filename, url_list):
    """
    Check if there are new URLs
    If there are, return only the new URLs
    """
    if len(url_list) == 0:
        print("No links found!")
        return 0

    if os.path.isfile(os.getcwd() + "/../results/" + filename):
        data = read_in_csv(os.getcwd() + "/../results/" + filename)
        # data_transposed = [list(i) for i in zip(*data)]

        if data != []:
            latest_url = data[0][14] # change to url

            if latest_url == url_list[0]:
                print("Website is not scraped as database is up to date.")
                return 0

            else:
                try:
                    url_list = url_list[:url_list.index(latest_url)] # only keep the new urls
                    print('Found new URLs!')
                except ValueError: # e.g. new year / month
                    url_list = url_list

        else:
            print(".csv file exists but is empty. Proceeding to scrape the website.")
    else:
        print('.csv not found, scraping all links')

    return url_list

## used
def update_metadata_csv(index, df):
    """
    """
    df.iloc[index, -1] = datetime.datetime.now()
    return df

## used
def read_in_csv(filename):
    """
    Read in the .csv file, given filename
    """
    # print(filename)
    
    with open(filename, encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        data = [r for r in reader]
        data.pop(0) # header = data.pop(0)

        if data == []:
            print(filename + " is empty!")
    
    return data

## used
def write_to_csv(data, target_directory, filename):
    """
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

## used
def isChinese(s):
    """
    """
    if re.findall(r'[\u4e00-\u9fff]+', s):
        return True
    else:
        return False 

## used
def malay_to_english(foreign_text):
    """
    Performs translation from Malay to English using googletrans library, for Malaysia websites
    """

    #from googletrans import Translator  
    from google_trans_new import google_translator  # new package installed on 14-01-2021
    """
    To handle "JSONDecodeError: Extra data"
    Change line 151 in google_trans_new/google_trans_new.py which is: response = (decoded_line + ']') to response = decoded_line
    """

    try:
        #print("Unable to translate! Using another translator.")
        #from translate import Translator
        #translator = Translator(from_lang='zh', to_lang='en')
        
        """Commented on 14-01-2021 since google translate is not working"""
        #translator = Translator() 
        #english_text = translator.translate(foreign_text).text
        
        translator = google_translator() 
        english_text = translator.translate(foreign_text)
        print(english_text)
        
    except:
        print("Unable to translate! Using foreign text.")
        english_text = foreign_text

    return english_text

## used
def chinese_to_english(foreign_text):
    """
    Performs translation from Malay to English using googletrans library, for Malaysia websites
    """
    

    """
    2022.02.08 import package for translateing traditional Chinese to simple Chinese
    """
    from pylangtools.langconv import Converter
    foreign_text_zh = Converter('zh-hans').convert(foreign_text)
    #print(foreign_text_zh)
    #from googletrans import Translator  
    from google_trans_new import google_translator  
    try:
        #print("Unable to translate! Using another translator.")
        #from translate import Translator
        #translator = Translator(from_lang='zh', to_lang='en')
        
        """Commented on 14-01-2021 since google translate is not working"""
        #translator = Translator()
        #english_text = translator.translate(foreign_text).text
        
        translator = google_translator()
        """ 2022.02.08 rewrite foreign_text to foreign_text_zh for translateing traditional Chinese to simple Chinese"""
        english_text = translator.translate(foreign_text_zh)  
        print(english_text)
        
    except:
        print("Unable to translate! Using foreign text.")
        english_text = foreign_text

    return english_text

## used
def rename_html_file(url, agency, date, title, webpage):
    if '.pdf' in url:
        return # won't save html for .pdf so don't need rename

    stored_url_cleaned = url.replace('/','').replace(':','').replace('https','').replace('http','').replace('www.','').replace('?','').replace('%20','_')
    stored_url_cleaned = stored_url_cleaned[:100] + '.html'


    # agency_cleaned = agency.split('-')[1].strip()
    date_cleaned = date.replace('/','_')
    title_cleaned = title.replace('\n','_').replace('\r','_').translate(str.maketrans({a:None for a in string.punctuation})).replace(' ','_')[:100]

    local_url = date_cleaned + '_' + title_cleaned + '.html'

    country = agency.split('-')[1].strip()
    html_folder_directory_higher = '../results/html/' + country + '/'
    if not os.path.exists(html_folder_directory_higher):
        print('folder ' + html_folder_directory_higher + ' not found, creating it...')
        os.makedirs(html_folder_directory_higher)

    html_folder_directory = '../results/html/' + country + '/' + webpage + '/'
    if not os.path.exists(html_folder_directory):
        print('folder ' + html_folder_directory + ' not found, creating it...')
        os.makedirs(html_folder_directory)
        
    try:
        os.rename('../results/html/' + stored_url_cleaned, '../results/html/' + country + '/' + webpage + '/' + local_url)
    except FileExistsError: # sometimes 2 websites link to the same article
        os.remove('../results/html/' + stored_url_cleaned)

## used
def clean_text(dirty_text):
    """
    Only keep alnum and spaces 
    """
    cleaned_text = ''.join([i for i in dirty_text if (i.isalnum() or i == ' ' or i in string.punctuation or i == '\n')]) # exclude = ['▼']
    cleaned_text = ' '.join(cleaned_text.split()) # resolves double space
    # cleaned_text = cleaned_text.replace(u'\xa0', u' ')
    # from unicodedata import normalize, category
    # cleaned_text = ''.join([c for c in normalize('NFD', cleaned_text) if category(c) != 'Mn']) # remove weird accents
    if len(cleaned_text) > 30000:
        cleaned_text = "[truncated] " + cleaned_text[:30000]
        truncation_flag = 1
    else:
        truncation_flag = 0

    return (cleaned_text, truncation_flag)

##used
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

## used
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

## used
def get_date(source_code_subset, element_name, attribute_name, attribute_value, date_regex):
    """
    Read in date and return a datetime object of the date 
    There will be a need to parse the date
    If date is more than 30 days ago, return 1 for old_news_flag

    Input: 
    Output: A tuple of (date, old_news_flag)
    """
    try: 

        day_1 = "\d{1}"
        day_2 = "\d{2}" 
        days = "(" + day_2 + "|" + day_1 + ")"
        year_2 = "\d{2}"
        year_4 = "\d{4}"
        monthsShort="(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
        monthsLong="(January|February|March|April|May|June|July|August|September|October|November|December)"
        separators = "([/\- ,]|, )" # FDA Press has July 24, 2019  so ", " becomes a separator too
        
        date_regex_m_d_y = days + separators + days + separators + year_2 # days and months both 2 digits only
        date_regex_d_m_y = days + separators + days + separators + year_2
        date_regex_y_m_d = year_2 + separators + days + separators + days
        date_regex_y_b_d = year_2 + separators + monthsShort + separators + days
        date_regex_y_B_d = year_2 + separators + monthsLong + separators + days
        date_regex_d_b_y = days + separators + monthsShort + separators + year_2
        date_regex_d_B_y = days + separators + monthsLong + separators + year_2
        date_regex_B_d_y = monthsLong + separators + days + separators + year_2

        date_regex_m_d_Y = days + separators + days + separators + year_4
        date_regex_d_m_Y = days + separators + days + separators + year_4
        date_regex_Y_m_d = year_4 + separators + days + separators + days
        date_regex_Y_b_d = year_4 + separators + monthsShort + separators + days
        date_regex_Y_B_d = year_4 + separators + monthsLong + separators + days
        date_regex_d_b_Y = days + separators + monthsShort + separators + year_4
        date_regex_d_B_Y = days + separators + monthsLong + separators + year_4
        date_regex_B_d_Y = monthsLong + separators + days + separators + year_4
        # print(date_regex_d_b_Y)

        if element_name == 0:
            date_raw = source_code_subset
        elif attribute_name == 0 and attribute_value == 0:
            date_raw = source_code_subset.find(element_name)
        else:
            date_raw = source_code_subset.find(element_name, {attribute_name:attribute_value})
        
        try:
            date_text = date_raw.get_text().strip()
        except AttributeError: # date_raw is None
            return (0, 0)
        
        try:
            '''
            2022.04.05
            add a 'repalce' function to fix the date error in hk_recentpressrelease
            '''
            # date_datetime = datetime.datetime.strptime(date_raw.get_text().strip(), date_regex)
            date_text = date_raw.get_text().strip().replace("--","-")
            date_datetime = datetime.datetime.strptime(date_text, date_regex)
        except ValueError: # usually because of unconverted data (e.g. extra words other than the dates)
            date_regex_reformatted = 'date_regex' + date_regex.replace(' ', '').replace('/', '').replace('%', '_').replace('-', '').replace(',', '')
            date_search_result = re.search(eval(date_regex_reformatted), date_text).group()
            if date_search_result:
                date_datetime = datetime.datetime.strptime(date_search_result, date_regex)
            else: # can't find a date
                return (0, 0)
        date = date_datetime.strftime("%Y/%m/%d")

        if datetime.datetime.today().year != date_datetime.year or (datetime.datetime.today() - date_datetime).days > 7:
            # print(date, 1)
            return (date, 1)
        else:
            # print(date, 0)
            return (date, 0)
    
    except NameError:
        print('Unable to scrape date from current URL')
        return (0,0)


'''
2022.04.20
new function for OCR
'''
## used
def image_pdf_to_text_pytesseract(PDF_file,agency,webpage):
    from PIL import Image
    import pytesseract
    from pdf2image import convert_from_path

    '''
    Part #1 : Converting PDF to images
    '''
    
    # Store all the pages of the PDF in a variable
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    pytes_path = str(os.path.dirname(os.getcwd()))+'\system\poppler-0.68.0\bin'
    pytes_path = str(pytes_path).replace('\x08', r'\b')
    pages = convert_from_path(PDF_file, 500,poppler_path = pytes_path)
      
    # Counter to store images of each page of PDF to image
    image_counter = 1
    
    country = agency.split('-')[1].strip()
    pic_folder_directory_higher = '../results/pictures/' + country + '/'
    if not os.path.exists(pic_folder_directory_higher):
        print('folder ' + pic_folder_directory_higher + ' not found, creating it...')
        os.makedirs(pic_folder_directory_higher)

    pic_folder_directory = '../results/pictures/' + country + '/' + webpage + '/'
    if not os.path.exists(pic_folder_directory):
        print('folder ' + pic_folder_directory + ' not found, creating it...')
        os.makedirs(pic_folder_directory)
    
    # filename =  pic_folder_directory + date_cleaned + '_' + title_cleaned + '.jpg'
    # r = requests.get(url, stream=True)

    
    # Iterate through all the pages stored above
    for page in pages:
      
        # Declaring filename for each page of PDF as JPG
        filename = pic_folder_directory+"page_"+str(image_counter)+".jpg"
          
        # Save the image of the page in system
        page.save(filename, 'JPEG')
        image_counter = image_counter + 1
    
    
    '''
    Part #2 - Recognizing text from the images using OCR
    '''
    # Variable to get count of total number of pages
    filelimit = image_counter-1 
    # Iterate from 1 to total number of pages
    
    '''
    '''
    
    pytes_path = str(os.path.dirname(os.getcwd()))+'\system\Tesseract-OCR\tesseract.exe'
    pytes_path = pytes_path.replace('\t', r'\t')
    pytesseract.pytesseract.tesseract_cmd = pytes_path
    all_text = []
    for i in range(1, filelimit + 1):
        filename = pic_folder_directory+ "page_"+str(i)+".jpg"
              
        # Recognize the text as string in image using pytesserct
        text = str(((pytesseract.image_to_string(Image.open(filename)))))
        text = text.replace('-\n', '')   
        all_text.append(text)
        os.remove(filename)
        print(filename,'is removed')
    final_text = ''.join(all_text)
    text_cleaned = final_text.replace('\n', ' ')
    text_cleaned = text_cleaned.replace(r'|', ' ')
    text_cleaned = re.sub('\s*We build a healthy Hong Kong and aspire to be an internationally renowned public health authority not intended to serve as guidelines or to replace professional clinical judgement\.\s*', ' ',text_cleaned)
    text_cleaned = re.sub('DEPARTMENT OF HEALTH DRUG OFFICE.*\(IN REPLY PLEASE QUOTE THIS FILE REF\.\)\s*','',text_cleaned)
    text_cleaned = re.sub('\s*Please note that this letter serves as a mean for the DH.*','',text_cleaned)
    text_cleaned = re.sub(r'http[s]?(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),\s]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', ' ', text_cleaned)
    return text_cleaned

## used
def image_pdf_to_text_easyocr(PDF_file,agency,webpage):
    import easyocr
    # from PIL import Image
    # import sys
    from pdf2image import convert_from_path
    
    # PDF_file = '../results/pdf/HK DOH/Letters to Healthcare Providers/2022_04_19_ANAGRELIDE_HYDROCHLORIDE_Components_Pharmaceutical_Security_Information_Chinese_Only.pdf'
    
    # pages = convert_from_path(PDF_file, 500,poppler_path=r'.\system\poppler-0.68.0\bin')
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    pages_path = str(os.path.dirname(os.getcwd()))+'\system\poppler-0.68.0\bin'
    pages_path = str(pages_path).replace('\x08', r'\b')
    pages = convert_from_path(PDF_file, 500,poppler_path = pages_path)
    
    # Counter to store images of each page of PDF to image
    image_counter = 1
    country = agency.split('-')[1].strip()
    pic_folder_directory_higher = '../results/pictures/' + country + '/'
    if not os.path.exists(pic_folder_directory_higher):
        print('folder ' + pic_folder_directory_higher + ' not found, creating it...')
        os.makedirs(pic_folder_directory_higher)

    pic_folder_directory = '../results/pictures/' + country + '/' + webpage + '/'
    if not os.path.exists(pic_folder_directory):
        print('folder ' + pic_folder_directory + ' not found, creating it...')
        os.makedirs(pic_folder_directory)
    
    # filename =  pic_folder_directory + date_cleaned + '_' + title_cleaned + '.jpg'
    # r = requests.get(url, stream=True)

    
    # Iterate through all the pages stored above
    for page in pages:
      
        # Declaring filename for each page of PDF as JPG
        filename = pic_folder_directory+"page_"+str(image_counter)+".jpg"
          
        # Save the image of the page in system
        page.save(filename, 'JPEG')
        image_counter = image_counter + 1
    
    '''
    Part #2 - Recognizing text from the images using OCR
    '''
    # Variable to get count of total number of pages
    filelimit = image_counter-1
    reader = easyocr.Reader(['ch_tra','en'])
    all_text = []
    combined_result = []
    # os.chdir(os.path.dirname(os.path.realpath(__file__)))
    # os.chdir(r'C:\Users\Huang Yiting\OneDrive\webcrawling_without_SARTAN')
    for i in range(1, filelimit + 1):
        filename = pic_folder_directory+"page_"+str(i)+".jpg"
        # print(filename)
              
        # Recognize the text as string in image using easyocr
        result = reader.readtext(filename)
        all_text.extend(result)
        os.remove(filename)
        print(filename,'is removed')
    for i in all_text:
        detail = i[1]
        combined_result.append(detail)
    final = ''.join(combined_result)
    print(final)
    final_cleaned = final.replace('\'', ', ')
    final_cleaned = re.sub(r'衛生署藥物辦公室.*PLEASE QUOTE THIS FILE REF.','',final_cleaned)
    final_cleaned = re.sub(r'我們要建設個健康的香港並立志成為國際知名的公共衛生監管機構',' ',final_cleaned)
    final_cleaned = re.sub(r'http[s]?(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),\s]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', ' ', final_cleaned)
    final_cleaned = re.sub(r'請向衛生署藥物不良反應分組報告由藥物引起的任何不良事件.*', '', final_cleaned)
    print('before trans text/n',final_cleaned)
    print('end')
    final_trans = chinese_to_english(final_cleaned)
    final_trans = re.sub('[^\x00-\x7F] *',"",final_trans)
    print('after trans text/n',final_trans)
    return final_trans
            
    
## used
def extract_information_layer2_pdf(title, agency, webpage, date, url):
    """
    """

    try:
        filename = download_layer2_pdf(title, agency, webpage, date, url)

        import tika
        tika.initVM()
        # tika.TikaClientOnly = True
        
        from tika import parser
        
        '''
        2022.03.08
        add a try function for encoding latin-1 in hk_undeclared
        '''
        
        # try:
        body_text_raw = parser.from_file(filename)
        # except UnicodeEncodeError:
        #     body_text_raw = parser.from_file(filename).encode('utf-8').decode('latin-1')
        
        body_text = body_text_raw["content"]
        

        malay_website_list = ["Overseas reg - Malaysia MOH","Overseas reg - NPRA"]
        if body_text:
            # print(repr(body_text))
            body_text = body_text.strip()
            #if agency == "Overseas reg - Malaysia MOH":
            if agency in malay_website_list:
                print("List match")
                translated_text = malay_to_english(body_text)
                (case_description_text, truncation_flag) = clean_text(translated_text)
                # case_description_text = get_title(body_text, 0,0,0, language='malay')
            elif agency == "Overseas reg - HK DOH":
                translated_text = chinese_to_english(body_text)
                (case_description_text, truncation_flag) = clean_text(translated_text)
            else:
                (case_description_text, truncation_flag) = clean_text(body_text)
                # case_description_text = get_title(body_text, 0,0,0)
            return case_description_text

        else: # no text extracted, probably means only images in PDF. need OCR
            #ocr_case_description_text = ocr_for_pdf(filename)
            """Commeneted for now since error not fixed"""
            ocr_case_description_text = 'Unable to extract any text from PDF'


            if ocr_case_description_text:
                # print(ocr_case_description_text)
                #if agency == "Overseas reg - Malaysia MOH":
                if agency in malay_website_list:
                    print("List match")
                    translated_text = malay_to_english(ocr_case_description_text)
                    # print(translated_text)
                    (case_description_text, truncation_flag) = clean_text(translated_text)
                    # case_description_text = get_title(ocr_case_description_text, 0,0,0, language='malay')
                else:
                    (case_description_text, truncation_flag) = clean_text(ocr_case_description_text)
                    # case_description_text = get_title(ocr_case_description_text, 0,0,0)
                return case_description_text

            else:
                print('Unable to extract any text from PDF')
                return '-'

    except NameError:
        print('Unable to get PDF file from Layer 2...')
        return '-'

## used
def download_layer2_pdf(title, agency, webpage, date, url):
    """
    """

    try:
        url = url.replace(' ','%20')
        '''
        2022.04.21
        add codes to translate title of PDF for ocr reading
        '''
        title_cleaned = title.replace('\n','_').replace('\r','_').translate(str.maketrans({a:None for a in string.punctuation})).replace(' ','_')[:100]
        title_trans = chinese_to_english(title_cleaned)
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
        
        # filename = pdf_folder_directory + date_cleaned + '_' + title_cleaned + '.pdf'
        filename = pdf_folder_directory + date_cleaned + '_' + title_trans + '.pdf'
        r = requests.get(url, stream=True)
        with open(filename, 'wb') as f:
            f.write(r.content)
        
        return filename

    except NameError:
        print('Unable to obtain PDF file from layer 2 URL!')
        return 0
 
## used
def get_description(source_code_subset, element_name, attribute_name, attribute_value, language='english', tag = "Other"):
    """
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
                """
                2022.02.10 
                for health Canada, extract affected product information table
                """
                table_text = table.get_text().strip().replace('\n', ' ')
                #print(table_text)
                
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
        #print(description_cleaned)
        
        """
        2022.02.10 
        for health Canada, add table information for affacted produce
        """
        #tag = "Health Canada_recalls and alert"
        if tag == "Health Canada_recalls and alert":
            print(True)
            description_cleaned = str(description_cleaned.replace('Affected products ', 'Affected products: '+table_text))
        else:
            description_cleaned = description_cleaned
            
        #print(description_cleaned)

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
     
### not used
# def save_image(title, source_code, agency, webpage, date, url):
#     """
#     From source code, look for images and download if present. 
#     Images are saved in the respective folder in /results/pictures/<website>/
#     """
#     try: # can't have a general code because it will very likely create false positives (like website header image, logo, etc)
#         title_cleaned = title.replace('\n','_').replace('\r','_').translate(str.maketrans({a:None for a in string.punctuation})).replace(' ','_')[:100]
#         date_cleaned = date.replace('/','_')
#         country = agency.split('-')[1].strip()
#         image_folder_directory_higher = '../results/pictures/' + country + '/'
#         if not os.path.exists(image_folder_directory_higher):
#             print('folder ' + image_folder_directory_higher + ' not found, creating it...')
#             os.makedirs(image_folder_directory_higher)

#         image_folder_directory = '../results/pictures/' + country + '/' + webpage + '/'
#         if not os.path.exists(image_folder_directory):
#             print('folder ' + image_folder_directory + ' not found, creating it...')
#             os.makedirs(image_folder_directory)
    
#         if country == 'Australia TGA': # assuming only 1 image per section
#             images_raw = source_code.find_all("div", {"class" : "file file-image file-image-png"})
#             for i, image in enumerate(images_raw):
#                 image_link = image.find_all('img')[0]['src']
#                 image_extension = image_link.split('.')[-1]
#                 try:
#                     urllib.request.urlretrieve(image_link, image_folder_directory + date_cleaned + '_' + title_cleaned + '_' + str(i) + '.' + image_extension)
#                 except (urllib.error.HTTPError, urllib.error.URLError):
#                     print('using requests instead to dl image for mmoh')
#                     downloaded_file = requests.get(image_link)
#                     f = open(image_folder_directory + date_cleaned + '_' + title_cleaned + '_' + str(i) + '.' + image_extension, 'wb')
#                     f.write(downloaded_file.content)
#                     f.close()

#         elif country == 'Health Canada':
#             images_raw = source_code.find("div", {"id" : "awr_details_container"})
#             image_links = images_raw.find_all('img')
#             for i, image in enumerate(image_links):
#                 #print(i, image)
#                 image_link = urljoin(url, image['src'])  
#                 if 'rsam' in image_link:
#                     continue
#                 image_extension = image_link.split('.')[-1]
#                 try:
#                     urllib.request.urlretrieve(image_link, image_folder_directory + date_cleaned + '_' + title_cleaned + '_' + str(i) + '.' + image_extension)
#                 except (urllib.error.HTTPError, urllib.error.URLError):
#                         print('using requests instead to dl image for mmoh')
#                         downloaded_file = requests.get(image_link)
#                         f = open(image_folder_directory + date_cleaned + '_' + title_cleaned + '_' + str(i) + '.' + image_extension, 'wb')
#                         f.write(downloaded_file.content)
#                         f.close()
        
#         elif country == 'FDA':
#             if webpage == "Tainted Sexual Enhancement Products" or webpage == "Tainted Weight Loss Products" or webpage == "MedWatch" or webpage == "Drug Recalls":
#                 images_raw = source_code.find_all('img', {'typeof':'foaf:Image'})
#                 for i, image in enumerate(images_raw):
#                     image_link = urljoin(url, image['src'])
#                     image_extension = image_link.split('.')[-1].split('?')[0] # there's some weird ?itok=... after jpg
#                     try:
#                         urllib.request.urlretrieve(image_link, image_folder_directory + date_cleaned + '_' + title_cleaned + '_' + str(i) + '.' + image_extension)
#                     except (urllib.error.HTTPError, urllib.error.URLError):
#                         print('using requests instead to dl image for mmoh')
#                         downloaded_file = requests.get(image_link)
#                         f = open(image_folder_directory + date_cleaned + '_' + title_cleaned + '_' + str(i) + '.' + image_extension, 'wb')
#                         f.write(downloaded_file.content)
#                         f.close()
            
#             elif webpage == "Tainted Arthritis Pain Products": # <img style="-webkit-user-select: none;" src="https://www.fda.gov/media/91685/download"> so no obvious ext given in the URL, need to hardcode
#                 images_raw = source_code.find_all('img', {'class' : 'img-responsive pull-right frame-white'})
#                 for i, image in enumerate(images_raw):
#                     image_link = urljoin(url, image['src'])
#                     # image_extension = image_link.split('.')[-1].split('?')[0] # there's some weird ?itok=... after jpg
#                     try:
#                         urllib.request.urlretrieve(image_link, image_folder_directory + date_cleaned + '_' + title_cleaned + '_' + str(i) + '.jpg')
#                     except urllib.error.HTTPError:
#                         print('using requests instead to dl image for mmoh')
#                         downloaded_file = requests.get(image_link)
#                         f = open(image_folder_directory + date_cleaned + '_' + title_cleaned + '_' + str(i) + '.' + image_extension, 'wb')
#                         f.write(downloaded_file.content)
#                         f.close()

#             else:
#                 pass
#         elif country == "UK MHRA":
#             images_raw = source_code.find_all("img", {"class" : "app-c-figure__image"})            # app-c-figure__image
#             for i, image in enumerate(images_raw):
#                 image_link = urljoin(url, image['src'])
#                 image_extension = image_link.split('.')[-1]
#                 try:
#                     urllib.request.urlretrieve(image_link, image_folder_directory + date_cleaned + '_' + title_cleaned + '_' + str(i) + '.' + image_extension)
#                 except (urllib.error.HTTPError, urllib.error.URLError):
#                     print('using requests instead to dl image for mmoh')
#                     downloaded_file = requests.get(image_link)
#                     f = open(image_folder_directory + date_cleaned + '_' + title_cleaned + '_' + str(i) + '.' + image_extension, 'wb')
#                     f.write(downloaded_file.content)
#                     f.close()

#         elif country == 'HK DOH':
#             images_raw = source_code.find_all("div", {"class" : "pad10"})
#             for i, image in enumerate(images_raw):
#                 image_links = image.find_all('img') # not same root
#                 for link in image_links:
#                     image_link = link['src']
#                     image_extension = image_link.split('.')[-1]
#                     try:
#                         urllib.request.urlretrieve(image_link, image_folder_directory + date_cleaned + '_' + title_cleaned + '_' + str(i) + '.' + image_extension)
#                     except (urllib.error.HTTPError, urllib.error.URLError):
#                         print('using requests instead to dl image for mmoh')
#                         downloaded_file = requests.get(image_link)
#                         f = open(image_folder_directory + date_cleaned + '_' + title_cleaned + '_' + str(i) + '.' + image_extension, 'wb')
#                         f.write(downloaded_file.content)
#                         f.close()
        
#         elif country == 'Malaysia MOH':
#             images_raw = source_code.find_all("div", {"id" : "page_content"})
#             for i, image in enumerate(images_raw):
#                 image_links = image.find_all('img') # not same root
#                 for link in image_links:
#                     original_link = link['src']
#                     cleaned_link = original_link.replace(' ','%20')
#                     image_link = urljoin(url, '/' + cleaned_link)
#                     image_extension = image_link.split('.')[-1]
#                     if 'assets/shared/images' in image_link:
#                         continue # skip images of icons we are not interested in 
#                     try:
#                         urllib.request.urlretrieve(image_link, image_folder_directory + date_cleaned + '_' + title_cleaned + '_' + str(i) + '.' + image_extension)
#                     except (urllib.error.HTTPError, urllib.error.URLError):
#                         print('using requests instead to dl image for mmoh')
#                         downloaded_file = requests.get(image_link)
#                         f = open(image_folder_directory + date_cleaned + '_' + title_cleaned + '_' + str(i) + '.' + image_extension, 'wb')
#                         f.write(downloaded_file.content)
#                         f.close()
#         else:
#             pass

#         return 

#     except (IndexError, AttributeError):
#         print('No images found in ' + title_cleaned)
#         return


def save_pdf(title, source_code, agency, webpage, date, url, element_name, attribute_name, attribute_value):
    """
    Retrieves the PDFs that are present in the webpage (not the PDF of the website itself - for that there's generate_pdf_from_url)
    """
    try: 
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

        check_for_pdf = source_code.find_all(element_name, {attribute_name : attribute_value})
        if check_for_pdf:
            print('pdf found in ' + title)
            for i, pdf in enumerate(check_for_pdf):
                link_raw = pdf.find("a", href=True)
                    
                """Added by Prem"""
                link = link_raw["href"].replace(' ','%20')
                #print(link)
                try:
                    urllib.request.urlretrieve(link, pdf_folder_directory + date_cleaned + '_' + title_cleaned + '_' + str(i) + '.pdf')
                except urllib.error.HTTPError:
                    downloaded_file = requests.get(link)
                    f = open(pdf_folder_directory + date_cleaned + '_' + title_cleaned + '_' + str(i) + '.pdf', 'wb')
                    f.write(downloaded_file.content)
                    f.close()
    except (NameError, requests.exceptions.ChunkedEncodingError):
        print('Additional .pdf file not downloaded for ' + agency + ' ' + webpage)
        print(title)

    return

## used
def generate_pdf_from_url(title, url, agency, webpage, date, case_description_text=None):
    """
    Similar to how we usually print webpages to PDF 

    Given a URL of the webpage, 
    """

    try: 
        #print(url)

        
        if 'pdf' == url.split('.')[-1]:
            print("The webpage is a PDF file. Cannot use pdfkit. Using requests.")
            download_layer2_original_pdf(title, url, agency, webpage, date)
            # return

        title_cleaned = title.replace('\n','_').replace('\r','_').translate(str.maketrans({a:None for a in string.punctuation})).replace(' ','_')[:100]
        """
        2022.02.17 turn some date(int) into str
        """
        date = str(date)
        date_cleaned = date.replace('/','_')
        country = agency.split('-')[1].strip()

        original_pdf_folder_directory_higher = '../results/original_pdf/' + country + '/'
        print(original_pdf_folder_directory_higher)
        
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
            config = pdfkit.configuration(wkhtmltopdf = path_wkthmltopdf)
            #option : disable-javascript option to expand checklists/drop downs/etc in page. Eg: TGA Compmed page
            options = {'quiet':'','disable-javascript':''}
            
            # pdfkit.from_url(url,original_pdf_folder_directory + date_cleaned + '_' + title_cleaned[0:30] + '_'+ title_cleaned[-15:] + '_' + str(random.randint(0,100)) + '.pdf',configuration=config, options = options)
            pdf_web = original_pdf_folder_directory + date_cleaned + '_' + title_cleaned[0:30] + '_'+ title_cleaned[-15:] + '_' + str(random.randint(0,100)) + '.pdf'
            pdfkit.from_url(url,pdf_web,configuration=config, options = options)
            
            print("PDF generated using pdfkit")
            
        except Exception:
            print("Error Occured in generate_pdf_from_url")

    except NameError:
        print('.pdf file not generated for ' + agency + ' ' + webpage)
        print(title)

    return 

## used
def download_layer2_original_pdf(title, url, agency, webpage, date):
    """
    Given the URL for the PDF file, download and save the PDF in original_pdf folder.
    Function similar to download_layer2_pdf except the destination folder. 
    download_layer2_pdf saves the file in 'pdf' folder.
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

## used
def generate_txt_case_description(title, case_desc, agency, webpage, date):
    """
    Excel has a character limit, so when there's >30k characters, we will generate a txt of the case description instead
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
        
        #filename_to_write =  os.path.join(long_case_description_pdf_folder_directory, date_cleaned + '_' + title_cleaned[1:30] + '.txt')
        with open(long_case_description_pdf_folder_directory + date_cleaned + '_' + title_cleaned[0:30] + '.txt', 'w', encoding="utf-8") as f:
            f.write(str(case_desc))
        #with open(filename_to_write, 'w', encoding="utf-8") as f:
            #f.write(case_desc)
    except NameError:
        print('.txt file not generated for ' + agency + ' ' + webpage)
        print(title)
    
    return

### not meaningful but used
def perform_text_classification(case_desc):
    """
    Does Sartan keyword check as well (should move this away eventually, maybe as a separate function)

    Check whether keywords (linked to LLT meddra classes) are inside the case desc 
    If not, use saved xgboost model to predict the correct class 
    """
    """for word in sartan_keywords:
        if word in case_desc:
            print(f"\nSartan-related keyword found: {word}\n")

    list_of_keywords = keywords.keys()
    # print(list_of_keywords)
    for word in list_of_keywords:
        if word in case_desc:
            print(f'keyword matched: {word}, matched class is {keywords[word]}')
            return keywords[word]
    
    print("No keywords found, using xgboost model")

    classifier = joblib.load('../data/classificationmodel.pkl')
    # print(case_desc[:300])
    cleaned_case_desc = ' '.join([item for item in case_desc.split() if item not in stopwords])
    # print(cleaned_case_desc[:300])
    y_pred = classifier.predict([cleaned_case_desc])
    # print(y_pred)
    return y_pred[0] """ # it's in a list 
    return "To be filled later"

if __name__ == "__main__":
    perform_text_classification("Trying out sartan")