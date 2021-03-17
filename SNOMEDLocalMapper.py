#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 13:49:14 2020

@author: danielbean
"""

#load relations from SNOMED-CT
from SNOMED.SNOMEDreader import SNOMEDreader
from ScoreBuilder import MapperTemplate


class SNOMEDLocalMapper(MapperTemplate):
     def __init__(self, conf):
          MapperTemplate.__init__(self, conf)
          self.snomed = SNOMEDreader()
          self.cdb2name = {}
          if 'rela_file' in conf and conf['rela_file'] != None:
               self.load_rels(conf['rela_file'])

          if 'snomed_path' in conf and conf['snomed_path'] != None:
               self.parse(conf['snomed_path'])
               
     def parse(self, snomed_path):
          """
          parse from raw SNOMED data
          """
          self.graph = self.snomed.parse(snomed_path)
		  
     def load_rels(self, rela_file):
          """
          load preprocessed relationships dict
          """
          self.graph = self.snomed.load_rels(rela_file)
    
     def load_cdb(self, cdb_file):
          self.cui2name = self.snomed.load_cdb(cdb_file)
          
     def get_descendants(self, start, depth):
          return self.graph.traverse(start, depth)
     
if __name__ == "__main__":
     snomed_mapper = SNOMEDLocalMapper({})
     rela_file = 'SNOMED/rela.example.txt'
     snomed_mapper.load_rels(rela_file)
     print snomed_mapper.get_descendants('HP:0000012', 1)
     print snomed_mapper.get_descendants('HP:0000012', 2)