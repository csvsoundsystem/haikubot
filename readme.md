![haikubot](haikubot.png) [@ohhaikubot](http://www.twitter.com/ohhaikubot)
========================
This is the code for generating a haikubot on twitter.

Set this script up on a ec2 by first downloading the script into the default user directory:
```
wget http://raw.github.com/csvsoundsystem/haikubot/master/haikubot.py
```
Then create a cronjob by entering:
```
sudo crontab -u ec2-user -e
```
This will open a vi screen where you'll insert:
```
*/30 * * * * /usr/bin/python /home/ec2-user/haikubot.py
```
Exit this screen and save the cron job by pressing `ZZ`
<\br>
The script will send out no more than 5 haikus every half-hour,each spaced apart by 5 minutes.
