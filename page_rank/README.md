# PageRank Web Crawler & Graph Analyzer

Use `scrapy` to collect page relationship informatoin and build a page rank dataset \

Crawls webpages starting from a list of seed URLs, builds a directed graph of the links, computes PageRank, and visualizes the graph’s degree distribution.

# Usage
1. Install scrapy 
```
pip install scrapy 

```
2. Create `crawler.txt` file with the format: 
```
max_nodes 
domain
url
url
...
url

```
3.  Run command inside `page_rank\`
```
python ./page_rank.py --crawler crawler.txt --crawler_graph out_graph.gml --pagerank_values node_rank.txt --loglogplot
```
## Features
- Web Crawling:
The crawler starts from a set of seed URLs provided in crawler.txt and collects outgoing links that belong to the same domain.

- Graph Construction:
The directed graph is built using NetworkX, where each node is a webpage and each edge represents a hyperlink from one page to another.

- PageRank Computation:
PageRank scores are computed using NetworkX's implementation.

- Log-Log Plot (Optional):
Generates a log-log plot of the degree distribution.

## Commands 
To use this script the following command and additional options are available: \
`python ./page_rank.py` \
\
  `--crawler crawler.txt` - crawls the .html pages specified in crawler.txt and generates a .gml file of the resulting crawl\
  `--input crawled.gml` - Specifies the directed graph  (graph.gml) to be used in the page rank algorithm and Loglog plot if the crawling is not provided \
  `--crawler_graph out_graph.gml` - Saves the processed graph to out_graph.gml. \
  `--pagerank_values node_rank.txt` - computes pagerank of the graph and saves the values to node_rank.txt\
  `--loglogplot` - Generates a log-log plot of the degree distribution of the graph

 

## Input Crawler File Format
`crawler.txt`
```
100
example.com
https://example.com
https://example.com/page2
```

  
