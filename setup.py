import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-limit',help='The number of subreddit posts for a spotify song/album',type=int)
    parser.add_argument('-filter',help='The time filter to use to check posts:\nday, hour, month, week, year ',type=str)
    args = parser.parse_args()
    
    #Exit if help
    if hasattr(args,'help'):
        exit(1)

    #Set defaults if none
    if args.limit is None:
        args.limit = 20
    if args.filter is None:
        args.filter = 'day'
    
    return args