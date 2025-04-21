import argparse
import os
import sys
import networkx as nx
import matplotlib.pyplot as plt
from scrapy.crawler import CrawlerProcess
import scrapy

crawled_graph = nx.DiGraph()

class LinkSpider(scrapy.Spider):
  name = 'link_spider'
  custom_settings = {
    # 'FEEDS': {
    #   'output.gml': {
    #     'format': 'gml',
    #     'overwrite': True
    #   }
    # },
    'LOG_ENABLED': False,
    'DoWNLOAD_DELAY': 1.0,
    'USER_AGENT': 'CECS427 PageRank Bot',
  }
  def __init__(self, max_nodes=101, domain=None, start_urls=None, **kwargs):
    super().__init__(**kwargs)
    self.max_nodes = max_nodes
    self.allowed_domain = domain
    self.start_urls = start_urls or []
    self.visited = set()

  def parse(self, response): 
    current_url = response.url
    if current_url in self.visited or len(crawled_graph.nodes) >= self.max_nodes:
      return 
    self.visited.add(current_url)


    links = response.css('cite a::attr(href)').getall()
    print(f"[INFO] Found {len(links)} links on {current_url}")
    for href in links: 
      if self.allowed_domain in href and href != current_url:
        crawled_graph.add_edge(current_url, href)
        if href not in self.visited and len(crawled_graph.nodes) < self.max_nodes:
          yield scrapy.Request(href, callback=self.parse)


def run_crawler(crawler_file):
    with open(crawler_file, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    max_nodes = int(lines[0])
    domain = lines[1]
    seeds = lines[2:]

    process = CrawlerProcess()
    process.crawl(LinkSpider, max_nodes=max_nodes, domain=domain, start_urls=seeds)
    process.start()
    print(f'graph:  {crawled_graph}')
    return crawled_graph


def build_graph_from_gml(path):
  """
  descrip: read a .gml file and create a directed graph using NetworkX
  param: .gml file
  return: directed graph
  """
  return nx.read_gml(path, label='id')

def compute_pagerank(graph, alpha=0.85): 
  """
  descrip: compute the PageRank of a directed graph using NetworkX
  param: directed graph
  return: dictionary of nodes and their PageRank values
  """
  return nx.pagerank(graph, alpha=alpha)
  

def plot_loglog(graph):
  """
  descrip: plot the log-log plot of the degree distribution of a directed graph using Matplotlib
  param: directed graph
  return: log-log plot
  """
  degrees = [deg for _, deg in graph.degree()]
  degree_counts = {}
  for d in degrees:
      degree_counts[d] = degree_counts.get(d, 0) + 1

  x = sorted(degree_counts.keys())
  y = [degree_counts[k] for k in x]

  plt.figure()
  plt.loglog(x, y, marker='o')
  plt.title("Log-Log Plot of Degree Distribution")
  plt.xlabel("Degree")
  plt.ylabel("Frequency")
  plt.grid(True)
  plt.show()


def main(): 
  parser = argparse.ArgumentParser(description="Web Crawler and PageRank") 

  parser.add_argument('--crawler', help='Input crawler.txt file')
  parser.add_argument('--input', help='Input GML file') 
  parser.add_argument('--loglogplot', action='store_true', help='Generate log-log plot')
  parser.add_argument('--crawler_graph', help='Output GML file for crawled graph')
  parser.add_argument('--pagerank_values', help='Output text file for PageRank values')

  args = parser.parse_args()
  graph = nx.DiGraph()

  if args.crawler: 
    print("[INFO] Crawling websites...")
    graph = run_crawler(args.crawler) 
    
    if args.crawler_graph: 
      nx.write_gml(graph, args.crawler_graph) 
  elif args.input: 
    if not os.path.exists(args.input): 
      sys.exit(f"[ERROR] Input file {args.input} does not exist.") 
    else: graph = build_graph_from_gml(args.input)
  else: 
    sys.exit("[ERROR] You must specify either --crawler or --input")
      
  if args.loglogplot: 
    print("[INFO] Generating log-log plot...") 
    plot_loglog(graph) 

  if args.pagerank_values: 
    print("[INFO] Computing PageRank...") 
    pr = compute_pagerank(graph)
    with open(args.pagerank_values, 'w') as f: 
      for node, rank in sorted(pr.items(), key=lambda x: -x[1]): 
        f.write(f"{node} {rank}\n")

if __name__ == "__main__": 
  main() 
        

    

  
