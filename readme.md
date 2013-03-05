![haikubot](haikubot.png) [@ohhaikubot](http://www.twitter.com/ohhaikubot)
========================
-------------------------------------
### Generate a haiku bot on twitter.
-------------------------------------
Set this script up on an EC2 by first downloading the script into the default user directory:
```
wget http://raw.github.com/csvsoundsystem/haikubot/master/haikubot.py
```
Install pip:
```
sudo easy_install pip
```
Install python dependencies:
```
sudo pip install tweepy nltk 
```
Open up a python shell and run:
```
import nltk
nltk.download()
```
This will open a prompt to install `nltk` add-ons.  Select `cmudict` and download it.
<br/>
<br/>
Exit python and create a cronjob by entering:
```
sudo crontab -u ec2-user -e
```
This will open a vi screen where you'll insert:
```
*/30 * * * * /usr/bin/python /home/ec2-user/haikubot.py
```
Exit this screen and save the cron job by pressing `ZZ`
<br/>
<br/>
The script will send out no more than 5 haikus every half-hour, each spaced apart by 5 minutes.

### License

This work is licensed under a [Creative Commons Attribution 3.0 Unported License](http://creativecommons.org/licenses/by/3.0/deed.en_US)
