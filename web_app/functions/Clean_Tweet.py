import re

def clean_tweet(tweet):
    '''Cleaning raw tweet for modeling'''
    tweet = tweet.lower()
    emoji_list = tweet.split()                  # Creating list to reference emojis
    tweet = re.sub('[^a-z 0-9]', '', tweet)
    tweet = tweet.split(' ')
    output_string = ''

    # Creating output string, handeling links and emojis
    for index, token in enumerate(tweet):
        if token[0:4] == 'http':
            pass
        elif token == '':
            try:
                output_string = output_string + ' ' + str(ord(emoji_list[index]))   # Replacing emoji with number value
            except:
                # Token is not an emoji
                pass
        else:
            output_string = output_string + ' ' + token

    output_string = output_string[1:]

    return output_string