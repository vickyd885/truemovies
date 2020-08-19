"""
    Process the dataset before dumping into Postgres
"""

import os
import gzip
import xml.etree.cElementTree as ET

import numpy as np
import pandas as pd
import sqlalchemy

"""
Fetch postgres settings from env
"""
pg_host = os.environ.get("pg_host")
pg_port = os.environ.get("pg_port")
pg_user = os.environ.get("pg_user")
pg_password = os.environ.get("pg_password")

if not all([pg_host, pg_port, pg_user, pg_password]):
    print("More than one db settings missing..postgres won't work")

movies_csv = "datasets/movies_metadata.csv"
wiki_csv = "datasets/cleaned-wiki.csv"

movies_df = pd.read_csv("datasets/movies_metadata.csv")
print(f"Size of csv df: {len(movies_df)}")

# Clean the dataset and work out the revenue ratio
movies_df = movies_df[movies_df['budget'].apply(lambda x: str(x).isdigit())]
movies_df['budget'] = movies_df['budget'].astype(str).astype(int)

movies_df = movies_df.drop(movies_df[(movies_df['revenue'] == 0.0) | (movies_df['budget'] == 0)].index)

movies_df['revenue_ratio'] = movies_df['revenue'].div(movies_df['budget'])
print(movies_df['revenue_ratio'])

print(movies_df['title'])





# Load the simplified wiki csv

wiki_df = pd.read_csv("datasets/cleaned-wiki.csv")
wiki_df = wiki_df.drop_duplicates(subset=['title'], keep='first')
print(wiki_df)


merged_df = pd.merge(movies_df, wiki_df, on="title")

# sample_movies = movies_df.loc[movies_df['title'] == 'Toy Story']
# sample_wiki = wiki_df.loc[wiki_df['title'] == 'Toy Story']
#
# sample_merge = merged_df.loc[merged_df['title'] == 'Toy Story']
# print(sample_movies, sample_wiki, sample_merge)


all_columns = list(merged_df)
columns_to_include = ['title', 'budget', 'year', 'revenue', 'rating', 'ratio', 'production_companies', 'url', 'abstract']
columns_to_exclude = set(all_columns) - set(columns_to_include)

sql_df = merged_df.drop(columns=list(columns_to_exclude))

print(sql_df)
# engine = sqlalchemy.create_engine(f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/database")
# con = engine.connect()
#
# table_name = 'top_movies'
# sql_df.to_sql(table_name, con)
#
#
# con.close()