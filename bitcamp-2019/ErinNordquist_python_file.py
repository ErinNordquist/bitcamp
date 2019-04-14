# -*- coding: utf-8 -*-
"""bitcamp2019.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/17mMv3HtX-szYCfRgltqxNe_DIhpSVh71

# Data Importantion and Formatting
The data was formatted in text files delimited by spaces. I used regular expressions to extract the data from each of the files.
"""

import numpy as np
import pandas as pd
import re

df = pd.read_table('issuance_loans.txt')


col = df.columns.values[0]
df['raw'] = df[col]
##try splitting with regex
iss_loans = df['raw'].str.extract(r'(\d\d\d)  (.{7})  (.{12}) (.{10}) (...) (.{13}) (.{10}) (...) (.{9}) (..) (.{7}) (..) (.) (...)  (.{7}) (...) (...)  (.{12}) (.{9}) (.{5}) (.+)$')
iss_loans.columns = ['bor_credit_score', 'curr_int_rate', 'curr_upb', 'first_pay_date', 'first_time_hb_flag', 'loan_channel','loan_id','loan_product_type','loan_purpose','loan_state','maturity_date','numb_of_borr','numb_of_units','orig_dti','orig_int_rate','orig_loan_term', 'orig_ltv', 'orig_upb', 'property_occupancy','property_type','servicer_name']
iss_loans.replace('NULL',np.nan, inplace = True)
iss_loans['curr_int_rate'] = iss_loans['curr_int_rate'].astype(float)
iss_loans['orig_int_rate'] = iss_loans['orig_int_rate'].astype(float)
iss_loans['first_pay_date'] = pd.to_datetime(iss_loans['first_pay_date'])
iss_loans['first_time_hb_flag'].replace('NO', 0, inplace = True)
iss_loans['first_time_hb_flag'].replace('YES', 1, inplace = True)
iss_loans['numb_of_borr'] = iss_loans['numb_of_borr'].astype(float)
iss_loans['numb_of_units'] = iss_loans['numb_of_units'].astype(float)
iss_loans['curr_upb'] = iss_loans['curr_upb'].astype(float)
iss_loans['orig_upb'] = iss_loans['orig_upb'].astype(float)  
problem = iss_loans['orig_dti'][9] #dealing with a missing value 
iss_loans.replace(problem,np.nan, inplace = True)
iss_loans['orig_dti'] = iss_loans['orig_dti'].astype(float)
iss_loans['orig_loan_term'] = iss_loans['orig_loan_term'].astype(float)
iss_loans['orig_ltv'] = iss_loans['orig_ltv'].astype(float)

iss_loans.head()



df = pd.read_table('loans_origination_info.txt')


col = df.columns.values[0]
df['raw'] = df[col]

##try splitting with regex
loans_orig_info = df['raw'].str.extract('(.+) (.+) (.+) (.+) (.+) (.+) (.+) (.+) (.+) (.+) (.+) (.+) (.+) (.+) (.+) (.+) (.+)')
loans_orig_info.columns = df.columns.values[0].split(' ')
loans_orig_info = loans_orig_info.replace('NULL', np.nan)
loans_orig_info['nb_loan_number'] = loans_orig_info['nb_loan_number'].astype(float)
loans_orig_info['nb_original_balance'] = loans_orig_info['nb_original_balance'].astype(float)
loans_orig_info['nb_original_fico'] = loans_orig_info['nb_original_fico'].astype(float)
loans_orig_info['nb_debt_ratio'] = loans_orig_info['nb_debt_ratio'].astype(float)
loans_orig_info['nb_original_rate'] = loans_orig_info['nb_original_rate'].astype(float)
loans_orig_info['nb_original_ltv'] = loans_orig_info['nb_original_ltv'].astype(float)
loans_orig_info['nb_original_cltv'] = loans_orig_info['nb_original_cltv'].astype(float)
loans_orig_info['nb_unit_count'] = loans_orig_info['nb_unit_count'].astype(float)
loans_orig_info['nb_original_term'] = loans_orig_info['nb_original_term'].astype(float)
loans_orig_info['nb_io_term'] = loans_orig_info['nb_io_term'].astype(float)
loans_orig_info['nb_origination_date'] = pd.to_datetime(loans_orig_info['nb_origination_date'])
loans_orig_info['nb_maturity_date'] = pd.to_datetime(loans_orig_info['nb_maturity_date'])

