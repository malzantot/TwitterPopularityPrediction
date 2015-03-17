import json

class TwitterParser:
    def __init__(self, hashtag):
        self.hashtag = hashtag
        self.filename = format("data/tweets_#%s.txt" %(self.hashtag))
        self.fh = None
        self.tweet = None

    def load(self):
        self.fh = open(self.filename, 'r') # File handle

    def close(self):
        if self.fh is None:
            print('Error closing file')
            return
        self.fh.close()
        self.fh = None

    def next_tweet(self):
        if self.fh is None:
            print('Error: cannot find tweets file for hashtag #%s' %(self.hashtag))
            return -1
        line = self.fh.readline()
        if not line:
            self.tweet = None
            self.close()
            return -1
        self.tweet = json.loads(line)
        return 0

    def get_tweet(self):
        return self.tweet

    def get_retweet_count(self):
        if self.tweet is None:
            return None
        return self.tweet['metrics']['citations']['total']-1

    def get_post_time(self):
        if self.tweet is None:
            return None
        return self.tweet['citation_date']

    def get_tweet_type(self):
        if self.tweet is None:
            return None
        return self.tweet['type']

    def get_followers_count(self):
        if self.tweet is None:
            return None
        return self.tweet['author']['followers']
