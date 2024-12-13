import logging
import requests

from pprint import pprint

from Journal import Journal
import csv

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

API_KEY = '5c2c30b984e5d89aac97203a39827ca2'
URL_BASE = "https://api.elsevier.com/content/search/scopus?" 

JOURNALS_FILE_PATH = './resources/journals.csv'
KEYWORDS_FILE_PATH = './resources/keywords.txt'

YEAR_RANGE = range(2000, 2024)

RESULTS_PER_REQUEST = 25

REQUEST_HEADER_DICT = {  "X-ELS-APIKey"  : API_KEY,
                         "Accept"        : 'application/json'}

PUBLICATION_RESPONSE_DICT_KEY = 'prism:publicationName'
TOTAL_RESULTS_RESPONSE_DICT_KEY = 'opensearch:totalResults'
START_INDEX_RESPONSE_DICT_KEY = 'opensearch:startIndex'
TITLE_RESPONSE_DICT_KEY = 'dc:title'

SEARCH_RESULTS_RESPONSE_DICT_KEY = 'search-results'
ENTRY_RESPONSE_DICT_KEY = 'entry'

API_FIELD_RESTRICION_EISSN =        'EISSN' # Electronic International Standard Serial Number
API_FIELD_RESTRICION_ISSN =         'ISSN' # International Standard Serial Number
API_FIELD_RESTRICION_PUBYEAR =      'PUBYEAR' # Publication Year
API_FIELD_RESTRICION_SRCTYPE =      'SRCTYPE' # Source Type (j : journal, b : book, k : book series, p : conference, r : report, d : trade journal)
API_FIELD_RESTRICION_TITLE_ABS_KY = 'TITLE-ABS-KEY' # Title, Abstract and Keywords
API_FIELD_START =                   'start' # start for pagination

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def generate_url(query_dict):
    
    query_string = 'query='
    
    # search for articles from specific journal based on ISSN or EISSN
    if query_dict[API_FIELD_RESTRICION_ISSN] is not None:
        query_string += f'{API_FIELD_RESTRICION_ISSN}({query_dict[API_FIELD_RESTRICION_ISSN]})&'
    else:
        query_string += f'{API_FIELD_RESTRICION_EISSN}({query_dict[API_FIELD_RESTRICION_EISSN]})&'
    
    # search for articles from specific year
    query_string += f'{API_FIELD_RESTRICION_PUBYEAR}({query_dict[API_FIELD_RESTRICION_PUBYEAR]})&'
    
    # search for articles with specific keywords in Title, Abstract and Keywords
    query_string += f'{API_FIELD_RESTRICION_TITLE_ABS_KY}({query_dict[API_FIELD_RESTRICION_TITLE_ABS_KY]})'
    
    # add cursor for pagination
    query_string +=f'&{API_FIELD_START}={query_dict[API_FIELD_START]}'
    
    # add number of results per request
    query_string +=f'&count={RESULTS_PER_REQUEST}'
    
    # search for articles from specific source type (journal and trade journal)
    query_string += f'{API_FIELD_RESTRICION_SRCTYPE})(j,d)'
    
    # query_string += '&view=complete'

    return URL_BASE + f'{query_string}'

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def execute_request(query):
        
    request_url = generate_url(query)    
    
    print(f'Request URL: {request_url}')
    
    response = requests.get(request_url,
                            headers=REQUEST_HEADER_DICT)
      
    if response.status_code == 200:
        return response.json()
    else:
        print('ERROR: ', response.status_code)
        pprint(response.json())
        return None

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def load_journals(file_path = JOURNALS_FILE_PATH):
    
    journals = []
    
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        
        for row in reader:
            journals.append(Journal.from_dict({'title' : row[0],
                                               'publisher' : row[1],
                                               'issn' : row[2],
                                               'eissn' : row[3]}))
            
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

# Name of the journal, year, title of the article, abstract, article keywords, authors

def extract_data_from_response(item):
    pass

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def run_queries(journal_list, keyword_list):
                
        for journal in journal_list:
            
            for keyword in keyword_list:
                
                for year in YEAR_RANGE:
                    
                    retrived_count = 0
                    total_results = 0
                    
                    while retrived_count < total_results or total_results == 0:
                    
                        query_dict = {  API_FIELD_RESTRICION_ISSN : journal.issn,
                                        API_FIELD_RESTRICION_EISSN : journal.eissn,
                                        API_FIELD_RESTRICION_PUBYEAR : year,
                                        API_FIELD_RESTRICION_TITLE_ABS_KY : keyword,
                                        API_FIELD_START : retrived_count}
                                        
                        response = execute_request(query=query_dict)
                        
                        if response is not None:
                            total_results = int(response[SEARCH_RESULTS_RESPONSE_DICT_KEY][TOTAL_RESULTS_RESPONSE_DICT_KEY])
                            retrived_count += RESULTS_PER_REQUEST
                                
                            for item in response[SEARCH_RESULTS_RESPONSE_DICT_KEY][ENTRY_RESPONSE_DICT_KEY]:
                                pprint(item)
                                input()
                                   
                        input(f'Press Enter to continue...{retrived_count} / {total_results}')
                        
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def main():

    logging.basicConfig(filename='elsevier-api.log', 
                        filemode='w', 
                        format='%(name)s - %(levelname)s - %(message)s', 
                        level=logging.DEBUG)
    
    journal_list = load_journals()
    keyword_list = load_keywords()    

    run_queries(journal_list, keyword_list)
    
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == '__main__':
    main()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~