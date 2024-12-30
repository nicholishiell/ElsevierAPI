import csv
import requests
from pprint import pprint

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

DATA_BASE_FILE_PATH = "database-files/test-db.db"

JOURNALS_FILE_PATH = './resources/journals.csv'
KEYWORDS_FILE_PATH = './resources/keywords.txt'
API_KEYS_FILE_PATH = './resources/api-keys.txt'

URL_BASE = "https://api.elsevier.com/content/search/scopus?" 

YEAR_START = 1999
YEAR_END = 2025
YEAR_RANGE = range(YEAR_START, YEAR_END)

RESULTS_PER_REQUEST = 25

TOTAL_RESULTS_RESPONSE_DICT_KEY = 'opensearch:totalResults'
START_INDEX_RESPONSE_DICT_KEY = 'opensearch:startIndex'

PUBLICATION_RESPONSE_DICT_KEY = 'prism:publicationName'
DATE_RESPONSE_DICT_KEY = 'prism:coverDate'
TITLE_RESPONSE_DICT_KEY = 'dc:title'
ABSTRACT_RESPONSE_DICT_KEY = 'dc:description'
KEYWORDS_RESPONSE_DICT_KEY = 'authkeywords'
AUTHORS_RESPONSE_DICT_KEY = 'author'
DOI_RESPONSE_DICT_KEY = 'prism:doi'

REQUIRED_RESPONSE_KEYS = [  PUBLICATION_RESPONSE_DICT_KEY,
                            DATE_RESPONSE_DICT_KEY,
                            TITLE_RESPONSE_DICT_KEY,
                            ABSTRACT_RESPONSE_DICT_KEY,
                            KEYWORDS_RESPONSE_DICT_KEY,
                            AUTHORS_RESPONSE_DICT_KEY,
                            DOI_RESPONSE_DICT_KEY]

RESPONSE_TOTAL_RESULTS_KEY = 'opensearch:totalResults'

SEARCH_RESULTS_RESPONSE_DICT_KEY = 'search-results'
ENTRY_RESPONSE_DICT_KEY = 'entry'

API_FIELD_RESTRICION_EISSN =        'eissn' # Electronic International Standard Serial Number
API_FIELD_RESTRICION_ISSN =         'issn' # International Standard Serial Number
API_FIELD_RESTRICION_PUBYEAR =      'pubyear' # Publication Year
API_FIELD_RESTRICION_SRCTYPE =      'srctype' # Source Type (j : journal, b : book, k : book series, p : conference, r : report, d : trade journal)
API_FIELD_RESTRICION_TITLE_ABS_KY = 'title-abs-key' # Title, Abstract and Keywords
API_FIELD_START =                   'start' # start for pagination

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def load_journals(file_path = JOURNALS_FILE_PATH):
    
    journals = []
    
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        
        for row in reader:
            journals.append({'title' : row[0],
                            'publisher' : row[1],
                            'issn' : row[2],
                            'eissn' : row[3]})

    return journals

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def load_keywords(file_path = KEYWORDS_FILE_PATH):
    
    keywords = []
    
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        
        for row in reader:
            keywords.append(row[0])
            
    return keywords

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def get_all_forms(keyword: str) -> list:
    
    keyword = keyword.lower()
      
    forms = []
    
    forms.append(keyword)
    forms.append(keyword.replace(' ', '-'))
    forms.append(keyword.replace('-', ' '))
    
    upper_forms = []
    
    for item in forms:
        upper_forms.append(item.capitalize())
        upper_forms.append(item.upper())
    
    forms = forms + upper_forms
    
    return list(set(forms))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def run_test_query_dict():
 
    request_url = 'https://api.elsevier.com/content/search/scopus?query=title-abs-key(family) AND issn(0001-3072) AND pubyear is 2020&start=0&count=25&view=complete'
    response = requests.get(request_url,
                            headers=REQUEST_HEADER_DICT)
      
    if response.status_code != 200:
        print('ERROR: ', response.status_code)
        pprint(response.json())
        return None
   
    for item in response.json()[SEARCH_RESULTS_RESPONSE_DICT_KEY][ENTRY_RESPONSE_DICT_KEY]:
       
        if 'error' in item:
            print(item['error'])
            continue

        print(item['dc:title'])
        print(item['prism:coverDate'])
        print(item['prism:publicationName'])
        # print(item['dc:description'])
        input()

