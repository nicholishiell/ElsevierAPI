import requests
from pprint import pprint

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

API_KEY = '5c2c30b984e5d89aac97203a39827ca2'
URL_BASE = "https://api.elsevier.com/content/search/scopus?" 

PUBLICATION_RESPONSE_DICT_KEY = 'prism:publicationName'

API_FIELD_RESTRICION_EISSN =        'EISSN' # Electronic International Standard Serial Number
API_FIELD_RESTRICION_ISSN =         'ISSN' # International Standard Serial Number
API_FIELD_RESTRICION_PUBYEAR =      'PUBYEAR' # Publication Year
API_FIELD_RESTRICION_SRCTYPE =      'SRCTYPE' # Source Type (j : journal, b : book, k : book series, p : conference, r : report, d : trade journal)
API_FIELD_RESTRICION_TITLE_ABS_KY = 'TITLE-ABS-KEY' # Title, Abstract and Keywords

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def generate_url(query_dict):
    
    query_string = ''
    
    for key, value in query_dict.items():
        query_string += f'{key}({value}) AND '
    
    query_string = f'{API_FIELD_RESTRICION_ISSN}(0001-3072)&{API_FIELD_RESTRICION_TITLE_ABS_KY}(machine-learning)'
        
    query_string += '&view=complete'

    return URL_BASE + f'query={query_string}'

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def execute_request(headers, query):
        
    request_url = generate_url(query)    
    
    print(f'Request URL: {request_url}')
    
    response = requests.get(request_url,
                            headers=headers)
      
    if response.status_code == 200:
        return response.json()
    else:
        print('ERROR: ', response.status_code)
        return None

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def main():

    headers_dict = {"X-ELS-APIKey"  : API_KEY,
                    "Accept"        : 'application/json'}
        
    query_dict = {  'ISSN' : '0001-3072',
                    'EISSN' : '0001-3072',
                    'PUBYEAR' : 2020,
                    'TITLE-ABS-KEY' : 'machine-learning'}

    response = execute_request(headers=headers_dict, 
                               query=query_dict)

    if response is not None:    
        for item in response['search-results']['entry']:
            publication_name = item[PUBLICATION_RESPONSE_DICT_KEY]
            print(f'Publication: {publication_name}')
            
    
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == '__main__':
    main()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~