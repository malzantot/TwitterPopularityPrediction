from twitterparser import TwitterParser
import datetime, time
import numpy as np
import statsmodels.api as sm

def gen_features(hashtags):
    y = np.zeros(shape=(0))                # Y: target value
    X = np.zeros(shape=(0,5))       # X: predictors
    for htag in hashtags:
        print(htag)
        data = np.genfromtxt(format('results/%s_results.txt' %(htag)), delimiter=',')
        min_time = np.min(data[:, 0])
        max_time = np.max(data[:, 0])
        time_win = np.arange(min_time, max_time+1, 3600)
        win_cnt = time_win.shape[0]

        tag_X = np.zeros(shape=(win_cnt-1,5))
        tag_y = np.zeros(win_cnt-1)

        for ii in range(data.shape[0]):
            tweet_ts = data[ii][0]
            win_idx  = (tweet_ts - min_time) / 3600

            # Target value
            if win_idx > 0:   # We are not predicting for first window
                tag_y[win_idx-1] += 1

            if (win_idx < win_cnt-1): # Ware not generating features from last window
                tag_X[win_idx, 0] += 1              # Number of tweets
                tag_X[win_idx, 1] += data[ii][2]    # Number of retweets
                tag_X[win_idx, 2] += data[ii][1]    # Sum of followers
                tag_X[win_idx, 3] = max(tag_X[win_idx, 3], data[ii][1]) # Max number of followers
                tag_X[win_idx, 4] = datetime.datetime.fromtimestamp(data[ii][0]).hour

        X = np.vstack((X, tag_X))
        y = np.append(y, tag_y)

        #print tag_X
        #print tag_y

    # Constant term in regression
    X = sm.add_constant(X)
    return (X, y)

hashtags = ['gohawks', 'gopatriots', 'nfl', 'patriots', 'sb49', 'superbowl']
X, y = gen_features(hashtags)
# Fit regression model
results = sm.OLS(y, X).fit()

# Inspect the results
print(results.summary())
