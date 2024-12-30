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
        
        self.quota_reached = False
        self.pause_util = 0
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def __str__(self):
        
        return f'API Key: {self.headers["X-ELS-APIKey"]}'
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def __repr__(self):
        
        return self.__str__()
                  
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def get_total_results(self, response_dict : dict) -> int:
    
        return int(response_dict[SEARCH_RESULTS_RESPONSE_DICT_KEY][TOTAL_RESULTS_RESPONSE_DICT_KEY])
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def get_query_results(self, response_dict : dict) -> list:
        
        return response_dict[SEARCH_RESULTS_RESPONSE_DICT_KEY][ENTRY_RESPONSE_DICT_KEY]
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def send_request(self,
                    request_url : str) -> dict:
        
        response = requests.get(request_url,
                                headers=self.headers)
               
        if response.status_code != 200:
            
            self.handle_error(response)
            
            return {'error' : { 'message' : f'failed with status code {response.status_code}',
                                'status_code' : response.status_code}}
            
        return response.json()
                    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def handle_error(   self,
                        response):
        
        if response.status_code == 429:
            self.quota_reached = True
            self.pause_until = int(response.headers['X-RateLimit-Reset'])

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def is_available(self):
        
        if self.quota_reached:
            if time.time() > self.pause_until:
                self.quota_reached = False
  
        return not self.quota_reached

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def is_error(   self,
                    response_dict : dict) -> bool:
            
        return 'error' in response_dict
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def check_item(self,
                   item : dict) -> bool:
               
        if 'error' in item:
            return False

        for key in REQUIRED_RESPONSE_KEYS:
            if key not in item:
                return False
             
        return True
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def handle_response(self,
                        response_dict : dict) -> list:
        
        results = []
        
        for item in self.get_query_results(response_dict):
            if self.check_item(item):               
                results.append(item)
           
        return results
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def run_scopus_query(   self,
                            query_dict : dict):
                       
        total_results = 0
        status_code = 200
        results = []
        
        start_index = query_dict['start_index']
                     
        while total_results > start_index or start_index == 0:
                        
            request_url = self.generate_url(query_dict=query_dict,
                                            start_index=start_index)    

            response = self.send_request(request_url)

            if not self.is_error(response):
                total_results = self.get_total_results(response)   
                results.extend(self.handle_response(response))  
                start_index += RESULTS_PER_REQUEST
            else:
                status_code = response['error']['status_code']
                break
            
        return {'job_id' : query_dict['job_id'],
                'query_results' : { 'results' : results,
                                    'total_results' : total_results,
                                    'skipped' : total_results - len(results),
                                    'final_index' : start_index,
                                    'status_code' : status_code}}
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def run_serial_title_query( self,
                                issn : str):
        
        request_url = f'https://api.elsevier.com/content/serial/title/issn/{issn}/?field=dc:publisher'
        response = self.send_request(request_url)
        
        print(response)
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def run_abstract_retrevial_query(   self,
                                        scopus_id : str):
        
        request_url = f'https://api.elsevier.com/content/abstract/scopus_id/{scopus_id}/'
        
        request_url += '?field=prism:publicationName'
        request_url += '?view=full&field=dc:title,prism:coverDate'
        
        response = self.send_request(request_url)
        
        pprint(response)   
    
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
        query_string += f' AND {API_FIELD_RESTRICION_SRCTYPE}(j OR d)'
                      
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
    
    sess = ElsevierAPISession(api_key='f3ddb33fcba5c1d11acb8d98e123163b')

    query_dict = {  'eissn': '1468-4489',
                    'issn': '0963-9284',
                    'job_id': 1,
                    'keyword': 'deep learning',
                    'start_index': 0}
        
    result = sess.run_scopus_query(query_dict)

    job_id = result['job_id']
    total_results = result['query_results']['total_results']
    
    print(f'Job {job_id} complete. {total_results} results found.')

    for response_entry in result['query_results']['results']:
        publisher = sess.run_serial_title_query(response_entry['prism:issn'])
    
        print(response_entry['prism:publicationName'])
        print(response_entry['dc:title'])
        print(response_entry['prism:coverDate'])
        print('------------------------------------')
    
    
    # sess.run_abstract_retrevial_query(scopus_id='84858315911')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == '__main__':
    main()    
    