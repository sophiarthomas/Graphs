import argparse
import os
import sys
import networkx as nx
import matplotlib.pyplot as plt
from scrapy.crawler import CrawlerRunner
import scrapy
from twisted.internet import reactor, defer
import threading 


crawled_graph = nx.DiGraph()
lock = threading.Lock() # manage concurrent access to the graph
visited = set()

class LinkSpider(scrapy.Spider):
  name = 'link_spider'
  custom_settings = {
    'LOG_ENABLED': False,
    'DOWNLOAD_DELAY': 2.0,
    'USER_AGENT': 'CECS427 PageRank Bot',
    'COOKIES_ENABLED': False,
    'ROBOTSTXT_OBEY':False,
    # 'REQUEST_FINGERPRINTER_IMPLEMENTATION': 'scrapy2',
  }
  def __init__(self, max_nodes=100, domain=None, start_urls=None, **kwargs):
    super().__init__(**kwargs)
    self.max_nodes = max_nodes
    self.allowed_domain = domain
    self.start_urls = start_urls or []

  def parse(self, response): 
    current_url = response.url
    with lock: 
      if current_url in visited or len(crawled_graph.nodes) >= self.max_nodes:
        return 
      visited.add(current_url)


    links = response.css('a::attr(href)').getall()
    filtered_links = [href for href in links if self.allowed_domain in href and href != current_url and '.html' in href]
    print(f"[INFO] Found {len(filtered_links)} links on {current_url}")
    for href in filtered_links: 
      with lock:
        if len(crawled_graph.nodes) >= self.max_nodes:
          return
        crawled_graph.add_edge(current_url, href)

      with lock:
        if href not in visited:
          yield scrapy.Request(href, callback=self.parse)


def run_crawler(crawler_file):
    print(f"[INFO] Running crawler with {crawler_file}")
    with open(crawler_file, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    max_nodes = int(lines[0])
    domain = lines[1]
    seeds = lines[2:]

    runner = CrawlerRunner()

    @defer.inlineCallbacks
    def crawl_all():
      tasks = []
      for seed in seeds: 
        print(f"[INFO] Crawling {seed}")
        task = runner.crawl(LinkSpider, max_nodes=max_nodes, domain=domain, start_urls=[seed])
        tasks.append(task)

      yield defer.DeferredList(tasks)
      reactor.stop()

    crawl_all()
    reactor.run()

    print(f"[DONE] Graph has {len(crawled_graph.nodes)} nodes and {len(crawled_graph.edges)} edges")
    return crawled_graph

def build_graph_from_gml(path):
  """
  descrip: read a .gml file and create a directed graph using NetworkX
  param: .gml file
  return: directed graph
  """
  return nx.read_gml(path, label='id')

def compute_pagerank(graph, max_nodes, tol=1.0e-6, alpha=0.85): 
  """
  descrip: compute the PageRank of a directed graph using NetworkX
  param: directed graph
  return: dictionary of nodes and their PageRank values
  """
  N = len(graph)
  if N == 0:
    return {}

  nodes = list(graph)
  M = {node: set(graph.predecessors(node)) for node in graph}
  out_degree = {node: len(list(graph.successors(node))) for node in graph}

  pr = dict.fromkeys(graph, 1.0 / N)

  for _ in range(max_nodes):
    prev_pr = pr.copy()
    for node in graph:
      rank_sum = sum(prev_pr[neigh] / out_degree[neigh] 
                     for neigh in M[node] if out_degree[neigh] != 0)
      pr[node] = (1 - alpha) / N + alpha * rank_sum

    # Check convergence
    err = sum(abs(pr[n] - prev_pr[n]) for n in graph)
    if err < N * tol:
        break

  return pr
  
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

def plot_graph(graph, label_attr='label'):
  print(f"[INFO] Ploting graph with {len(graph.nodes)} nodes and {len(graph.edges)} edges")
  plt.figure(figsize=(12, 8))
  pos = nx.spring_layout(graph, k=0.15, iterations=20)
  nx.draw_networkx_nodes(graph, pos, node_size=50, node_color='blue', alpha=0.6)
  nx.draw_networkx_edges(graph, pos, alpha=0.1)

  labels = {
    node: graph.nodes[node].get(label_attr, str(node))[:30]
    for node in graph.nodes()
  }

  nx.draw_networkx_labels(graph, pos, font_size=8, font_color='black', labels=labels)

  plt.title("Web Graph", fontsize=16)
  plt.axis('off')
  plt.tight_layout()
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
  
  plot_graph(graph)

  if args.loglogplot: 
    print("[INFO] Generating log-log plot...") 
    plot_loglog(graph) 

  if args.pagerank_values: 
    print("[INFO] Computing PageRank...") 
    pr = compute_pagerank(graph, max_nodes=graph.number_of_nodes())
    with open(args.pagerank_values, 'w') as f: 
      for node, rank in sorted(pr.items(), key=lambda x: -x[1]): 
        f.write(f"{node} {rank}\n")

if __name__ == "__main__": 
  main() 
        

    

  
