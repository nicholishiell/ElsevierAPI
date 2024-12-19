from utils import *
from generate_database import create_connection

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class DataBaseInterface:

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def __init__(   self,
                    data_base_file_path = DATA_BASE_FILE_PATH):
        
        self.db_conn = create_connection(data_base_file_path)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def extract_item(self, 
                     key : str,
                     response_entry : dict) -> str:
        
        # if type(response_entry) == dict:
        
        #     if key in response_entry.keys():
        #         return response_entry[key]
        # else:
        #     print(type(response_entry))
        #     print(response_entry)
        
        if key in response_entry.keys():
            return response_entry[key]
         
        return 'None'

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def extract_authors(self, 
                        authors_list : list) -> str:
        
        authors = ''
        
        for item in authors_list:
            surname = self.extract_item('surname', item)
            given_name = self.extract_item('given-name', item)
            authors += f'{surname}, {given_name}; '
        
        return authors

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def check_entry_exists(self,
                           result_data_dict : dict) -> bool:
        
        doi = self.extract_item(DOI_RESPONSE_DICT_KEY, result_data_dict)
        
        cursor = self.db_conn.cursor()
        
        cursor.execute("SELECT 1 FROM results WHERE doi = ?", (doi,))
        
        if cursor.fetchone():
            return True
        
        return False
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _insert_result( self,
                        result_data_dict : dict,
                        verbose = False) -> bool:
        
        journal = self.extract_item(PUBLICATION_RESPONSE_DICT_KEY, result_data_dict)
        year = self.extract_item(DATE_RESPONSE_DICT_KEY, result_data_dict)
        title = self.extract_item(TITLE_RESPONSE_DICT_KEY, result_data_dict)
        abstract = self.extract_item(ABSTRACT_RESPONSE_DICT_KEY, result_data_dict)
        keywords = self.extract_item(KEYWORDS_RESPONSE_DICT_KEY, result_data_dict)
        authors = self.extract_authors(self.extract_item(AUTHORS_RESPONSE_DICT_KEY, result_data_dict))
        doi = self.extract_item(DOI_RESPONSE_DICT_KEY, result_data_dict)
    
        cursor = self.db_conn.cursor()
        cursor.execute("""
            INSERT INTO results (journal, year, title, abstract, keywords, authors, doi)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (journal, year, title , abstract, keywords, authors, doi))
                
        self.db_conn.commit()
        
        if verbose:
            print(f' \"{journal}\", {year}, \"{title}\", \"{abstract}\", {keywords}, {authors}\n')   
    
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def insert_result(self, 
                      result_data_dict : dict) -> None:
        
        if not self.check_entry_exists(result_data_dict):
            self._insert_result(result_data_dict)
                  
        return True
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def incomplete_jobs(self) -> bool:
        
        cursor = self.db_conn.cursor()
        
        cursor.execute("SELECT 1 FROM jobs WHERE is_complete = 0 LIMIT 1")
        result = cursor.fetchone()
        
        return (result is not None)
           
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def _get_journal_eissn( self,
                            journal_id : int) -> str:
        
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT eissn FROM journal WHERE id = ?", (journal_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return None       
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def _get_journal_issn( self,
                            journal_id : int) -> str:
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT issn FROM journal WHERE id = ?", (journal_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return None       
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def _job_row_to_job_dict(   self,
                                row : tuple) -> dict:

        if row is None:
            return None

        job_id = row[0]
        keyword = row[2]
        start_index = row[5]
        journal_id = row[1]
        
        eissn = self._get_journal_eissn(journal_id)
        issn = self._get_journal_issn(journal_id)
     
        return {'job_id': job_id,
                'keyword': keyword,
                'start_index': start_index,
                'issn': issn,
                'eissn': eissn}  
        
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def get_next_job(self) -> dict:
                
        cursor = self.db_conn.cursor()
        
        cursor.execute("SELECT * FROM jobs WHERE is_complete = 0 AND in_progress = 0 LIMIT 1")
            
        return self._job_row_to_job_dict(cursor.fetchone())
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def mark_job_complete(  self,
                            job_id : int) -> None:
        
        cursor = self.db_conn.cursor()

        # Mark the job as in progress
        cursor.execute("UPDATE jobs SET is_complete = 1 WHERE id = ?", (job_id,))
        self.db_conn.commit()
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def mark_job_in_progress(   self,
                                job_id : int) -> None:
        
        cursor = self.db_conn.cursor()

        # Mark the job as in progress
        cursor.execute("UPDATE jobs SET in_progress = 1 WHERE id = ?", (job_id,))
        self.db_conn.commit()
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
       
    def show_results(self):
           
            cursor = self.db_conn.cursor()
            
            cursor.execute("SELECT * FROM results")
            rows = cursor.fetchall()
            
            for row in rows:
                print(row)
     
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
               
    def get_results(self) -> list:
        
        cursor = self.db_conn.cursor()
        
        cursor.execute("SELECT * FROM results")
        rows = cursor.fetchall()
        
        return rows

    
# ============================================================================