#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 15:27:45 2019

@author: danielbean
"""

### build dummy data for examples

import numpy as np
import pandas as pd

# prescribing data
n_patients = 10000

#drug names
oac_drugs = ['warfarin', 'apixaban', 'rivaroxaban', 'no oac']
ap_drugs = ['aspirin', 'no ap']

#generate a random drug choice for each patient and convert to dummy variables
oac_choice = np.random.choice(oac_drugs, n_patients, replace=True, p=[0.3, 0.3, 0.1, 0.3])
oac_prescribing = pd.get_dummies(oac_choice)

ap_choice = np.random.choice(ap_drugs, n_patients, replace=True, p=[0.3, 0.7])
ap_prescribing = pd.get_dummies(ap_choice)

prescribing = oac_prescribing.join(ap_prescribing)

#add some fake scores
prescribing['chadsvasc'] = np.random.choice(10, n_patients, replace=True)

#gender
prescribing['client_gendercode'] = np.random.choice(['Male', 'Female'], n_patients, replace=True)

#date
dates_in_range = pd.date_range(start='1/1/2019', end='7/1/2019', freq='D')
prescribing['date'] = np.random.choice(dates_in_range, n_patients, replace=True)

prescribing.to_csv('../example_data/prescribing_and_score.csv')
