## EE239AS Project 3: Popularity Prediction on Twitter
## Winter 2015
## Part 1

from twitterparser import TwitterParser
import numpy as np
import matplotlib, matplotlib.pyplot as plt

# Return the average number of followers, average number of retweets and average number
# of tweets per hour for a given hashtag.
def process_hashtag(hashtag):
    parser = TwitterParser(hashtag)
    parser.load()
    results_fh = open(format('results/%s_results.txt' %(hashtag)), 'w')
    followers_cnt = []
    retweets_cnt = []
    tweet_time = []
    while parser.next_tweet() == 0:
        followers_cnt.append(parser.get_followers_count())
        retweets_cnt.append(parser.get_retweet_count())
        tweet_time.append(parser.get_post_time())
        results_fh.write(str(parser.get_post_time()) + ',' + \
            str(parser.get_followers_count()) + ', ' + \
            str(parser.get_retweet_count()) + '\n')
    parser.close()

    # Plot a histogram for the number of tweets per hour
    min_time = np.min(tweet_time)
    max_time = np.max(tweet_time)
    plt.hist(tweet_time, bins = range(min_time, max_time+3600, 3600))
    plt.title(format('Number of Tweets per Hour for #%s' %(hashtag)))
    plt.xlabel('Time')
    plt.ylabel('Number of Tweets in Hour')
    #plt.show()
    plt.savefig(format('figures/%s.png' %(hashtag))) # Save to png

    ## Compute the mean of number of tweets per hour
    tweets_per_hour = np.zeros((max_time - min_time)/3600 + 1)
    for tt in tweet_time:
        tweets_per_hour[(tt-min_time)/3600] += 1

    print('%d - %d' %(min_time, max_time))
    #print('%d %d ' %(np.min(tweets_per_hour), np.max(tweets_per_hour)))
    #print('Length : %d' %(np.shape(tweets_per_hour)[0]))

    return (np.mean(followers_cnt), np.mean(retweets_cnt), np.mean(tweets_per_hour))


hashtags = ['gohawks', 'gopatriots', 'nfl', 'patriots', 'sb49', 'superbowl']

for tag in hashtags:
    print('Hashtag #%s' %(tag))
    followers, retweets, avg_per_hour = process_hashtag(tag)
    print('\t\tAverage number of followers per tweet: %f' %(followers))
    print('\t\tAverage number of retweets : %f' %(retweets))
    print('\t\tAverage number of tweets per hour: %f' %(avg_per_hour))
    print(' ')
    print(' ')
