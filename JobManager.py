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
       
        if verbose:
            print(f'Job {job_id} complete. {total_results} results found.')
        
        for response_entry in query_results:          
            if 'error' not in response_entry:
                pprint(response_entry)
                self.db_interface.insert_result(response_entry)
              
        self.db_interface.mark_job_complete(job_id)       
   
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def run_jobs(self):
                
        with ThreadPoolExecutor() as executor:
                   
            while self.db_interface.incomplete_jobs():
                
                futures = []
                for session in self.sessions_list:
                    
                    job_dict = self.db_interface.get_next_job()
                    
                    if job_dict is not None: 
                    
                        future = executor.submit(session.run_query, job_dict)
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