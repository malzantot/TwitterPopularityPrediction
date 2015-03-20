
## dumb ass EE239AS Project 3: Popularity Prediction on Twitter
## Winter 2015
## Part 3

from twitterparser import TwitterParser
import numpy as np
import pandas as pd 
import statsmodels.api as sm
import statsmodels.formula.api as smf
import statsmodels.graphics.api as smg 

import matplotlib.pyplot as plt

# Return the average number of followers, average number of retweets and average number
# of tweets per hour for a given hashtag.

def process_hashtag(hashtag):
    
    #========== extract needed factors    
    
    parser = TwitterParser(hashtag)
    parser.load()
    results_fh = open(format('%s_factors.txt' %(hashtag)), 'w')

    followers_cnt = []
    retweets_cnt = []
    tweet_time = []
    userMentioned = [] 
    coexistHashTag = []
    numberURLcontain = []
    tweetType = []
    
    while parser.next_tweet() == 0:
        
        followers_cnt.append(parser.get_followers_count())
        retweets_cnt.append(parser.get_retweet_count())
        tweet_time.append(parser.get_post_time())
        userMentioned.append(parser.get_user_mentioned())
        coexistHashTag.append(parser.get_coExistHashtags())
        tweetType.append(parser.get_tweet_type())
        numberURLcontain.append(parser.get_numberURLcontain())
        
        results_fh.write( str(parser.get_post_time()) + ',' + str(parser.get_followers_count()) + ',' + str(parser.get_retweet_count()) + ',' + str(parser.get_user_mentioned()) + ',' + str(parser.get_coExistHashtags()) + ',' + str(parser.get_numberURLcontain()) +',' + str(parser.get_tweet_type()) + '\n' )

    parser.close()    
    return (np.mean(followers_cnt), np.mean(retweets_cnt), np.mean(userMentioned), np.mean(coexistHashTag), np.mean(numberURLcontain) )

def fit_LM (htag):
    
    print('Hashtag #%s' %(htag))
    #========== iter over each hour 
    
    df = pd.read_csv(('%s_factors.txt' %(htag))) 
    df.columns = ['time_stamp', 'followers', 'retweets', 'userMentioned', 'coexistHash', 'urlCount','type']
    df = df.sort_index(by=['time_stamp'], ascending=[True])
    
    time_stamp = df.ix[:,0]
    time_split = 3600 # 3600 unit is 1 hour. 
    begin_time = df['time_stamp'].min() # time of line_count entry 
    
    duration = 0
    dormant = 1
    means = None 
    
    for i in range(df.__len__()-1) : # go through each 'time-slot' (1 hour)
        end_time = begin_time + time_split 
        oneHour = df[ (time_stamp>=begin_time) & (time_stamp<end_time) ] 
        begin_time = end_time # update begin-time    
        duration = duration+1 # time duration.
        if (duration > (df['time_stamp'].max() - begin_time) / time_split ):
            break 
        if (oneHour.__len__() < 1): # if no tweet can be found 
            dormant = dormant + 1
        else:      
            if (duration == 1): 
                means = oneHour.mean()
                means = pd.concat( [ means, pd.Series(oneHour.__len__(),['count']) ] ) 
            else:
                means = pd.concat( [ means, pd.concat ( [ oneHour.mean() , pd.Series(oneHour.__len__(),['count']) ] ) ] )       
            
    hourData = means.values.reshape(means.__len__()/df.columns.__len__(),df.columns.__len__()) # divide how many columns there are
    hourData = pd.DataFrame(hourData)
    hourData.columns = ['time_stamp', 'followers', 'retweets', 'userMentioned', 'coexistHash', 'urlCount', 'count'] # put the value to be predicted in the 2nd column 
    
    temp = hourData.iloc[1:(hourData.__len__()+1)] # remove row 1 
    data_fit = hourData.iloc[0:hourData.__len__()] # remove last row, can't be used in analysis 
    data_fit.insert(1, 'count2' , pd.DataFrame( temp['count'].values.reshape(temp['count'].__len__(),1) ) )
    data_fit.__delitem__('time_stamp')

    #========== fit model 

    data_fit = sm.add_constant(data_fit) ## use hour X to predict hour X+1
    lm = smf.ols('np.log(count2) ~ np.log(followers) + retweets + userMentioned + coexistHash + urlCount', data=data_fit).fit()
    
    y = lm.fittedvalues
    y_true = np.log( data_fit['count2'].iloc[1:(y.__len__()+1)] )
    
    fig, ax = plt.subplots(figsize=(8,6)) # plot 
    ax.set_title(htag+': Observed vs. Fitted tweet count per hour')
    ax.set_xlabel('log Observed values')
    ax.set_ylabel('log Fitted values');
    ax.plot(y_true, y, 'o') # OLS
    plt.savefig(htag+'obsVsFitted_ols.png')
    print ( lm.summary() )
    
    data_fit.loc[:,1] = np.log(data_fit['followers'])
    data_fit.__delitem__('count') 
    data_fit = data_fit.iloc[0:(data_fit.__len__()-1)] # remove the stupid NAN in last row. 
    y = data_fit['count2'].values # true y
    data_fit.__delitem__('count2')
    x = data_fit.values
    x = sm.add_constant(x, prepend=True) # model X
    
    gauss_log = sm.GLM(y, x, family=sm.families.Gaussian(sm.genmod.families.links.log))
    gauss_log_results = gauss_log.fit()
    print(gauss_log_results.summary())
    
    fig, ax = plt.subplots(figsize=(8,6)) # plot 
    ax.set_title(htag+': Observed vs. Fitted tweet count per hour')
    ax.set_xlabel('log Observed values')
    ax.set_ylabel('log Fitted values');
    ax.plot(y, gauss_log_results.fittedvalues, 'o')  
    plt.savefig(htag+'obsVsFitted_gauss_logLink.png')
    
    fig, ax = plt.subplots(figsize=(8,6)) # plot 
    ax.set_title(htag+': Tweet count per hour')
    ax.set_xlabel('Hour')
    ax.set_ylabel('Tweet Count');
    ax.plot( gauss_log_results.fittedvalues, 'ro', label='fitted')  
    ax.plot( y, 'b-', label='true')
    ax.legend(loc="best");
    plt.savefig(htag+'tweetPerHour.png')

    #========== fit model 

htag = ['gohawks', 'gopatriots', 'nfl', 'patriots', 'sb49', 'superbowl']

for tag in htag: 
##!! only need to run this once loop ONCE. 
    followers, retweets, usersMention, coexistHash, urlCount = process_hashtag(htag)
    
for tag in htag:
    fit_LM(tag)

