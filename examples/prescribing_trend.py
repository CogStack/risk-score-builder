#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 16:04:30 2019

@author: danielbean
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.style.use('ggplot')


## demo plots for prescribing trends
## n.b. this is using dummy data to illustrate the process, there are no
## meaningful patterns in the output.

def figures(af, drugs, ax, panel="", date_col='date_stamp', freq='M'):
    """
    af: prescribing data
    drugs: names of drug columns to plot. Must be mutually exclusive columns 
           which gives the total number of patients when summed
    ax: axis for plot
    panel: name for panel in a grid plot e.g. "A", "Prescribing over time"
    date_col: column name containing dates for aggregation
    freq: aggregation of dates, default 'M' (monthly), see 
              pandas.DataFrame.resample for options
    """
    if af.shape[0] == 0:
        print "no data"
        return

    sum_cols = [date_col] + drugs 

    #input shouldn't need to be daily but not tested
    per_day = af[sum_cols].groupby(date_col).sum() 
    per_day['date'] = per_day.index
    per_day = per_day.set_index('date')
    per_day['total'] = per_day[drugs].sum(axis=1)
    
    #normalise for stacked plot
    per_day_norm = per_day[drugs]
    for dr in drugs:
        norm = per_day[dr]/per_day['total']
        per_day_norm.loc[:,dr] = norm
    
    #resample average
    weekly = pd.DataFrame() #called weekly but actual resample determined by freq parameter
    for dr in drugs:
        weekly[dr] = per_day_norm[dr].resample(freq).mean() * 100
     
    colours2 = ['#b9433e','#f4b688','#90a0c7','#A1D292']

    weekly.loc[:,drugs].plot(kind='bar', stacked=True, color=colours2, width=1.1, ax=ax)
    t = weekly.index.tolist()
    tm = [x.strftime('%m') for x in t]
    v = ""
    for i in range(len(tm)):
        if tm[i] != v:
            v = tm[i]
        else:
            tm[i] = ""
    
    #formatting axes and legend
    ax.set_xticklabels(tm)
    ax.tick_params(axis='x', rotation=0)
    ax.set_title(panel, loc='left')
    ax.set_xlabel('Date')
    ax.set_ylabel('Prercent of admissions')
    patches, labels = ax.get_legend_handles_labels()
    ax.legend(patches, labels, loc=2, bbox_to_anchor=(1.05, 1), frameon=True, ncol=1, facecolor='#FFFFFF')
              
              
def drug_vs_score(af, drugs, ax, score_name, display_name="", panel=""):
    """
    Stacked plot of prescribing stratified by risk score with n above column.
    drugs: names of drug columns to plot. Must b emutually exclusive columns 
           which gives the total number of patients when summed
    ax: axis for plot
    score_name: column containing score for each patient
    display_name: label for X axis, default=score_name
    panel: name for panel in a grid plot e.g. "A", "Prescribing vs score"
    """
    if af.shape[0] == 0:
        print "no data"
        return
    
    if display_name == "":
        display_name = score_name
    
    sum_cols = [score_name] + drugs

    per_point = af[sum_cols].groupby(score_name).sum()
    per_point['date'] = per_point.index
    per_point = per_point.set_index('date')
    per_point['total'] = per_point[drugs].sum(axis=1)
    
    #normalise for stacked plot
    per_point_norm = per_point[drugs]
    for dr in drugs:
        norm = per_point[dr]/per_point['total']
        per_point_norm.loc[:,dr] = norm 
    per_point_norm = per_point_norm * 100
    per_point_norm['total'] = per_point['total'] #for label over column
    

    colours2 = ['#b9433e','#f4b688','#90a0c7','#A1D292','#ffd92f','#A1D292']
    per_point_norm[drugs].plot(kind='bar', legend=False, stacked=True, color=colours2, ax=ax)
    
    #add n per bar
    for i in range(per_point_norm.shape[0]):
        ax.text(i-0.2, 100.5, int(per_point_norm['total'].iloc[i]), fontsize=8)
    
    #formatting axes and legend
    ax.tick_params(axis='x', rotation=0)
    ax.set_title("%s" % (panel), loc='left')
    ax.set_xlabel(display_name)
    ax.set_ylabel('Percent of admissions')
    patches, labels = ax.get_legend_handles_labels()
    ax.legend(patches, labels, loc=2, bbox_to_anchor=(1.05, 1), frameon=True, facecolor='#FFFFFF')


# =============================================================================
# Load and filter data, set up plot container
# =============================================================================
## load prescribing data and apply threshold to consider only high risk patients
af = pd.DataFrame.from_csv('../example_data/prescribing_and_score.csv')

thresholds = {'Female':2, 'Male':2}
above = []
for index, row in af.iterrows():
    above.append(row['chadsvasc'] >= thresholds[row['client_gendercode']])

af = af[above]

# preprocessing of dates
af['date_stamp'] = pd.to_datetime(af['date'])

## create figure container
fig, ax = plt.subplots(nrows=2, ncols=1)
fig.subplots_adjust(hspace=0.35, wspace=0.0)

# =============================================================================
# prescribing trend over time
# =============================================================================
oac_drugs = ['warfarin', 'apixaban', 'rivaroxaban']
af['oac_any_drug'] = af[oac_drugs].any(axis=1)
af['No drug'] = ~af['oac_any_drug']

figures(af, oac_drugs + ['No drug'], ax[0], "A")


# =============================================================================
# prescribing vs score
# =============================================================================
#group by OAC / AP / both / neither
ap_drugs = ['aspirin']
af['ap_any_drug'] = af[ap_drugs].any(axis=1)
af['OAC+AP'] = af['ap_any_drug'] & af['oac_any_drug']
af['OAC only'] = af['oac_any_drug'] & ~af['ap_any_drug']
af['AP only'] = af['ap_any_drug'] & ~af['oac_any_drug']
af['No drug'] = ~af['ap_any_drug'] & ~af['oac_any_drug']

score_plot_drugs = ['OAC only', 'OAC+AP', 'AP only', 'No drug']
drug_vs_score(af, score_plot_drugs, ax[1], 'chadsvasc', 'CHA2DS2-VASc', 'B')

fig.set_size_inches(7,7)