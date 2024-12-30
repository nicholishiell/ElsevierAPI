import logging

import sqlite3 
import asyncio
#import aiofiles

from pprint import pprint

from ElsevierAPISession import ElsevierAPISession
from utils import *
from JobManager import JobManager
import csv

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def load_elseveir_api_sessions(api_keys_file_path = API_KEYS_FILE_PATH):
    
    sessions_list = []
    
    with open(api_keys_file_path, 'r') as file:
        for line in file.readlines():
            sessions_list.append(ElsevierAPISession(api_key=line.strip()))
   
    return sessions_list
    
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def export_results_csv(results : list) -> None:
    
    with open('results.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['journal', 'year', 'title' , 'abstract', 'keywords', 'authors'])
        for result in results:
             writer.writerow([result[7],result[4],result[3],result[1],result[5],result[2]])

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def main():

    sessions_list = load_elseveir_api_sessions() 

    job_manager = JobManager(sessions_list)

    job_manager.run_jobs()   
    
    export_results_csv(job_manager.get_results())
           
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == '__main__':
    main()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~