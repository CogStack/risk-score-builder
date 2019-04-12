# -*- coding: utf-8 -*-
"""
Created on Wed Aug 08 13:30:48 2018

@author: Dan Bean
"""

#calculate clinical risk scores using example data

import json
import pandas as pd

import Scorer as scorer

with open('../example_data/risk_nlp_data.txt') as f:
    pt = json.load(f)

    
#concepts related to each score
with open('../output/chadsvasc.generated.definition.txt') as f:
    chads_definition = json.load(f)

with open('../output/hasbled.generated.definition.txt') as f:
    hasbled_definition = json.load(f)


#make a dataframe of patients x risk factors
print "generate risk factor dataframe"
df_data = []
pt_not_found = set()
for p in pt:
    #NLP features pre-filtered to those relevant to the score and above
    #any required confidence threshold
    pt_data = p['features']
    
    #identifiers
    pt_data['patient_id'] = p['identifiers']['patient_id']
    
    #create any components of the score we've defined manually rather
    #than from NLP
    pt_data['Female'] = p['features']['_male'] == 0
    pt_age = p['features']['_age']
    pt_data['Age_gte75'] = pt_age >= 75
    pt_data['Age_65-74'] = (pt_age >= 65 and pt_age < 75)
    pt_data['Age_gt65'] = pt_age > 65
    df_data.append(pt_data)
    
df = pd.DataFrame(df_data)

# in this example we're working at the level of UMLS CUI's, but any identifiers
# can be used as long as the patient data and score definition are using the
# same system. 


#chads2vasc
print "score chads2vasc"
chadsvasc = scorer.Scorer(chads_definition)
chadsvasc_result = chadsvasc.score(df, ['patient_id'])
chadsvasc_scores = chadsvasc_result['scores']
#concepts in score definition that were never seen in the input patient data
chadsvasc_not_found = chadsvasc_result['not_found'] 
#save scores to csv
chadsvasc_scores.to_csv('../example_data/chadsvasc_scores.csv', index=False)


#hasbled
print "score hasbled"
hasbled = scorer.Scorer(hasbled_definition)
hasbled_scores = hasbled.score(df, ['patient_id'])
#export directly from Scorer result
hasbled_scores['scores'].to_csv('../example_data/hasbled_scores.csv', index=False)

