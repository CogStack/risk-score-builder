#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 16:03:17 2019

@author: danielbean
"""

import ScoreBuilder as sb

import yaml, json

with open('config.yml') as f:
    conf = yaml.load(f)
    
builder = sb.ScoreBuilder('test')
tm = sb.TestMapper({}) #empty configuration for test mapper
builder.add_mapper('Test', tm)


#HPO
hpom = sb.HPOMapper(conf['HPO'])
builder.add_mapper('HPO', hpom)
hpo_umls = sb.HPOUMLSMapper(conf['HPO'])
builder.add_mapper('HPO_UMLS', hpo_umls)

    
#UMLS
umls = sb.UMLSMapper(conf['UMLS'])
builder.add_mapper('UMLS', umls)

#build the chadsvasc score definition
definition = builder.build('input_files/chadsvasc_definition.csv')
print "CHA2DS2-VASc"
for comp in definition:
    print "%s: %s concepts" % (comp, len(definition[comp]['concepts']))
print "\n"

with open('output/chadsvasc.generated.definition.txt','w') as f:
    json.dump(definition, f)
    

#build the hasbled score definition
definition = builder.build('input_files/hasbled_definition.csv', 'input_files/manual terms to delete.csv')
print "HAS-BLED"
for comp in definition:
    print "%s: %s concepts" % (comp, len(definition[comp]['concepts']))

with open('output/hasbled.generated.definition.txt','w') as f:
    json.dump(definition, f)