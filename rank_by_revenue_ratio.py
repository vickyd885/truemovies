"""
    Process the dataset before dumping into Postgres
"""

import os
import pandas as pd
import sqlalchemy

"""
Fetch postgres settings from env
"""
pg_host = os.environ.get("POSTGRES_HOST")
pg_port = os.environ.get("POSTGRES_PORT")
pg_user = os.environ.get("POSTGRES_USER")
pg_password = os.environ.get("POSTGRES_PASSWORD")
pg_db = os.environ.get("POSTGRES_DATABASE")

if not all([pg_host, pg_port, pg_user, pg_password, pg_db]):
    print("More than one db settings missing..postgres won't work")

"""
Paths and other settings
"""
movies_csv = "datasets/movies_metadata.csv"
wiki_csv = "datasets/cleaned-wiki.csv"
top_num_of_records = 1000



"""
Load and clean both datasets
"""
movies_df = pd.read_csv("datasets/movies_metadata.csv")
print(f"Size of csv df: {len(movies_df)}")
movies_df = movies_df[movies_df['budget'].apply(lambda x: str(x).isdigit())]
movies_df['budget'] = movies_df['budget'].astype(str).astype(int)

movies_df = movies_df.drop(movies_df[(movies_df['revenue'] == 0.0) | (movies_df['budget'] == 0)].index)

movies_df['revenue_ratio'] = movies_df['revenue'].div(movies_df['budget'])
# print(movies_df['revenue_ratio'])


wiki_df = pd.read_csv("datasets/cleaned-wiki.csv")
wiki_df = wiki_df.drop_duplicates(subset=['title'], keep='first')
print(wiki_df)

"""
Do some joins to get a combined df, then make it pretty to send to sql
"""
merged_df = pd.merge(movies_df, wiki_df, on="title")

# sample checks..
# sample_movies = movies_df.loc[movies_df['title'] == 'Toy Story']
# sample_wiki = wiki_df.loc[wiki_df['title'] == 'Toy Story']
#
# sample_merge = merged_df.loc[merged_df['title'] == 'Toy Story']
# print(sample_movies, sample_wiki, sample_merge)


columns_to_drop = ['adult', 'belongs_to_collection', 'genres', 'homepage', 'id',
                   'imdb_id', 'original_language', 'original_title', 'overview',
                   'poster_path', 'production_countries',
                   'runtime', 'spoken_languages', 'status', 'tagline', 'video',
                   'vote_average', 'vote_count']

print(list(merged_df))
sql_df = merged_df.drop(columns=list(columns_to_drop))
sql_df = sql_df.sort_values(by=['revenue_ratio']).head(top_num_of_records)

print(sql_df)

print(list(sql_df))


engine = sqlalchemy.create_engine(f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}")
con = engine.connect()
table_name = 'top_movies'
con.execute(f"DROP TABLE IF EXISTS {table_name};")

sql_df.to_sql(table_name, con)
con.close()


merged_df = merged_df.drop(columns=columns_to_drop)
merged_df.to_csv("datasets/merged.csv", index=False)