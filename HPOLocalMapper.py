#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 12:47:02 2019

@author: danielbean
"""

## convert HPO obo format into a basic python dict structure
from HPO.HPOreader import HPOreader
from ScoreBuilder import MapperTemplate


class HPOLocalMapper(MapperTemplate):
     def __init__(self, conf):
          MapperTemplate.__init__(self, conf)
          self.hpo = HPOreader()
          if 'ontology_file' in conf and conf['ontology_file'] != None:
               self.parse(conf['ontology_file'])
               
     def parse(self, obo_file):
          self.graph = self.hpo.parse(obo_file)
          
     def get_descendants(self, start, depth):
          return self.graph.traverse(start, depth)
     
if __name__ == "__main__":
     hpo_mapper = HPOLocalMapper({})
     obo_file = 'HPO/hp.sample.obo.txt'
     hpo_mapper.parse(obo_file)
     print hpo_mapper.get_descendants('HP:0000012', 1)
     print hpo_mapper.get_descendants('HP:0000012', 2)