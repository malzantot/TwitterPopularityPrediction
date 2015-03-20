# Part 4 using part 3 way

from twitterparser import TwitterParser
from featureExtraction import *
import datetime
import time
import pandas as pd 
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf

feb18am = datetime.datetime(2015,02,01,8,00,0)
feb18pm = datetime.datetime(2015,02,01,20,00,0)

# Not daylight saving time on feb 1: adjust clock backwards by 1h
offset = -3600

tfeb18am = int(time.mktime(feb18am.timetuple())) + offset
tfeb18pm = int(time.mktime(feb18pm.timetuple())) + offset

hashtags = ['gohawks', 'gopatriots', 'nfl', 'patriots', 'sb49', 'superbowl']

# Split data by timestamp.
# Returns 3x6 matrix of numpy arrays. data[i][j] is the data for
# model=i and hashtag[j].
# Models 0-2 correspond to before/during/after superbowl periods
def modelSplit():
	print 'Splitting data for three different models.'
	data = []
	
	for i in xrange(3):
		data.append([])
		for j in xrange(len(hashtags)):
			data[i].append([])

	count = 0
	for i in xrange(len(hashtags)):
		hashtag = hashtags[i]
		print('Hashtag #%s' %(hashtag))
		df = pd.read_csv(('result_part3/%s_factors.txt' %(hashtag))) 

		df.columns = ['time_stamp', 'followers', 'retweets', 'userMentioned', 'coexistHash', 'urlCount','type']
		df = df.sort_index(by=['time_stamp'], ascending=[True])
    
		time_stamp = df.ix[:,0]

		data[0][i] = df[ time_stamp < tfeb18am ]
		data[1][i] = df[ (time_stamp >= tfeb18am) & (time_stamp < tfeb18pm) ]
		data[2][i] = df[ time_stamp >= tfeb18pm ]

	return data

def preparexy(df, dfcurrent):
	time_stamp = df.ix[:,0]
	time_split = 3600 # 3600 unit is 1 hour. 
	begin_time = df['time_stamp'].min() # time of line_count entry 
    
	duration = 0
	dormant = 1
	means = None

	maxtime = df['time_stamp'].max()
	mintime = df['time_stamp'].min()

	# feature building for training data
	for i in range(dfcurrent.__len__()-1) : # go through each 'time-slot' (1 hour)
		end_time = begin_time + time_split 
		oneHour = dfcurrent[ (time_stamp>=begin_time) & (time_stamp<end_time) ] 
		begin_time = end_time # update begin-time    
		duration = duration+1 # time duration.
		if (duration > (maxtime-mintime) / time_split ):
			print duration
			break 
		if (oneHour.__len__() < 1): # if no tweet can be found 
			dormant = dormant + 1
		else:      
			if (duration == 1): 
				means = oneHour.mean()
				means = pd.concat( [ means, pd.Series(oneHour.__len__(),['count']) ] ) 
			else:
				means = pd.concat( [ means, pd.concat ( [ oneHour.mean() , pd.Series(oneHour.__len__(),['count']) ] ) ] )       

	hourData = means.values.reshape(means.__len__()/dfcurrent.columns.__len__(),dfcurrent.columns.__len__()) # divide how many columns there are
	hourData = pd.DataFrame(hourData)
	hourData.columns = ['time_stamp', 'followers', 'retweets', 'userMentioned', 'coexistHash', 'urlCount', 'count'] # put the value to be predicted in the 2nd column 
    
	temp = hourData.iloc[1:(hourData.__len__()+1)] # remove row 1 
	data_fit = hourData.iloc[0:hourData.__len__()] # remove last row, can't be used in analysis 
	data_fit.insert(1, 'count2' , pd.DataFrame( temp['count'].values.reshape(temp['count'].__len__(),1) ) )

	temp = hourData.iloc[1:(hourData.__len__()+1)] # remove row 1 
	data_fit = hourData.iloc[0:hourData.__len__()] # remove last row, can't be used in analysis 
	data_fit.insert(1, 'count2' , pd.DataFrame( temp['count'].values.reshape(temp['count'].__len__(),1) ) )
	data_fit.__delitem__('time_stamp')

	#========== add a constant (intercept)
	data_fit = sm.add_constant(data_fit) ## use hour X to predict hour X+1   
   
	#========== numerical issues. if take log (0) 
	data_fit['followers'].loc[data_fit['followers']==0] = 1

	data_fit.loc[:,'log_follower'] = np.log(data_fit['followers']) # log of avg_followers 
	data_fit.__delitem__('followers')
	data_fit.__delitem__('count') 
	data_fit = data_fit.iloc[0:(data_fit.__len__()-1)] # remove the stupid NAN in last row. 
	y = data_fit['count2'].values # true y
	data_fit.__delitem__('count2')
	x = data_fit.values
	#x = sm.add_constant(x, prepend=True) # model X
	return (x, y)

# Perform one group of cross validation
def crossValidation(modelData, model, group):
	print 'Performing training/testing on model {}, group {}'.format(model, group)
	res = np.zeros(len(hashtags))

	for i in xrange(len(hashtags)):
		print 'hashtag: {}'.format(hashtags[i])
		df = modelData[model][i]
		df = df.sort_index(by=['time_stamp'], ascending=[True])

		dftrain = df[(df.index.to_series() - group) % 10 != 0]
		dftest = df[(df.index.to_series() - group) % 10 == 0] 
		print 'hashtag #{} Ntrain:{} Ntest:{}'.format(hashtags[i], dftrain.__len__(), dftest.__len__())

		x,y = preparexy(df, dftrain)
		xt, yt = preparexy(df, dftest)

		gauss_log = sm.GLM(y, x, family=sm.families.Gaussian(sm.genmod.families.links.log))
		gauss_log_results = gauss_log.fit()
		print(gauss_log_results.summary())

		yp = gauss_log_results.predict(xt)

		print yp
		print yt

		res[i] = np.average(np.abs(yp-yt))
			# End of feature extraction
		print res[i]
	print res
	return res

def main():
	data = modelSplit()
	#print data

	#model = 1
	#group = 0
	#crossValidation(data, model, group)

	hl = len(hashtags)

	avgdiff = np.zeros([3, hl])
	for model in xrange(3):
		res = np.zeros(hl)
		for group in xrange(10):
			res += crossValidation(data, model, group)
			#res += np.ones(6) 
		avgdiff[model,:] = res
	#print 'Average absolute diff over 3 models and 10 groups:'
	#print avgdiff 
	avgdiff = avgdiff/10.0;
	print avgdiff

if __name__=='__main__':
	main()
