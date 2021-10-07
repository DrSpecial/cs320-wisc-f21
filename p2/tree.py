# project: p2
# submitter: kxia7
# partner: none
# hours:

from zipfile import ZipFile
from io import TextIOWrapper
import csv

class ZippedCSVReader:
    def __init__(self, zipfile):
        with ZipFile(zipfile) as zf:
            self.path=[]
            for info in zf.infolist():
                self.path.append(info.filename)
            self.path.sort()
            self.zip = zipfile
            
    
    def rows(self, csv_file=None):
        with ZipFile(self.zip) as zf:
            if csv_file is not None:
                    with zf.open(csv_file) as csvfile:
                        reader = csv.DictReader(TextIOWrapper(csvfile))
                        for row in reader:
                            yield row
            else:
                for file in self.path:
                    with zf.open(file) as csvfile:
                        reader = csv.DictReader(TextIOWrapper(csvfile))
                        for row in reader:
                            yield row
                            
                            
class Loan:
    def __init__(self, amount, purpose, race, sex, income, decision):
        self.amount = amount
        self.purpose = purpose
        self.race = race
        self.sex = sex
        self.income = income
        self.decision = decision

    def __repr__(self):
        return f"Loan({self.amount}, {repr(self.purpose)}, {repr(self.race)}, {repr(self.sex)}, {self.income}, {repr(self.decision)})"

    def __getitem__(self, lookup):
        if hasattr(self, str(lookup)):
            return getattr(self, lookup)
        else:
            if lookup in list(self.__dict__.values()):
                return 1
            else:
                return 0


class Bank:
    def __init__(self, name, reader):
        self.name = name
        self.reader = reader
    
    def loans(self):
        for row in self.reader.rows():
            if self.name is None or row['agency_abbr'] == self.name:
                loan = Loan(int(row['loan_amount_000s']) if row['loan_amount_000s'] else 0, row['loan_purpose_name'], row['applicant_race_name_1'], row['applicant_sex_name'], int(row['applicant_income_000s']) if row['applicant_income_000s'] else 0, 'approve' if row['action_taken']==1 else 'deny')
                yield loan
    

def get_bank_names(reader):
    banks = set()
    for row in reader.rows():
        banks.add(row['agency_abbr'])
            
    return sorted(list(banks))


class SimplePredictor():
    def __init__(self):
        self.approved = 0
        self.denied = 0

    def predict(self, loan):
        if loan.purpose == 'Refinancing':
            self.approved += 1
            return True
        else:
            self.denied += 1
            return False

    def get_approved(self):
        return self.approved

    def get_denied(self):
        return self.denied
    


class Node(SimplePredictor):
    def __init__(self, field, threshold, left, right):
        super().__init__()
        self.field = field
        self.threshold = threshold
        self.left = left
        self.right = right

    def dump(self, indent=0):
        if self.field == "class":
            line = "class=" + str(self.threshold)
        else:
            line = self.field + " <= " + str(self.threshold)
        print("  "*indent+line)
        if self.left != None:
            self.left.dump(indent+1)
        if self.right != None:
            self.right.dump(indent+1)
            
    def node_count(self):
        left_count = right_count = 0
        
        if self.left is not None:
            left_count = self.left.node_count()

        if self.right is not None:
            right_count = self.right.node_count()
        
        return left_count + right_count + 1

def build_tree(rows, root_idx=0):
    # recursively call build_tree to create child Nodes (if any)
    # before constructing+returning the node corresponding to the row
    # at index root_idx in rows
    
    curr_node = rows[root_idx]
    left_node = None
    right_node = None
    
    if curr_node['left'] != '-1':
        left_node = build_tree(rows, int(curr_node['left']))
        
    if curr_node['right'] != '-1':
        right_node = build_tree(rows, int(curr_node['right']))
    
    return Node(curr_node['field'], curr_node['threshold'], left_node, right_node)
