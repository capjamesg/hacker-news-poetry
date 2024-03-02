import json
import string

import nltk
import requests
import tracery
from flair.data import Sentence
from flair.models import SequenceTagger
from jinja2 import Template


HN_TOP_STORIES = "https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty"


def get_front_page() -> list:
    top_stories = requests.get(HN_TOP_STORIES).json()[:30]

    stories = []
    for story_id in top_stories:
        story = requests.get(
            f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json?print=pretty"
        ).json()
        stories.append(story["title"])
    return stories


# SAVE AS stories.json
# with open("stories.json", "w") as f:
#     import json
#     json.dump(get_front_page(), f)

with open("stories.json", "r") as f:
    stories = json.load(f)

nouns = []
adjectives = []
verbs = []
proper_nouns = []

tagger = SequenceTagger.load("flair/pos-english")

word_to_title = {}

for heading in stories:
    sentence = Sentence(heading)
    tagger.predict(sentence)

    for entity in sentence:
        if len(entity.text) < 2:
            continue

        if entity.tag in ["NN", "NNS"]:
            nouns.append(entity.text.lower())
        elif entity.tag in ["JJ", "JJR", "JJS"]:
            adjectives.append(entity.text.lower())
        elif entity.tag in ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]:
            verbs.append(entity.text.lower())
        elif entity.tag in ["NNP", "NNPS"]:
            proper_nouns.append(entity.text)
        else:
            continue
        
        word_to_title[entity.text.lower()] = heading

grammar = tracery.Grammar(
    {
        "origin": [
            "the #adjective# #noun# of #noun#",
            "for all the #adjective# #noun#",
            "my heart, #noun#",
            "my #noun# is #adjective#",
            "like a #noun# in the #noun#",
            "from #propernoun#, I learned #noun#",
            "a #adjective# #propernoun#",
            "be #adjective# and #adjective#",
        ],
        "adjective": adjectives,
        "verb": verbs,
        "noun": nouns,
        "propernoun": proper_nouns + ["Hacker News"],
    }
)

hn_poetry = [grammar.flatten("#origin#") for _ in range(30)]

hn_poetry = list(set(hn_poetry))

poems = {title: {"title": title, "components": []} for title in hn_poetry}

for title, poem in poems.items():
    for word in title.split(" "):
        if word in word_to_title:
            poem["components"].append(word_to_title[word])

poems = list(poems.values())

with open("poetry.html", "r") as f:
    template = Template(f.read())

with open("poetry_results.html", "w") as f:
    f.write(template.render(posts=poems))