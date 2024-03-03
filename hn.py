import json
import os

import requests
import tqdm
import tracery
from flair.data import Sentence
from flair.models import SequenceTagger
from flair.nn import Classifier
from jinja2 import Template

HN_TOP_STORIES = "https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty"
N_STORIES = 30


def get_front_page() -> list:
    top_stories = requests.get(HN_TOP_STORIES).json()[:N_STORIES]

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
years = []

tagger = SequenceTagger.load("flair/pos-english")
ner_tagger = Classifier.load("ner")

word_to_title = {}

for heading in tqdm.tqdm(stories):
    sentence = Sentence(heading)
    ner_tagger.predict(sentence)

    for entity in sentence.get_spans("ner"):
        word_to_title[entity.text.lower()] = heading

        heading = [w for w in heading.split(" ") if w.lower() != entity.text.lower()]
        heading = " ".join(heading)

    sentence = Sentence(heading)
    tagger.predict(sentence)

    for entity in sentence:
        if entity.text.isdigit() and len(entity.text) == 4:
            years.append(entity.text)
            continue

        if len(entity.text) < 2 or not entity.text.isalpha():
            continue

        if entity.tag in ["NN", "NNS"]:
            nouns.append(entity.text.lower())
        elif entity.tag in ["JJ", "JJR", "JJS"]:
            adjectives.append(entity.text.lower())
        elif entity.tag in ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]:
            verbs.append(entity.text.lower())
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
            "in #years#, #noun#",
        ],
        "adjective": adjectives,
        "verb": verbs,
        "noun": nouns,
        "propernoun": proper_nouns + ["Hacker News"],
        "years": years,
    }
)

hn_poetry = [grammar.flatten("#origin#") for _ in range(30)]

hn_poetry = list(set(hn_poetry))


poems = []

# if "a" then word that starts with a vowel, add an "n"
for title in hn_poetry:
    words = title.split(" ")
    if title.split(" ")[0].lower() == "a":
        if title.split(" ")[1][0].lower() in "aeiou":
            title = "an " + title[2:]
    poems.append(title)

poems = {title: {"title": title, "components": set()} for title in poems}

for title, poem in poems.items():
    for word in title.split(" "):
        if word.lower() in word_to_title:
            poem["components"].add(word_to_title[word.lower()])

for title, poem in poems.items():
    poem["components"] = list(poem["components"])

poems = list(poems.values())

with open("poetry.html", "r") as f:
    template = Template(f.read())

with open("index.html", "w") as f:
    f.write(template.render(posts=poems))

os.system("mv -f index.html /var/www/hnpoetry/")
