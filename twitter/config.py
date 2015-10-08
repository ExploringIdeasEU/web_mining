
# attributes to archive. the 0th item must always be the tweet ID.
# "text" is the normal UTF-8 text;
archive_attributes = [ "id", "created_at", "retweet_count", "text" ]

# delay between fetching individual pages
delay = 2.0

per_page = 50

# include RTs by other people in the archive?
include_rts = True

# by default, refuse to save partial archive results (after exiting the
# process early) to prevent gaps in archives. 
save_partial = False


# Twitter authentication tokens
consumer_key = None
consumer_secret = None
access_key = None
access_secret = None

