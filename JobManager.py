from concurrent.futures import ThreadPoolExecutor, as_completed

from DataBaseInterface import DataBaseInterface
from utils import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class JobManager:
    
    def __init__(self,
                 session_list : list,
                 data_base_file_path = DATA_BASE_FILE_PATH):
        
        self.db_interface = DataBaseInterface(data_base_file_path)
        self.sessions_list = session_list
       
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def job_complete(self, 
                     future,
                     verbose = True):
        
        result = future.result()
        
        job_id = result['job_id']
        query_results = result['query_results']['results']
        total_results = result['query_results']['total_results']
        skipped = result['query_results']['skipped']
        status_code = int(result['query_results']['status_code'])       
        final_index = result['query_results']['final_index']
        
        if verbose:
            print(f'Job {job_id} returned status {status_code}. {total_results} records found. {skipped} record(s) skipped')
       
        if status_code == 200:       
            for response_entry in query_results: 
                # an error will be present in a successful response if no articles match the query         
                if 'error' not in response_entry:
                    self.db_interface.insert_result(response_entry)
                    
                self.db_interface.mark_job_complete(job_id) 
                
        elif status_code == 429:
            print('API limit reached.')
            self.db_interface.mark_job_not_in_progress(job_id, final_index)   
        else:
            print('Error: ', status_code)
            self.db_interface.mark_job_not_in_progress(job_id, final_index)
            
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def run_jobs(self):
                
        with ThreadPoolExecutor() as executor:
                   
            while self.db_interface.incomplete_jobs():
                
                futures = []
                
                for session in self.sessions_list:
                    
                    if not session.is_available():
                        continue
                                            
                    job_dict = self.db_interface.get_next_job()
                    
                    if job_dict is not None: 
                    
                        future = executor.submit(session.run_scopus_query, job_dict)
                        futures.append(future)
                        
                        self.db_interface.mark_job_in_progress(job_dict['job_id'])
                    
                for future in as_completed(futures):
                    self.job_complete(future)
                    
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def show_results(self) -> None:
        self.db_interface.show_results()
        
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def get_results(self) -> list:
        return self.db_interface.get_results()
              
                    
# ============================================================================