# Importing all required libs
import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches

fin_list = []
votes_list = []

df_main = pd.read_csv("./data/HRDataset_v14.csv")
categorical = set(('Employee_Name','Position', 'State', 'Zip', 'DOB', 'Sex', 'MaritalDesc', 'CitizenDesc', 'HispanicLatino', 'RaceDesc', 'DateofHire', 'DateofTermination','TermReason' ,'EmploymentStatus', 'Department', 'ManagerName', 'RecruitmentSource', 'PerformanceScore', 'LastPerformanceReview_Date' ))


group_columns = ['EmpID', 'Salary']
sensitive_column = 'Employee_Name'

df_main.drop(df_main[df_main['EmploymentStatus'] == "Voluntarily Terminated" ].index, inplace = True)
df_main.drop(df_main[df_main['EmploymentStatus'] == "Terminated for Cause"].index, inplace = True)

for i in range(len(df_main)):
    # fin_list[df_main["EmpID"].iloc[i] - 10000] = True
    fin_list.append(df_main["EmpID"].iloc[i])
    
for i in range (207):
    votes_list.append([fin_list[i],random.choice(fin_list)])
    random.seed(i*i)
    
print (votes_list)