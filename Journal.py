class Journal:
    
    def __init__(self):
        self.title = None
        self.publisher = None
        self.issn = None
        self.eissn = None
        
    def __str__(self):
        return f'{self.title} ({self.issn}) ({self.eissn})'
    
    def __repr__(self):
        return f'{self.title} ({self.issn}) ({self.eissn})'
    
    @classmethod
    def from_dict(cls, journal_dict):
       
        journal = cls()
        journal.title = journal_dict['title']
        journal.publisher = journal_dict['publisher']
        
        if journal_dict['issn'] != '':
            journal.issn = journal_dict['issn']
        
        if journal_dict['eissn'] != '':
            journal.eissn = journal_dict['eissn']
        
        return journal
        
    def to_dict(self):
        return {'title' : self.title,
                'publisher' : self.publisher,
                'issn' : self.issn,
                'eissn' : self.eissn}