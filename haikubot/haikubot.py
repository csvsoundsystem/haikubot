import nltk
import tweepy
import pytumblr
import re, time, string, random, json, yaml
from collections import defaultdict
from nltk.corpus import cmudict

class HaikuBot(object):
    def __init__(
        self, 
        tmbl_blog = None,
        tmbl_consumer_key = None,
        tmbl_consumer_secret = None,
        tmbl_oauth_token = None,
        tmbl_oauth_token_secret = None,
        twt_consumer_key = None,
        twt_consumer_secret = None,
        twt_access_token = None,
        twt_access_token_secret = None,
        config = None,
        words = None,
        n_words = None,
        twt_list_slug = None,
        twt_list_owner = None):

        # words to search for
        self.words = words
        self.n_words = n_words if n_words is not None else 90

        # number to word lookup
        self.n2w = self.gen_n2w()

        # syllable dict
        self.cmu = cmudict.dict()

        if config is None:
            # tumblr config
            # blog to post to
            self.tmbl_blog  = tmbl_blog

            # api creds
            self.tmbl_config = {
                "ck" : tmbl_consumer_key,
                "cs" : tmbl_consumer_secret,
                "ot" : tmbl_oauth_token,
                "ots" : tmbl_oauth_token_secret
                }

            # twitter config
            # list to search for
            self.twt_list_slug = twt_list_slug
            self.twt_list_owner = twt_list_owner

            # api creds
            self.twt_config = {
                "ck" : twt_consumer_key,
                "cs" : twt_consumer_secret,
                "at" : twt_access_token,
                "ats" : twt_access_token_secret
                }
        else:
            # load config file
            c = yaml.safe_load(open(config))

            # tumblr config
            # blog to post to
            self.tmbl_blog  = c['tmbl_blog']

            # api creds
            self.tmbl_config = {
                "ck" : c['tmbl_consumer_key'],
                "cs" : c['tmbl_consumer_secret'],
                "ot" : c['tmbl_oauth_token'],
                "ots" : c['tmbl_oauth_token_secret']
            }

            # twitter config
            # list to search for
            self.twt_list_slug = c['twt_list_slug'] if c.has_key('twt_list_slug') else None
            self.twt_list_owner = c['twt_list_owner'] if c.has_key('twt_list_owner') else None

            # api creds
            self.twt_config = {
                "ck" : c['twt_consumer_key'],
                "cs" : c['twt_consumer_secret'],
                "at" : c['twt_access_token'],
                "ats" : c['twt_access_token_secret']
            }

        # connect to apis.
        self.tmbl_api = self.connect_to_tumblr()
        self.twt_api = self.connect_to_twitter()

    def connect_to_tumblr(self):
        c = self.tmbl_config
        return pytumblr.TumblrRestClient(c['ck'], c['cs'], c['ot'], c['ots'])

    def connect_to_twitter(self):
        c = self.twt_config
        auth = tweepy.OAuthHandler(c['ck'], c['cs'])
        auth.set_access_token(c['at'], c['ats'])
        return tweepy.API(auth)

    def gen_n2w(self):
        # generate number lookup for 0 - 99
        n2w = "zero one two three four five six seven eight nine".split()
        n2w.extend("ten eleven twelve thirteen fourteen fifteen sixteen".split())
        n2w.extend("seventeen eighteen nineteen".split())
        n2w.extend(tens if ones == "zero" else (tens + " " + ones) 
            for tens in "twenty thirty forty fifty sixty seventy eighty ninety".split()
            for ones in n2w[0:10])
        return n2w

    def number_of_syllables(self, word):
        return [len(list(y for y in x if y[-1].isdigit())) for x in self.cmu[word]]

    def detect_potential_haiku(self, tweet):
        tweet = tweet.encode('utf-8')

        # ignore tweets with @s, RT's and MT's and numbers greater than 3 digits
        if re.search(r'@|#|MT|RT|[0-9]{3,}', tweet):
            return None

        tweet = re.sub("&", "and", tweet)

        # remove punctuation
        tweet = tweet.translate(string.maketrans("",""), string.punctuation)

        # strip and lower text
        tweet = tweet.strip()
        tweet = tweet.lower()

        # split tweet into a list of words
        words = [w.strip() for w in tweet.split()]

        # replace numbers with words
        words = [self.n2w[int(w)] if re.search(r"0-9+", w) else w for w in words]

        # detect suitable tweets, annotate words with each words' number of syllables
        n_syllables = []
        clean_words = []

        for word in words:
            try:
                n_syllable = self.number_of_syllables(word)[0]
            except KeyError:
                return None
            if n_syllable > 7:
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

    def is_proper_haiku(self, haiku_dict):
        words = haiku_dict['words']
        syllables = haiku_dict['syllables']

        # make sure lines break at 5 and 12
        syllable_cum_sum = []
        syllables_so_far = 0
        for syllable in syllables:
            syllables_so_far += syllable
            syllable_cum_sum.append(syllables_so_far)
        if 5 in syllable_cum_sum and 12 in syllable_cum_sum:
            return True
        else:
            return False

    def format_haiku(self, haiku_dict):
        words = haiku_dict['words']
        syllables = haiku_dict['syllables']
        syllable_count = 0
        haiku = ''
        for i, word in enumerate(words):
            if syllable_count == 5:
                haiku = haiku + "\r\n"
            if syllable_count == 12:
                haiku = haiku + "\r\n"
            syllable_count += syllables[i]
            haiku += word.strip() + " "
        return haiku.strip() + "\r\n"

    def detect_haikus(self, tweets):
        if len(tweets)==0:
            return []
        print "detecting haikus..."
        haikus = []
        status_ids_so_far = []
        for tweet in tweets:
            h = self.detect_potential_haiku(tweet.text)
            if h is not None:
                if self.is_proper_haiku(h):
                    if tweet.id_str not in status_ids_so_far:
                        h_text = self.format_haiku(h)
                        print "HAIKU: ", h_text
                        haiku = {
                            "haiku_text": h_text,
                            "status_id": tweet.id_str,
                            "user": tweet.user.screen_name
                        }

                        status_ids_so_far.append(tweet.id_str)
                        haikus.append(haiku)

        print "found %d haikus..." % len(haikus)
        return haikus

    def fetch_new_tweets(self):
        if self.words is not None:
            print "searching twitter for keywords..."
            tweets = []
            for page in range(1, self.n_words):
                word = random.choice(self.words)
                try:
                    tweet_list = self.twt_api.search(q=word, lang="en")
                except tweepy.error.TweepError as e:
                    print e
                else:
                    tweets.extend(tweet_list)

        elif self.twt_list_slug is not None and self.twt_list_owner is not None:
            print "searching twitter list %s..." % self.twt_list_slug
            tweets = self.twt_api.list_timeline(
                owner_screen_name = self.twt_list_owner, 
                slug =  self.twt_list_slug,
                count = 200
            )

        else:
            raise("YOU MUST INCLUDE A LIST OF WORDS OR A TWITTER LIST TO FOLLOW!")
            return None

        return tweets

    def post_tweets(self, haikus):
        for h in haikus:
            
            haiku = h['haiku_text']
            user = "@%s" % h['user']
            tweet = haiku + " - " + user
            print "posting tweet - %s" % tweet
            try:
                self.twt_api.update_status(tweet)
            except tweepy.TweepError:
                continue

    def format_tumble(self, haiku):
        haiku_text = re.sub("\r\n", " <br></br> ", haiku['haiku_text'])
        url = "http://twitter.com/%s/status/%s" % (haiku['user'], haiku['status_id'])
        embdded_tweet = '''<p> <a href=%s target="_blank"> %s</a> </p>
                           <br></br>
                           <blockquote class="twitter-tweet"><p> <a href="%s"> original tweet </a></blockquote>
                           <script async src="//platform.twitter.com/widgets.js" charset="utf-8"></script>
                           ''' % (url, haiku_text, url)
        return {
            'body': embdded_tweet,
            'url': url
        }

    def post_tumbles(self, haikus):
        for h in haikus:
            tumbleku = self.format_tumble(h)
            try:
                print "posting tumble!"
                self.tmbl_api.create_text(self.tmbl_blog, body=tumbleku['body'], format="html")
            except Exception as e:
                print e
            time.sleep(2)

    def run(self):

        # find some tweets
        tweets = self.fetch_new_tweets()
        haikus = self.detect_haikus(tweets)

        # if we find a haiku, post it on twitter and tumblr
        if len(haikus)>0:

            self.post_tumbles(haikus)
            self.post_tweets(haikus)

if __name__ == '__main__':
    hb = HaikuBot(
        config = "../haikubot.yml",
        words = nltk.corpus.stopwords.words('english'),
        n_words = 50
    )
    hb.run()
    
