#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 10:25:39 2019

@author: danielbean
"""

## load HPO ontology into a directed graph in memory and use it to build
## an example risk score

from SNOMEDLocalMapper import SNOMEDLocalMapper
import ScoreBuilder as sb
import examples.Scorer as scorer

import json
import pandas as pd


#create the HPO mapper and parse the HPO .obo ontology file
rela_file = 'SNOMED/isa_rela_ch2pt.txt'
conf = {'rela_file': rela_file}
snomed_mapper = SNOMEDLocalMapper(conf)

#create a builder instance
builder = sb.ScoreBuilder()
#add the mapper to the score builder so it can be used in the definition file
#using "SNOMED_local"
builder.add_mapper('SNOMED_local', snomed_mapper)

#add the Test mapper so we can pass through manual features
tm = sb.TestMapper({}) #empty configuration for test mapper
builder.add_mapper('Test', tm)

#use the builder to parse the definition file and do the mapping
definition = builder.build('input_files/snomed_demo_definition.csv')

#apply the definition to patient data
with open('example_data/risk_nlp_data_hpo.txt') as f:
    pt = json.load(f)

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

#calculate risk score
demo = scorer.Scorer(definition)
demo_result = demo.score(df, ['patient_id'])
demo_scores = demo_result['scores']
print demo_scores.head()

#get names - snomedmapper can map cui to name
cdb_file = 'SNOMED/snomed_cdb_csv_SNOMED-CT-UK_Release_20200401.csv'
snomed_mapper.load_cdb(cdb_file)
rows = []
for k in definition:
    print 
    for v in definition[k]['concepts']:
        r = {'component': k}
        try:
            s = snomed_mapper.cui2name[v]
        except KeyError:
            s = ""
        r['cui'] = v
        r['name'] = s
        rows.append(r)

df = pd.DataFrame(rows)
df.to_csv('example_data/snomed_demo_mapped.csv')
