"""
EE239AS Project

"""
from twitterparser import TwitterParser

gohawks = TwitterParser("gohawks")
gohawks.load()
cnt = 0
while cnt < 5 and gohawks.next_tweet() == 0:
    tweet = gohawks.get_tweet()
    followers_cnt = gohawks.author_followers_count()
    print("%d %s %d" %(followers_cnt, tweet['tweet']['text']))
    cnt += 1

gohawks.close()