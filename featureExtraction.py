# Define a set of features that takes a tweet and returns some
# neumerical values, e.g, hour, number of follower, etc.
# Returning a list of numbers is also allowed.

# The examples below take numbers for demo purpose.
import datetime as dt

def square(x):
	return x*x

def m1(x):
	return x-1


def firstpostHour(tweet):
	postDateInt = tweet['citation_date']
	postDate = dt.datetime.fromtimestamp(postDateInt)
	return str(postDate)

########################################################
class TweetFeatureExtractor:
	def __init__(self):
		# A set of features to extract
		self.extractors = []	

	# Use this function to append new features with minimal
	# impact to existing code
	def addFeature(self, featureFunction):
		self.extractors.append(featureFunction)

	# Evaluate feature functions in the order we added them.
	def getFeatureValues(self, tweet):
		features = []
		for currentFeatureExtractor in self.extractors:
			currentFeature = currentFeatureExtractor(tweet)
			if type(currentFeature)==list:
				features += currentFeature
			else:
				features.append(currentFeature)
		return features

# Example
from twitterparser import TwitterParser
def main():

	fe = TweetFeatureExtractor()
	fe.addFeature(square)
	fe.addFeature(m1)
	print fe.getFeatureValues(10)
	print fe.getFeatureValues(-1)

	gohawks = TwitterParser('gohawks')
	gohawks.load()
	cnt = 0
	while cnt < 5 and gohawks.next_tweet() == 0:
	#while gohawks.next_tweet() == 0:
		tweet = gohawks.get_tweet()
		
		d = firstpostHour(tweet)
		print 'firstpose date for tweet {}: {}'.format(cnt+1, d)
		cnt += 1

if __name__=='__main__':
	main()

