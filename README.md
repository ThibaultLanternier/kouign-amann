# Kouign-Amann photo crawler

Local picture crawler responsible for indexing photo locally, hashing them for deduplication and sending thumbnails to the server

# Run the app

## Crawl for pictures

```
cd crawler
make init
python picture-crawler.py crawl
```

### Enable metrics

In order to have metrics formatted in InfluxDB format you need to make sure that the config.ini config file contains [crawler]metrics_output_path=/path/to/the/metrics

## Handle backup requests

```
cd crawler
make init
python picture-crawler.py backup
```
