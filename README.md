IfMeetThenTweet
===============

If a new user joins a meetup group (and they have a twitter handle), tweet them a greeting!

How-To
------

* Clone the repo.
* Run `pip install -r requirements`
* Add your Meetup & Twitter API keys to the ``api_keys.py`` file.  You will have to create a new application with Twitter. More information can be found here on where to get your keys: http://www.meetup.com/meetup_api/key/ and https://dev.twitter.com/apps/new
* In your console within the repo's directory, run ``python imtt.py``.  To have more output, run ``python imtt.py -d`` or ``python imtt.py --debug``.
* Watch your Twitter glory.
* Either run the script yourself, or attach it to a cron tab.

This script makes two logs: one for debugging messages, and one for Twitter handles tweeted.

**NEVER** commit your ``api_keys.py`` file!