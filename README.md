# True Film 

### Approach

I felt this was more of a data science exercise, rather than a data engineering task. 
My solution meets the requirements but I also went a bit further and setup a logstash pipeline
to ingest some of the data I was generating so it could be visualised in Kibana so it could  be used for other
purposes too.

The scripts I created would be akin to pipelines in a more sophisticated environment.
My scripts proxy for orchestratable tasks in Airflow (or your favourite orchestrator), Spark jobs or even 
standalone microservices. The goal would still be to filter the information, keep
whats needed and reuse the useful information to be efficient.

Technologies used: 
- Python3 with Pandas
    - Pandas is a great data science library and can handle efficiently read large datasets
    - Really easy to build things with Python3, handy when you have a full time job
    - Python3 has easy to use libraries to connect with Postgres or other frameworks should it be required. 
- Postgres (required) via Docker
    - Simple and easy to spin up a postgres database for this task
- ELK Stack for further data exploration
    - See `ELK and some other crazy ideas` section

The initial datasets were large and full of extra information which I did not want to repeatedly 
process. The wikipedia dataset was particularly large (6gb uncompressed), so I created a script that extracted all
the useful information and saved it as a CSV file (1gb). Having to only run the script once and using the smaller
CSV file greatly helped development speed and is more efficient.

The movies csv was fairly small, so I combined it with the simplified wiki csv in one another 
script using Pandas. Both scripts go into detail as to what I did, but it's not very 
complicated, essentially just manipulating the dataframes until it met the requirements.

Finally, I exported it to Postgres and also saved it as a csv. 

As with any sort of messy data, there is clean up involved and as part of that, you have to decide
what data to lose. This becomes relevant when merging the two datasets. The wikipedia dump has multiple 
pages for certain films. For example, `Toy Story` is a movie, but it also have a specific 
page for the physical toys kids buy or the video game. This also occurs when the movie name is a 
common name or has other notable uses e.g `Terminator` has lots of [wikipedia articles not related
to the film](https://en.wikipedia.org/wiki/Terminator). 

My answer to this was to use the shortest link, because the shortest link will either point to the
correct movie page IF there is only ONE wikipedia article and therefore it must be about the movie. Or in the cases like `Toy Story` and `Terminator`, it will 
point to a wikipedia disambiguation page, after which the user is free to find the correct article. 

### Better to scrape 

I would of preferred to not parse the wikipedia dump at all. Instead, once
we have a list of top 1000 movies with the revenue/budget ratio, we could instead 
have a pipeline which enriches these 1000 records by scrapping wikipedia. You could
build a sophisticated pipeline that can work out more accurately which is the correct 
wikipedia link, but more importantly the amount of computation (1000 requests vs the 6gb 
wikipedia dump) is massively reduced. 

There is some network cost associated with scrapping but these are manageable for 1000
requests, especially as movie data does not change that frequently.

#### ELK and some other crazy ideas

I was able to answer the question with just Pandas and manipulating dataframes with two
scripts. However, at the end I had a really interesting dataset (movies with data with 
some additional wikipedia information) and it seemed a bit of a waste to stop there. 

Data engineering is all about enabling access to the enriched data we create. So I exported
the merged Pandas dataframe (before filtering for 1000 top records) as a CSV. I setup a 
logstash pipeline that dumps this CSV data into Elasticsearch which can then be visualised
in kibana.. this can now answer all sorts of questions!
 
And you don't have to be Pandas expert or manipulate any DataFrames, Kibana gives you so 
much power with searching, creating visualisations.. well you know :)

To be honest -- if the task wasn't all about putting data into postgres, I would just use
Logstash! I actually created a logstash pipeline see (`logstash/conf/wikipedia-pipeline.conf`) that converts the uncompressed XML
dump into elasticsearch data. 

The logstash file input plugins are smart and can be configured to watch for changes to file
so if the initital datasets change, the pipeline is robust enough to cope and update Elastic.

Once this data is in Elasticsearch, it makes easier to enrich the movies data that is ingested, possibly even with a [proccessing pipeline](https://www.elastic.co/guide/en/elasticsearch/reference/master/ingest-processors.html)
You could even have dedicated ingest-nodes setup just to optimise this part of the ingestion if you're expecting lots more data coming in frequently.

Elastic is of course a great choice for searches since we have lots of text here. Once indexed,
searching capability is great and lots of great analytics are possible with Kibana.


### Setup & run 

- Ensure Docker is installed with docker-compose
- Create a virtualenv with python3 e.g `virtualenv env -p $(which python3)`
- Install dependencies e.g `pip install -r requirements.txt`
- Save the datasets to the `/datasets` folder named:
    - `movies_metadata.csv` for the movies csv
    - `enwiki-latest-abstract.xml.gz` for the wiki xml gz file
For the bare requirements of this task, the ELK stack is not needed, so feel free
to comment out those services. 
- Create a `postgres.env` file in the root directory with the values:
```
POSTGRES_PASSWORD=<yourpassword>
POSTGRES_USER=user
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=database
```
- `docker-compose up -d` - this atleast will run postgres on localhost:5432
-  Run the following commands to export env variables into the virtual env. 
```bash
set -o allexport
source postgres.env
set +o allexport
```
- First run `python3 simplify_wiki_xml.py` from the root of the folder
- Check that `datasets/cleaned-wiki.csv` has been created
- Now run `python3 rank_by_revenue_ratio.py`
- Check that `datasets/merged.csv` has been created and use your either a client or psql cli 
method to check postgres (`SELECT * FROM top_movies;`)




