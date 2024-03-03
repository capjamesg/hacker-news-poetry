# hacker-news-poetry

Poetry generated programmatically from the front page of Hacker News. Reset hourly.

[View the latest poems](https://hnpoetry.jamesg.blog)

## Examples

- like a section in the server
- be historical and high
- the last safety of instability
- for all the last expectations
- for all the observational programming
- from Hacker News, I learned pdf
- my heart, keyboard

(Generated from the homepage on March 2nd, 2024)

## Installation

To install this software, run:

```
git clone https://github.com/capjamesg/hacker-news-poetry
cd hacker-news-poetry/
pip3 install tracery flair requests tqdm jinja2
```

To generate poems, run:

```
python3 hn.py
```

The script retrieves new titles and generates poems.

For testing, comment out the `get_front_page()` function call once you have run the script once. This will allow you to generate poems without retrieving the homepage and its associated titles for each time you run the script.

## License

This project is licensed under an [MIT license](LICENSE).