loans_orig_info.head()

df = pd.read_table('loans_performance_timeseries.txt')


col = df.columns.values[0]
df['raw'] = df[col]

##try splitting with regex
loans_perf = df['raw'].str.extract('(.+) (.+) (.+) (.+) (.+) (.+)')
loans_perf.columns = df.columns.values[0].split(' ')
loans_perf = loans_perf.replace('NULL', np.nan)
loans_perf['nb_factor_date'] = pd.to_datetime(loans_perf['nb_factor_date'])
loans_perf['nb_loan_number'] = loans_perf['nb_loan_number'].astype(float)
loans_perf['nb_current_balance'] = loans_perf['nb_current_balance'].astype(float)
loans_perf['nb_realized_loss'] = loans_perf['nb_realized_loss'].astype(float)
loans_perf['nb_age'] = loans_perf['nb_age'].astype(float)
loans_perf['nb_delinquent_days'] = loans_perf['nb_delinquent_days'].astype(float)
loans_perf = loans_perf[pd.notnull(loans_perf['nb_delinquent_days'])].reset_index(drop = True) #drop meaningless rows and reindex
loans_perf.sort_values('nb_factor_date')
most_recent = loans_perf['nb_factor_date'].max()
in_progress = loans_perf[loans_perf['nb_factor_date'] >= most_recent ]
in_progress

#determine which nb_loan_number's ended with losses
loan_losses = loans_perf[loans_perf['nb_realized_loss'] > 0]
loan_losses = loan_losses[['nb_loan_number', 'nb_realized_loss']].groupby(['nb_loan_number'], as_index = False).sum()
loan_losses['caused_loss'] = 1
loan_losses = loans_perf[['nb_loan_number', 'nb_age']].groupby(['nb_loan_number']).max().merge(loan_losses, how = 'right', on = 'nb_loan_number')
loan_losses

loans_info = loans_orig_info[['nb_loan_number']]
loans_info = loans_info.merge(loan_losses, how = 'left')
loans_info['nb_realized_loss'] = loans_info['nb_realized_loss'].fillna(0)
loans_info['caused_loss'] = loans_info['caused_loss'].fillna(0)
loans_info['age'] = loans_perf['nb_age']
loans_info['orig_term'] = loans_orig_info['nb_original_term']
loans_info['orig_balance'] = loans_orig_info['nb_original_balance']
loans_info['orig_fico'] = loans_orig_info['nb_original_fico']
loans_info['orig_ltv'] = loans_orig_info['nb_original_ltv']
loans_info = loans_info.drop(columns={'nb_age'})
#loans_info['debt_ratio'] = loans_orig_info['nb_debt_ratio']
loans_info.head(10)

loans_info.sort_values('age').head()

import matplotlib.pyplot as plt
x = loans_info['age']
y = loans_info['nb_realized_loss']
plt.scatter(x,y)
plt.show()

!pip install -q sklearn

from sklearn.model_selection import train_test_split
import sklearn.tree
from sklearn.tree import DecisionTreeClassifier

loans_info['orig_fico'] = loans_orig_info['nb_original_fico']
loans_info['nb_realized_loss'] = np.log(loans_info['nb_realized_loss'])
loans_info['orig_balance'] = np.log(loans_info['orig_balance'])
vals = 0
runs = 100
x1 = 0
x2 = 0
x3 = 0
x4 = 0
for x in range (0,runs):
  clf = DecisionTreeClassifier()
  data = loans_info.dropna(axis = 0, how = 'any')
  X = (data.drop(columns={'nb_loan_number','nb_realized_loss', 'caused_loss','age'}))
  X_train, X_test, Y_train, Y_test = train_test_split(X, data['caused_loss'], test_size = .7, train_size = .3)
  tree = clf.fit(X_train, Y_train)
  vals = vals + (tree.score(X_test, Y_test))
  #print(tree.feature_importances_)
  x1 += tree.feature_importances_[0]
  x2 += tree.feature_importances_[1]
  x3 += tree.feature_importances_[2]
  x4 += tree.feature_importances_[3]
print(vals/runs) 
print('Average Importance of Loan Term, Loam Amount, FICO Score, and Loan to Value Ratio')
print(x1/runs)
print(x2/runs)
print(x3/runs)
x4/runs



