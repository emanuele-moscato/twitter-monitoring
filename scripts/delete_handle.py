import json
import pickle


IDS_PATH = '../data/data_tweepy/twitter_ids_dict.json'
DATA_PATH = '../data/data_tweepy/tweets_df.pkl'

HANDLES_TO_DELETE = ['welikechopin', 'welikeduel']

DELETE_TWEETS = True


def main():
    with open(IDS_PATH, 'r') as f:
        twitter_ids_dict = json.load(f)
        
    for handle in HANDLES_TO_DELETE:
        print(f"Deleting handle: {handle}")
        
        if handle in list(twitter_ids_dict.keys()):
            del twitter_ids_dict[handle]
            
            if DELETE_TWEETS:
                with open(DATA_PATH, 'rb') as f:
                    tweets_df = pickle.load(f)
                    
                tweets_df = tweets_df[tweets_df['twitter_handle']!=handle]
                
                with open(DATA_PATH, 'wb') as f:
                    pickle.dump(tweets_df, f)
                
            
        else:
            print(f"Handle '{handle}' not found")
            
    with open(IDS_PATH, 'w') as f:
        json.dump(twitter_ids_dict, f)


if __name__=='__main__':
    main()