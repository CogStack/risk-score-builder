#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 11:19:22 2019

@author: danielbean
"""
#generate dummy NLP output for HPO examples

import json
import pandas as pd
import numpy as np

#use the list of CUI from the scores to get a list of CUI to generate data for
#in reality the data would come from patient records and the list of all detected
#CUI for all patients would be filtered using this list of concepts, then used
#to calcualte the risk scores
concepts = pd.read_csv('../example_data/hpo_demo_list.csv')
all_cui = concepts['hp'].unique()

#size of output
n_patients = 10
cui_min = 0
cui_max = 10 #must be less than len(all_cui)
age_options = range(40,100,10)
output = []

#generate number of concepts found for each patient
n_cui = np.random.choice(range(cui_min, cui_max), n_patients, replace=True)

#gender
pt_gender = np.random.choice(2, n_patients, replace=True)

#age
pt_age = np.random.choice(age_options, n_patients, replace=True)


for pt in range(n_patients):
    pt_cui = np.random.choice(all_cui, n_cui[pt], replace=False)
    pt_cui_count = np.random.choice(10, n_cui[pt], replace=True)
    cui_data = {pt_cui[x]:pt_cui_count[x] for x in range(n_cui[pt])}
    cui_data['_age'] = pt_age[pt]
    cui_data['_male'] = pt_gender[pt]
    pt_data = {'features':cui_data}
    pt_data['identifiers'] = {'patient_id':pt}
    output.append(pt_data)
    
with open("../example_data/risk_nlp_data_hpo.txt",'w') as f:
    json.dump(output, f)