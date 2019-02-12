#!/usr/bin/env python3

import pandas
import json
import sys

# options str
STR_DATES = "dates"
STR_DEADLINES = "deadlines"
STR_EXERCISES = "exercises"
STR_BAD_OPTION = "invalid option"

# stats str
STR_MEAN = "mean"
STR_MEDIAN = "median"
STR_FIRST = "first"
STR_LAST = "last"
STR_PASSED = "passed"

# constants
FIRST_QUARTILE = 0.25
LAST_QUARTILE = 0.75

def get_stats(stats):
    s_dict = {}
    s_dict[STR_MEAN] = stats.mean()
    s_dict[STR_MEDIAN] = stats.median()
    s_dict[STR_FIRST] = stats.quantile(FIRST_QUARTILE)
    s_dict[STR_LAST] = stats.quantile(LAST_QUARTILE)
    s_dict[STR_PASSED] = len([stat for stat in stats if stat > 0])
    return s_dict


def find_duplicate_cols(cols, to_find):   
    duplicates = []
    for col in cols:
        if to_find in col:           
           duplicates.append(col)
    return duplicates


def date_stats(df):
    cols = list(df.head(0))    
    stats = {}
    processed = []

    for col in cols:
        if len(cols) == len(processed):
           break
        if col in processed:  
           continue
        
        col_split = col.split("/")
        col_stripped = col_split[0].strip()
        data_stats = df[cols[cols.index(col)]]    
        data_stats = data_stats.astype("float")
        
        if col != cols[-1]:                
           cols.remove(col)           
           identical_cols = find_duplicate_cols(cols, col_stripped)          
 
           for identical_col in identical_cols:
              identical_col_split = identical_col.split("/")
              identical_col_stripped = identical_col_split[0].strip()
              
              if col_stripped == identical_col_stripped:
                 next_data_stats = df[cols[cols.index(identical_col)]]
                 next_data_stats = next_data_stats.astype("float")
                 data_stats = data_stats.combine(next_data_stats, lambda x, y: x + y)
                 processed.append(col)
                 processed.append(identical_col)
           cols.insert(0, col)      
   
        stats[col_stripped] = get_stats(data_stats)       
    print(json.dumps(stats, ensure_ascii=False, indent=4))


def exercise_stats(df):
    cols = list(df.head(0))    
    stats = {}
    processed = []

    for col in cols:
        if len(cols) == len(processed):
           break
        if col in processed:  
           continue
        
        col_split = col.split("/")
        col_stripped = col_split[1].strip()
        data_stats = df[cols[cols.index(col)]]    
        data_stats = data_stats.astype("float")
        
        if col != cols[-1]:                
           cols.remove(col)           
           identical_cols = find_duplicate_cols(cols, col_stripped)          
 
           for identical_col in identical_cols:
              identical_col_split = identical_col.split("/")
              identical_col_stripped = identical_col_split[1].strip()
              
              if col_stripped == identical_col_stripped:
                 next_data_stats = df[cols[cols.index(identical_col)]]
                 next_data_stats = next_data_stats.astype("float")
                 data_stats = data_stats.combine(next_data_stats, lambda x, y: x + y)
                 processed.append(col)
                 processed.append(identical_col)
           cols.insert(0, col)      
   
        stats[col_stripped] = get_stats(data_stats)       
    print(json.dumps(stats, ensure_ascii=False, indent=4))


def deadline_stats(df):
    cols = list(df.head(0))    
    stats = {}

    for col in cols:      
        stats[col.strip()] = get_stats(df[cols[cols.index(col)]])       
         
    print(json.dumps(stats, ensure_ascii=False, indent=4))


def main():    
    if len(sys.argv) < 3:
        print("argv error: not enough program arguments")
        print("invocation: ./stat.py file option")
        sys.exit()

    file_name = sys.argv[1]
    option = sys.argv[2]

    df = pandas.read_csv(file_name, index_col="student", delimiter=",", skipinitialspace=True)
   
    if option == STR_DATES:
       date_stats(df)
    elif option == STR_DEADLINES:
       deadline_stats(df)
    elif option == STR_EXERCISES:
       exercise_stats(df)
    else:
       print(STR_BAD_OPTION)

if __name__ == "__main__":
    main()
