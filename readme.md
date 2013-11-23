HaikuBot
==========
Generate a haiku bot that posts to twitter and tumblr.

## dependencies
```
git clone https://github.com/tumblr/pytumblr.git
cd pytumblr
sudo python setup.py install 
```
```
git clone https://github.com/tweepy/tweepy.git
cd tweepy
sudo python setup.py install 
```
```
sudo pip install nltk
```
```
python
>>> import nltk
>>> nltk.download()
>>> # select "cmudict" and "stopwords"
```

## install
```
git clone https://github.com/abelsonlive/haiku-bot.git
cd haiku-bot && sudo python setup.py install
```

## run 
### With a config file
#### config:
`haiku-bot.yml`:
```
tmbl_blog : <your haikubots tumblr account>
tmbl_consumer_key : xxxxxxxx
tmbl_consumer_secret : xxxxxxxx
tmbl_oauth_token : xxxxxxxx
tmbl_oauth_token_secret : xxxxxxxx
twt_consumer_key : xxxxxxxx
twt_consumer_secret : xxxxxxxx
twt_access_token : xxxxxxxx
twt_access_token_secret : xxxxxxxx
twt_list_slug : members-of-congress # optionally follow a twitter list
twt_list_owner : cspan # optionally follow a twitter list
```
#### twitter list search w/ config
```
from haiku_bot import HaikuBot

hb = HaikuBot(config="haiku-bot.yml")
hb.run()
```

#### twitter word search w/ config
```
import nltk
from haiku_bot import HaikuBot

hb = HaikuBot(
  config="haiku-bot.yml"
  words = nltk.corpus.stopwords.words('english') # a list of arbitrary words, here we're using stopwords from nltk
  )
hb.run()
```
### Without a Config File
#### twitter list search w/o config
```
from haiku_bot import HaikuBot

hb = HaikuBot(
  tmbl_blog = <your haikubots tumblr account>,
  tmbl_consumer_key = xxxxxxxx,
  tmbl_consumer_secret = xxxxxxxx,
  tmbl_oauth_token = xxxxxxxx,
  tmbl_oauth_token_secret = xxxxxxxx,
  twt_consumer_key = xxxxxxxx,
  twt_consumer_secret = xxxxxxxx,
  twt_access_token = xxxxxxxx,
  twt_access_token_secret = xxxxxxxx,
  twt_list_slug = members-of-congress # optionally follow a twitter list,
  twt_list_owner = cspan # optionally follow a twitter list,
)
hb.run()
```
#### twitter word search w/o config
```
import nltk
from haiku_bot import HaikuBot

hb = HaikuBot(
  tmbl_blog = <your haikubots tumblr account>,
  tmbl_consumer_key = xxxxxxxx,
  tmbl_consumer_secret = xxxxxxxx,
  tmbl_oauth_token = xxxxxxxx,
  tmbl_oauth_token_secret = xxxxxxxx,
  twt_consumer_key = xxxxxxxx,
  twt_consumer_secret = xxxxxxxx,
  twt_access_token = xxxxxxxx,
  twt_access_token_secret = xxxxxxxx,
  words = nltk.corpus.stopwords.words('english') # a list of arbitrary words, here we're using stopwords from nltk
)
```
