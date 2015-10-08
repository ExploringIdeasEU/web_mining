#!/usr/bin/env python

"""
timelinearchiver: python twitter timeline archiver, output in CSV format
"""
__version__ = '0.1'
__author__  = 'ExploringIdeas.eu'
__license__ = 'MIT'


import sys
import os
import time
import argparse
import csv
import email.utils

import twitter

#configuration file
import config


def twitter_connect():
    """ create twitter API object """
    if config.consumer_key is not None:
        auth = twitter.OAuth(config.access_key, config.access_secret, config.consumer_key, config.consumer_secret)
        api = twitter.Twitter(auth = auth)
    else:
        api = twitter.Twitter()
    return api


def twitter_statuses(api, username, archive_size = 0, min_id = None, delay = 1):
    """  """
    page = 1
    last_id = None
    statuses = []

    user_info = api.users.show(screen_name = username)

    total_count = user_info["statuses_count"]
    fetch_count = total_count - archive_size
    print("[+]Statuses: new:%d old:%d total:%d" % (fetch_count, archive_size, total_count))

    try:
        found_last = False
        while len(statuses) < fetch_count:
            
            ## future: put in try/except if fails
            if last_id:
                results = api.statuses.user_timeline(screen_name = username, 
                                                     count = config.per_page, 
                                                     include_rts = config.include_rts, 
                                                     max_id = last_id - 1)
            else:
                results = api.statuses.user_timeline(screen_name = username, 
                                                     count = config.per_page,
                                                     include_rts = config.include_rts)

            if not results:
                print("[-]no results: exiting")
                break

            cumulative_count = len(statuses) + len(results)
            if cumulative_count > fetch_count:
                cumulative_count = fetch_count
            print("[+]page %d (%d/%d statuses)" % (page, cumulative_count, fetch_count))
            page += 1

            for status in results:
                if min_id is not None and str(status["id"]) == min_id:
                    found_last = True
                    break

                tweet = status["text"]
                tweet = tweet.replace("\n", " ")
                ## TODO: resolve shortened links
                status["text"] = tweet

                timestamp = email.utils.parsedate(status["created_at"])
                status["created_at"] = time.strftime("%Y-%m-%d %H:%M:%S", timestamp)

                #print("%d (%s) %s" % (status["id"], status["created_at"], status["text"]))

                last_id = status["id"]
                statuses.append(status)

            if found_last:
                print("[+]last tweet: exiting")
                break

            time.sleep(delay)

    except KeyboardInterrupt:
        print("[-]terminated (fetched %d/%d statuses)" % (len(statuses), fetch_count))
        if config.save_partial:
            print("[-]not saving to disk to avoid gaps in archive")
            sys.exit(1)

    print("[+]finished (found %d new tweets)" % len(statuses))
    statuses.reverse()
    return statuses


if __name__ == "__main__":

    ## parse command-line arguments
    parser = argparse.ArgumentParser(description='Archive a user timeline')

    parser.add_argument('-u', action='store', dest='username', required=True, help='twitter screen name to be archived')
    parser.add_argument('-f', action='store', dest='filename', help='archive filename')
    parser.add_argument('-d', action='store', dest='delay', default = 3, help='delay between pages fetching')

    parser.add_argument('--version', action='version', version='%(prog)s {version}'.format(version=__version__))

    args = parser.parse_args()


    config.archive_username = args.username

    if args.filename is not None:
        config.archive_filename = args.filename
    else:
        config.archive_filename = config.archive_username
    ## savaing data to file
    config.archive_filename += ".csv"

    config.delay = float(args.delay)


    print("[+]saving to file %s" % config.archive_filename)


    ## test if archive exist
    config.archive_exist = False
    ## if exist, extract the last id
    config.last_id = None
    config.archive_count = 0

    if os.path.exists(config.archive_filename):
        config.archive_exist = True

        try:
            fd = open(config.archive_filename, "r")
            reader = csv.reader(fd)
            lines = list(reader)
            row = lines[-1]
            config.archive_count = len(lines)
            config.last_id = row[config.archive_attributes.index("id")]
            print("[+]existing archive found, seeking up to ID %s" % config.last_id)
            fd.close()
        except:
            config.archive_exist = False
            config.last_id = None



    ## twiter connection object
    api = twitter_connect()


    ## get statuses from user profile
    statuses = twitter_statuses(api = api, 
                                username = config.archive_username, 
                                min_id = config.last_id, 
                                delay = config.delay, 
                                archive_size = config.archive_count)


    ## saving statuses to file
    ## format: id, date, retweet-count, status
    fd = open(config.archive_filename, "a")
    writer = csv.writer(fd)
    for status in statuses:
            row = tuple(map(lambda attribute: status[attribute], config.archive_attributes))
            writer.writerow(row)
    fd.close()


    #sys.exit()






