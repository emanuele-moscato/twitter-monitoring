def print_rate_limits(session):
    rate_limit_status = session._session.rate_limit_status()
    
    for key in rate_limit_status['resources'].keys():
        for endpoint in rate_limit_status['resources'][key].keys():
            limit = rate_limit_status['resources'][key][endpoint]['limit']
            remaining = rate_limit_status['resources'][key][endpoint]['remaining']
            
            if limit!=remaining:
                print(endpoint)
                print(rate_limit_status['resources'][key][endpoint])
                

def get_users_ids(session, twitter_handles_list, twitter_ids_dict, n_users=None):
    if not n_users:
        n_users = len(twitter_handles_list)
        
    print(f"Fetching {n_users} ids")
    
    for i in range(n_users):
        twitter_handle = twitter_handles_list[i]
        
        print(f"Fetching id: @{twitter_handle}")
        
        try:
            twitter_id = session.user_id(twitter_handle)
            
            twitter_ids_dict.update(
                {twitter_handle: twitter_id}
            )
        except Exception as e:
            print(e)
            

def fetch_tweets(session, twitter_ids_dict, tweets_df):
    for twitter_handle in list(twitter_ids_dict.keys())[:15]:
        try:
            since_id = int(tweets_df[
                tweets_df['twitter_handle']==twitter_handle
            ]['twitter_id'].max())
        except Exception as e:
            since_id = None
        
        print(f"Fetching tweets: {twitter_handle}")
        print(f"since_id={since_id}")

        try:
            tweets = session.tweets(
                twitter_ids_dict[twitter_handle], since_id=since_id
            )
        
            for tweet in tweets:
                tweet.as_dict['twitter_handle'] = twitter_handle
                tweets_df = tweets_df.append(tweet.as_dict, ignore_index=True)
        except Exception as e:
            print("Error:", e)
            
    return tweets_df