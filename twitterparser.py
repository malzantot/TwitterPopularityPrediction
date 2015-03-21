import json

class TwitterParser:
    def __init__(self, hashtag):
        self.hashtag = hashtag
        self.filename = format("data/tweets_#%s.txt" %(self.hashtag))
        self.fh = None
        self.tweet = None

    def load_file(self, file_name):
        self.filename = file_name
        self.fh = open(self.filename, 'r')

    def load(self):
        self.fh = open(self.filename, 'r') # File handle

    def close(self):
        if self.fh is None:
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
        return self.tweet['tweet']['user']['followers_count']
        #return self.tweet['author']['followers']

    def get_user_mentioned(self): 
        if self.tweet is None: 
            return None
        return self.tweet['tweet']['entities']['user_mentions'].__len__() # how many users got mentioned. 

    def get_coExistHashtags(self): 
        # tells if the 2 hashtags appear next to one another (#tag1#tag2)
        # according to paper: this is an "eye-catcher"
        if self.tweet is None: 
            return None
        hashes = self.tweet['tweet']['entities']['hashtags']
        if hashes.__len__ == 1: ## this means there is only 1 hashtag in the comment, so we stop
            return 0
        count = 0
        for i in range(hashes.__len__()-1): 
            if (hashes[i]['indices'][1]+2 == hashes[i+1]['indices'][0]):
                # if end of first tag is 2 units from begin of second tag.  
                count = count + 1
        return count 

    def get_numberURLcontain(self):
        if self.tweet is None:
            return None
        urls = self.tweet['tweet']['entities']['urls']
        return urls.__len__()



