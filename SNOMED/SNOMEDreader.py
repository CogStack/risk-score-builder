#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 13:52:46 2020

@author: danielbean
"""

#preprocess SNOMED ontology files to graph structure
from edges import Directed
import json
import pandas as pd

class SNOMEDreader:
    def __init__(self):
        self.terms = {}
        self.missing = set()
        
    def parse(self, path, return_graph = True, verbose = False):
        """
        Parse HPO .obo files to a directed graph. 
        path = path to .obo file
        return_graph = whether to return the directed graph (default: True) or
        save it as self.rels (False).
        verbose = print parsing errors (default false (off))
        """
        pass
        

    
    def load_rels(self, rela_file, return_graph = True, verbose = False):
        """
        load dict of relations and convert to graph
        rela_file = path to parent-child relations dict
        return_graph = whether to return the directed graph (default: True) or
        save it as self.rels (False).
        verbose = print parsing errors (default false (off))
        """
        rels = Directed()
        with open(rela_file) as f:
            pt2ch = json.load(f)
        
        for tgt in pt2ch:
            for src in pt2ch[tgt]:
                rels.add(src, tgt)
            
        if return_graph == True:
             return rels
        else:
             self.rels = rels
    
    def load_cdb(self, cdb_path):
        df = pd.read_csv(cdb_path)
        df.set_index('cui', inplace=True)
        df = df[df['tty'] == 1]
        cui2name = df['str'].T.to_dict()
        return cui2name
        
        
        
if __name__ == "__main__":
    reader = SNOMEDreader()
    #reader.parse('hp.sample.obo.txt')
    g = reader.load_rels('rela.example.txt')