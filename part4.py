from twitterparser import TwitterParser
from featureExtraction import *
import datetime
import time
import numpy as np
import statsmodels.api as sm

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
		print hashtag
		compressedTweets = np.genfromtxt(format('results/%s_results.txt' %(hashtag)), delimiter=',')
		for ii in range (compressedTweets.shape[0]):
			d = compressedTweets[ii][0]

			if d < tfeb18am:
				model = 0
			elif d < tfeb18pm:
				model = 1
			else:
				model = 2
			
			data[model][i].append(compressedTweets[ii,:]) 

	for i in xrange(3):
		for j in xrange(len(hashtags)):
			data[i][j] = np.array(data[i][j])
#			print '{},{}:{}'.format(i,j,np.shape(data[i][j]))

	return data

# Perform one group of cross validation
def crossValidation(modelData, model, group):
	print 'Performing training/testing on model {}, group {}'.format(model, group)

	featureWidth = 5

	y = np.zeros(shape=(0))         # Y: target value
	X = np.zeros(shape=(0,featureWidth))       # X: predictors

	yt = np.zeros(shape=(0))        # Test output
	Xt = np.zeros(shape=(0,featureWidth))      # Test feature input

	cnt = 0
	for i in xrange(len(hashtags)):
		data = modelData[model][i]

		#print np.shape(data)
		#print data
		#print data[:,0]

		min_time = np.min(data[:, 0])
		max_time = np.max(data[:, 0])
		time_win = np.arange(min_time, max_time+1, 3600)
		win_cnt = time_win.shape[0]

		tag_X = np.zeros(shape=(win_cnt-1,featureWidth))
		tag_y = np.zeros(win_cnt-1)

		tag_Xt = np.zeros(shape=(win_cnt-1,featureWidth))
		tag_yt = np.zeros(win_cnt-1)

		ntrain = 0
		ntest = 0
		for ii in range(data.shape[0]):
			tweet_ts = data[ii][0]
			win_idx  = (tweet_ts - min_time) / 3600
			
			# Determine if the data should belong to training or testing set
			if (cnt - group)%10 == 0:
				tagy = tag_yt
				tagX = tag_Xt
				ntest += 1
			else:
				tagy = tag_y
				tagX = tag_X
				ntrain += 1

			# Feature extraction here is identical to part 2 now.
			# Target value
			if win_idx > 0:   # We are not predicting for first window
				tagy[win_idx-1] += 1

			if (win_idx < win_cnt-1): # Ware not generating features from last window
				tagX[win_idx, 0] += 1              # Number of tweets
				tagX[win_idx, 1] += data[ii][2]    # Number of retweets
				tagX[win_idx, 2] += data[ii][1]    # Sum of followers
				tagX[win_idx, 3] = max(tag_X[win_idx, 3], data[ii][1]) # Max number of followers
				tagX[win_idx, 4] = datetime.datetime.fromtimestamp(data[ii][0]).hour

			# End of feature extraction

			cnt += 1
		print 'hashtag #{} Ntrain:{} Ntest:{}'.format(hashtags[i], ntrain, ntest)

		X = np.vstack((X, tag_X))
		y = np.append(y, tag_y)
		Xt = np.vstack((Xt, tag_Xt))
		yt = np.append(yt, tag_yt)
	X = sm.add_constant(X)
	Xt = sm.add_constant(Xt)

	results = sm.OLS(y,X).fit()
	#print results.summary()
	yp = results.predict(Xt)
	
	avgdiff = np.average(np.abs(yt-yp))
	print yt
	print yp
	print 'Average tweets:{}, average predicted:{}, average absolute diff:{}'.format(np.average(yt), np.average(yp), avgdiff)
	return avgdiff

def main():
	data = modelSplit()
	avgdiff = np.zeros([3,10])
	for model in xrange(3):
		for group in xrange(10):
			avgdiff[model][group] = crossValidation(data, model, group)
	print 'Average absolute diff over 3 models and 10 groups:'
	print avgdiff 

if __name__=='__main__':
	main()
