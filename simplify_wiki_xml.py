"""
    Takes a wiki xml dump and creates a csv which has all the data required to
    merged with the imbdb dataset

    based on: https://www.heatonresearch.com/2017/03/03/python-basic-wikipedia-parsing.html
"""
import gzip
import xml.etree.cElementTree as ET
import codecs
import csv


wiki_xml = "datasets/enwiki-latest-abstract.xml.gz"
clean_wiki_csv = "datasets/cleaned-wiki.csv"

count = 0

valid_columns = ["title", "abstract", "url"]
valid_columns_set = set(valid_columns)

in_wiki_entry = False
wiki_entry = {}

wiki_data = gzip.open(wiki_xml, 'rb')

with codecs.open(clean_wiki_csv, "w", "utf-8") as cleaned_csv:

    csv_writer = csv.writer(cleaned_csv, quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(valid_columns)

    for event, elem in ET.iterparse(wiki_data, events=['start', 'end']):

        # Check to see if we're _entering_ a <doc>
        if event == "start" and elem.tag == "doc":
            in_wiki_entry = True
            wiki_entry = {}

        # If we're in a doc, keep iterating and capture any elements that we're interested in
        if in_wiki_entry:
            if elem.tag in valid_columns:
                if elem.tag == "title" and elem.text:

                    better_title = elem.text.split("Wikipedia:")[-1].split("(")[0]  # clean up the title
                    elem.text = better_title.strip()
                wiki_entry[elem.tag] = elem.text

        # If we are _exitjng_ a </doc> tag, then we should have enough data to save to our DF
        if in_wiki_entry and event == "end" and elem.tag == "doc":
            csv_writer.writerow([wiki_entry['title'], wiki_entry['abstract'], wiki_entry['url']])


    elem.clear()

