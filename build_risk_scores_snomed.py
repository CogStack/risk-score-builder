#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 16:03:17 2019

@author: danielbean
"""

import ScoreBuilder as sb
from SNOMEDLocalMapper import SNOMEDLocalMapper
import pandas as pd

import yaml, json

with open('config.yml') as f:
    conf = yaml.load(f)
    
builder = sb.ScoreBuilder()
tm = sb.TestMapper({}) #empty configuration for test mapper
builder.add_mapper('Test', tm)

#SNOMED
rela_file = 'SNOMED/isa_rela_ch2pt.txt'
c = {'rela_file': rela_file}
snomed_mapper = SNOMEDLocalMapper(c)
cdb_file = 'SNOMED/snomed_cdb_csv_SNOMED-CT-UK_Release_20200401.csv'
snomed_mapper.load_cdb(cdb_file)
builder.add_mapper('SNOMED_local', snomed_mapper)


#build the chadsvasc score definition
definition = builder.build('input_files/chadsvasc_definition_snomed.csv')
print "CHA2DS2-VASc"
for comp in definition:
    print "%s: %s concepts" % (comp, len(definition[comp]['concepts']))
print "\n"

with open('output/chadsvasc.generated.definition.snomed.txt','w') as f:
    json.dump(definition, f)
    

rows = []
for k in definition:
    for v in definition[k]['concepts']:
        r = {'component': k}
        try:
            s = snomed_mapper.cui2name[v]
        except KeyError:
            s = ""
        r['cui'] = v
        r['name'] = s
        if v.startswith('S-'):
            rows.append(r)
        else:
            print "skip", v

df = pd.DataFrame(rows)
df.to_csv('output/chadsvasc.snomed.concepts.csv')



#build the dummy SMI score definition
definition = builder.build('input_files/SMI_definition_snomed_v2.csv')
print "SMI"
for comp in definition:
    print "%s: %s concepts" % (comp, len(definition[comp]['concepts']))
print "\n"

with open('output/SMI.generated.definition.snomed.txt','w') as f:
    json.dump(definition, f)
    

rows = []
for k in definition:
    for v in definition[k]['concepts']:
        r = {'component': k}
        try:
            s = snomed_mapper.cui2name[v]
        except KeyError:
            s = ""
        r['cui'] = v
        r['name'] = s
        if v.startswith('S-'):
            rows.append(r)
        else:
            print "skip", v

df = pd.DataFrame(rows)
df.to_csv('output/SMI.snomed.concepts.csv')
