from nltk.corpus import cmudict
import tweepy
import oauth2
import re
import time
import string


"""
set this script up on a ec2 crontab by entering the following:

sudo crontab -u ec2-user -e

and then in vi insert:

00 * * * * /usr/bin/python /home/ec2-user/haikubot.py

this will run the haikubot every hour,

the script will send out no more than 10 haikus every hour,
each spaced apart by 5 minutes.
"""


# initialize carnegie mellon dictionary
d = cmudict.dict()

# initialize twitter api connection
consumer_key = "xxxxxxxxxxxxxxx"
consumer_secret = "xxxxxxxxxxxxxxx"
access_token = "xxxxxxxxxxxxxxx"
access_token_secret = "xxxxxxxxxxxxxxx"

# authenticate
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


# helper functions
def test_for_digits(tweet):
    if re.search("[0-9]+", tweet):
        return True
    else:
        return False

def number_of_syllables(word):
    return [len(list(y for y in x if y[-1].isdigit())) for x in d[word]]

def remove_duplicates(input):
    output = []
    for x in input:
        if x not in output:
            output.append(x)
    return output

def detect_potential_haiku(tweet):
    tweet = tweet.encode('utf-8')
    # ignore any tweet with digits in it
    if test_for_digits(tweet):
        return None

    # clean out @'s, #'s, RT's, MT's, and punctuation
    tweet = re.sub('@', '', tweet)
    tweet = re.sub('#', '', tweet)
    tweet = re.sub('RT', '', tweet)
    tweet = re.sub('MT', '', tweet)
    tweet = tweet.translate(string.maketrans("",""), string.punctuation)
    tweet = tweet.strip()
    tweet = tweet.lower()

    # split tweet into a list of words
    words = tweet.split()

    # detect suitable tweets, annotate words with each words' number of syllables
    n_syllables = []
    clean_words = []

    for word in words:
        try:
            n_syllable = number_of_syllables(word)[0]
        except KeyError:
            return None
        if n_syllable > 5:
            return None
        else:
            n_syllables.append(n_syllable)
            clean_words.append(word.strip().lower())

    # remove tweekus that are really long
    clean_tweet = ' '.join(clean_words)
    if len(clean_tweet) > 125:
        return None
    # make sure tweets have the proper number of syllables
    total_syllables = sum(n_syllables)
    if total_syllables == 17:
        return {"words" : clean_words, "syllables" : n_syllables }
    else:
        return None

def is_proper_haiku(haiku_dict):
    words = haiku_dict['words']
    syllables = haiku_dict['syllables']

    # make sure lines break at 5 and 12
    syllable_cum_sum = []
    syllables_so_far = 0
    for syllable in syllables:
        syllables_so_far = syllables_so_far + syllable
        syllable_cum_sum.append(syllables_so_far)
    if 5 in syllable_cum_sum and 12 in syllable_cum_sum:
        return True
    else:
        return False


def format_haiku(haiku_dict, user, tweet_id):
    words = haiku_dict['words']
    syllables = haiku_dict['syllables']
    syllable_count = 0
    haiku = ''
    for i, word in enumerate(words):
        if syllable_count == 5:
            haiku = haiku + " / "
        if syllable_count == 12:
            haiku = haiku + " / "
        syllable_count = syllable_count + syllables[i]
        haiku = haiku + " " + word.strip()
    return haiku + " " + "https://twitter.com/" + str(user) + "/status/" + str(tweet_id)


"""

Here's where the haiku bot starts!


"""


print "scraping twitter feed..."
tweets = []
for page in range(1,100):
    try:
        page_of_tweets = api.search("the", lang="en", page=page) # searching for "the" doubly ensures english results
    except tweepy.error.TweepError:
        pass
    tweets.extend(page_of_tweets)

haikus = []
for tweet in tweets:
    h = detect_potential_haiku(tweet.text)
    if h is not None:
        if is_proper_haiku(h):
            the_haiku = format_haiku(h, tweet.from_user ,tweet.id_str)
            haikus.append(the_haiku)

haikus = remove_duplicates(haikus)

if len(haikus)>10:
    haikus = haikus[0:11]

for haiku in haikus:
    try:
        status = api.update_status(haiku)
    except tweepy.error.TweepError:
        pass
    time.sleep(300)
    print "tweeting", haiku
