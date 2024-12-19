import requests

import asyncio
import aiohttp

import time
import random

from pprint import pprint

from utils import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ElsevierAPISession:
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def __init__(self, api_key):
               
        self.headers = {"X-ELS-APIKey"  : api_key,
                        "Accept"        : 'application/json'}
        
        self.is_idle = True
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def __str__(self):
        
        return f'API Key: {self.headers["X-ELS-APIKey"]}'
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def __repr__(self):
        
        return self.__str__()
        
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def run_test_query( self,
                        query_dict : dict):
        
        self.is_idle = False
        
        print(f'Running job {query_dict["job_id"]}')
        pprint(query_dict)
        time.sleep(random.uniform(1., 5.))
        print(f'Completed job {query_dict["job_id"]}')
        
        self.is_idle = True
        
        return {"status": "completed",
                "job_id": query_dict['job_id'],
                "results": {}}        
           
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def get_total_results(self, response_dict : dict) -> int:
    
        return int(response_dict[SEARCH_RESULTS_RESPONSE_DICT_KEY][TOTAL_RESULTS_RESPONSE_DICT_KEY])
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def run_query(self,
                  query_dict : dict):
        
        status = 'completed'
        first_time = True
               
        results_dict = {'total_results' : 0,
                        'results' : []}
         
        start_index = query_dict['start_index']
                        
        while first_time or (results_dict['total_results'] > start_index):
                        
            request_url = self.generate_url(query_dict=query_dict,
                                            start_index=start_index)    

            response = requests.get(request_url,
                                    headers=self.headers)
        
            if first_time:
                first_time = False
                results_dict['total_results'] = self.get_total_results(response.json())
                
            if response.status_code != 200:
                status = f'failed with status code {response.status_code}'
                break
            
            for item in response.json()[SEARCH_RESULTS_RESPONSE_DICT_KEY][ENTRY_RESPONSE_DICT_KEY]:
                results_dict['results'].append(item)
                
            start_index += RESULTS_PER_REQUEST
            
        return {'job_id' : query_dict['job_id'],
                'query_results' : results_dict,
                'status' : status}
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def generate_url(self,
                    query_dict : dict,
                    start_index) -> str:
    
        issn = query_dict['issn']
        eissn = query_dict['eissn']
        keyword = query_dict['keyword']
            
        query_string = 'query='
        
        # search for articles from specific journal based on ISSN or EISSN
        if issn is not None:
            query_string += f'{API_FIELD_RESTRICION_ISSN}({issn}) AND '
        else:
            query_string += f'{API_FIELD_RESTRICION_EISSN}({eissn}) AND '
        
        # search for articles from specific year
        query_string += f'{API_FIELD_RESTRICION_PUBYEAR} > {YEAR_START} AND {API_FIELD_RESTRICION_PUBYEAR} < {YEAR_END} AND '
        
        # search for articles with specific keywords in Title, Abstract and Keywords
        query_string += self.add_keywords(keyword)
        
        # search for articles from specific source type (journal and trade journal)
        # query_string += f' AND {API_FIELD_RESTRICION_SRCTYPE}(j,d)'
        
        # add start for pagination
        query_string +=f'&{API_FIELD_START}={start_index}'
        
        # add number of results per request
        query_string +=f'&count={RESULTS_PER_REQUEST}'
            
        query_string += '&view=complete'

        return URL_BASE + f'{query_string}'
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def add_keywords(self,
                    keyword : str)-> str:

        keyword_query = ''
        
        for form in get_all_forms(keyword):
            keyword_query += f'\"{form}\" OR '
    
        return f'{API_FIELD_RESTRICION_TITLE_ABS_KY}({keyword_query[:-4]})'
        
# =================================================================================

def main():
    
    sess = ElsevierAPISession(api_key=API_KEYS[0])
    
    query_dict = {  'eissn': '1467-629X',
                    'issn': '0810-5391',
                    'job_id': 582,
                    'keyword': 'Algorithm',
                    'start_index': 0}
        
    result = sess.run_query(query_dict)

    job_id = result['job_id']
    total_results = result['query_results']['total_results']
    
    print(f'Job {job_id} complete. {total_results} results found.')

    pprint(result)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == '__main__':
    main()    
    