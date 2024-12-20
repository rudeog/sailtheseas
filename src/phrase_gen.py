# generate interesting phrases based on input supplied
import random

from util import custom_hash
# in response to a player giving their name
player_name_phrases = ["Ok (if that's your real name),",
                       "I have a relative with that name, they are in jail,",
                       "That must have been rough for you in school,",
                       "I'm not even going to ask how to pronounce that, anyway,",
                       "I don't know how you live with yourself,",
                       "Hopefully your siblings were not as unlucky,",
                       "I had a pet monkey with that name,",
                       "That sounds French, or maybe Irish,",
                       "Very fancy!"]
crew_name_phrases = ["An excellent hire!", "Looks a bit shifty, but ok.", "A pillar of our society!",
                     "Will do I suppose.", "Better keep an eye on that one.", "Very experienced, I hear.",
                     "Their references checked out.", "With a name like that, I hope we can trust them.",
                     "Sounds foreign.", "Good choice."]


ship_name_phrases = ["A ship with that name is bound to have good luck.",
                     "Well, I never heard of such a thing.",
                     "I'll get that stenciled on right away.",
                     "Well that seems a bit pretentious.",
                     "A bold move!",
                     "Hilarious!",
                     "Sounds like you put a lot of thought into that."]
places_phrases = ["I can't remember whether that's in the North or the South. Oh well.",
                  "I hear they make great pineapple cakes there.",
                  "My great uncle Folderol was from there.",
                  "My deceased aunt used to live there as well.",
                  "I've never heard of the place.",
                  "A likely story.",
                  "The weather is pretty changeable in those parts, I hear."]



def get_phrase(text, phrases):
    """
    return an interesting phrase from one of the phrase lists, given a word
    :param text:
    :param phrases:
    :return:
    """
    hash_value = custom_hash(text)  # get a consistent value across runs
    # Use modulo to map the hash value into the range [0, num-1]
    result = hash_value % len(phrases)
    return phrases[result]
