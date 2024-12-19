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

def main():

    sessions_list = [ElsevierAPISession(api_key) for api_key in API_KEYS]    

    job_manager = JobManager(sessions_list)

    job_manager.run_jobs()   
    
    results = job_manager.get_results()
    
    with open('results.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['journal', 'year', 'title' , 'abstract', 'keywords', 'authors'])
        for result in results:
             writer.writerow([result[7],result[4],result[3],result[1],result[5],result[2]])
           
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == '__main__':
    main()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~