#!/usr/bin/env python

from datetime import date
from optparse import OptionParser, make_option
from urllib2 import urlopen

import logging
import simplejson as json

import api_keys as k
import twitter


# logging setup: general logger
logger = logging.getLogger('IFmeetTHENtweet')
logger.setLevel(logging.DEBUG)

file_log = logging.FileHandler('IFmeetTHENtweet' + str(date.today()) + '.log')
file_log.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_log.setFormatter(file_formatter)

console_log = logging.StreamHandler()
console_formatter = logging.Formatter('%(message)s')
console_log.setFormatter(console_formatter)

logger.addHandler(file_log)
logger.addHandler(console_log)


def tweet_people(twitter_api, twitter_handles, twitter_log, personal_handle):
    """Tweets users that are new members to the meetup group."""
    already_msg = []
    already_msg.append(personal_handle)  # don't reply to myself

    fp = open(twitter_log, 'r')
    for handle in fp.readlines():
        already_msg.append(handle.strip('\n'))
    fp.close()

    users_to_tweet = twitter_handles
    tweeted_users = []
    for user in users_to_tweet:
        if user.lower() not in already_msg:
            greeting = '@PyLadiesSF has a new member! Welcome, %s!' % user
            try:
                post_status = twitter_api.PostUpdate(greeting)
                tweeted_users.append(user)
                logger.debug('Tweeted: %s' % greeting)
            except Exception, e:
                logger.exception('whoops, error: %s' % e)
                raise e

    fp = open(twitter_log, 'a')
    for user in tweeted_users:
        fp.write('%s\n' % user.lower())
    fp.close()
    logger.debug('Tweeted %d users.' % len(tweeted_users))

    return


def parse_member_twitter(members_json_list):
    """Parses out the twitter handle associated with a member's profile, if the handle exists."""
    twitter_handles = []
    member_list = members_json_list[0]['results']
    for member in member_list:
        if member.get('other_services').get('twitter') is not None:
            handle = member.get('other_services').get('twitter').get('identifier')
            if handle.startswith('@'):
                twitter_handles.append(handle)

    return twitter_handles


def get_members(meetup_key, meetup_group, total_members):
    """Retrieves twitter handles from new members.  Max entries per call = 200."""
    members_json_list = []
    i = 0
    while total_members > 0:
        # note: It is possible to get negative total_members if someone joins in the middle of this script
        members_url = 'https://api.meetup.com/members.json/?group_id=%s&key=%s&offset=%s' % (meetup_group, meetup_key, i)
        logger.debug('Calling %s' % members_url)
        members_response = urlopen(members_url)
        members_json = json.load(members_response, encoding='ISO-8859-1')
        members_json_list.append(members_json)
        total_members -= members_json_list[i]['meta']['count']
        i += 1

    return members_json_list


def get_member_count(meetup_key, meetup_group):
    """Grabs the count of members for a particular group."""
    meetup_url = 'https://api.meetup.com/2/groups.json/?group_id=%s&key=%s' % (meetup_group, meetup_key)
    logger.debug('Calling %s' % meetup_url)

    entry_response = urlopen(meetup_url)
    logger.debug('Called url successfully. Now parsing the json response.')

    json_parse = json.load(entry_response)
    total_members = json_parse.get('results')[0].get('members')

    if isinstance(total_members, int):
        return total_members
    else:
        return 0


def grab_api():
    meetup_key = k.MEETUP_API_KEY
    meetup_group = k.MEETUP_GROUP_ID

    twAPI = twitter.Api(consumer_key=k.TWITTER_CONSUMER_KEY,
                        consumer_secret=k.TWITTER_CONSUMER_SECRET,
                        access_token_key=k.TWITTER_ACCESS_TOKEN,
                        access_token_secret=k.TWITTER_ACCESS_TOKEN_SECRET)
    personal_handle = k.TWITTER_HANDLE

    return meetup_key, meetup_group, twAPI, personal_handle


def main():
    parser = OptionParser()
    parser.add_option('-d', '--debug', action='store_true', dest='debug',
                      help='Increases level of output for fun, or diagnostic purposes.')
    parser.set_defaults(debug=False, hash_list=None, portion='a')

    (options, args) = parser.parse_args()

    if options.debug:
        console_log.setLevel(logging.DEBUG)

    try:
        logger.debug('Grabbing API keys.')
        meetup_key, meetup_group, twAPI personal_handle = grab_api()
    except Exception, e:
        logger.exception('Twitter API grab error: %s' % e)
        return
    try:
        logger.debug('Grabbing Meetup Member Count.')
        total_members = get_member_count(meetup_key, meetup_group)
        logger.debug('Found %d members.' % total_members)
    except Exception, e:
        logger.exception('Member Count/API error: %s' % e)
        return
    try:
        logger.debug('Grabbing Members\' Public Profiles.')
        members_json_list = get_members(meetup_key, meetup_group, total_members)
    except Exception, e:
        logger.exception('Member Profile/API error: %s' % e)
        return

    logger.debug('Parsing the Meetup JSON response to a list of Twitter Handles.')
    twitter_handles = parse_member_twitter(members_json_list)
    logger.debug('Found %d members with twitter handles.' % len(twitter_handles))

    twitter_log = 'twitter_IFTTT.log'
    try:
        logger.debug('Attempting to tweet new members.')
        tweet_people(twAPI, twitter_handles, twitter_log, personal_handle)
    except Exception, e:
        logger.exception('Twitter API/tweeting error: %s' % e)

    logger.debug('All finished.  w00t, IFTTT pwned again.')

    return

if __name__ == '__main__':
    main()
