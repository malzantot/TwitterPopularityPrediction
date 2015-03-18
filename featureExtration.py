# Define a set of features that takes a tweet and returns some
# neumerical values, e.g, hour, number of follower, etc.

# The examples below take numbers for demo purpose.
def square(x):
	return x*x

def m1(x):
	return x-1

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
		for currentFeature in self.extractors:
			features.append(currentFeature(tweet))
		return features

# Example
if __name__=='__main__':
	fe = TweetFeatureExtractor()
	fe.addFeature(square)
	fe.addFeature(m1)
	print fe.getFeatureValues(10)
	print fe.getFeatureValues(-1)
