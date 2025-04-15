import argparse
import os
import sys
import networkx as nx
import matplotlib.pyplot as plt
import requests
from urllib.parse import urljoin, urlparse
from urllib.request import urlopen
import time
# import scrapy
from bs4 import BeautifulSoup
# from  utils.graph_utils import build_graph_from_gml, compute_pagerank, plot_loglog
# from crawler.my_crawler import run_crawler

"""
Reads or creates a graph by crawling the internet starting with web addresses in crawler.txt

python ./page_rank.py --crawler crawler.txt --loglogplot --crawler_graph out_graph.gml  --pagerank_values node_rank.txt

Generate directed graph using crawling and parameters in the .txt, performs page rank algorithm in create graph
Plots LogLog plot, writes resulting diagraph in out_graph.gml and writes the page rank of all the nodes in node_rank.txt
"""

def extract_links(url, domain):
  try: 
    response = requests.get(url, timeout=2) # request.Response Object 
    soup = BeautifulSoup(response.text, 'html.parser)') # response.text returns content of response in unicode 
    
    links = set()
    for tag in soup.find_all('a', href=True): 
      link = urljoin(url, tag['href'])
      # if valid_url(link, domain): 
      links.add(link.split('#')[0]) # ignore fragments
    return list(links)
  except: 
    return []

def run_crawler(crawler_file): 
  """
  descrip: basic `Scrapy` crawling system using requests + BeautifulSoup
  param: .txt file (n: int, domain: string, webpage_1: string...) 
  return: generate a .gml directed graph using crawling 
  """
  with open(crawler_file, 'r') as f: 
    url = [line.strip() for line in f if line.strip()]

  max_nodes = int(url[0])
  domain = url[1]
  seeds = url[2:]

  graph = nx.DiGraph()
  visited = set() # no duplicates  
  queue = list(seeds) 

  while queue and len(graph.nodes) < max_nodes: 
    print(f'[CREATE] DiGraph')
    current = queue.pop(0)
    visited.add(current)

    links = extract_links(current, domain)
    print(links)

    for link in links: 
      graph.add_edge(current, link)
      if link not in visited and link not in queue and len(graph.nodes) < max_nodes: 
        queue.append(link)
    time.sleep(1)
  return graph 

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
  pass


def main(): 
  parser = argparse.ArgumentParser(description="Web Crawler and PageRank") 

  parser.add_argument('--crawler', help='Input crawler.txt file')
  parser.add_argument('--input', help='Input GML file') 
  parser.add_argument('--loglogplot', action='store_true', help='Generate log-log plot')
  parser.add_argument('--crawler_graph', help='Output GML file for crawled graph')
  parser.add_argument('--pagerank_values', help='Output text file for PageRank values')

  args = parser.parse_args()

  if args.crawler: 
    print("[INFO] Crawling websites...")
    graph = run_crawler(args.crawler) 
  #   if args.crawler_graph: 
  #     nx.write_gml(graph, args.crawler_graph) 
  # elif args.input: 
  #   if not os.path.exists(args.input): 
  #     sys.exit(f"[ERROR] Input file {args.input} does not exist.") 
  #     graph = build_graph_from_gml(args.input)
  #   else: 
  #     sys.exit("[ERROR] You must specify either --crawler or --input")
      
  # if args.loglogplot: 
  #   print("[INFO] Generating log-log plot...") 
  #   plot_loglog(graph) 

  # if args.pagerank_values: 
  #   print("[INFO] Computing PageRank...") 
  #   pr = compute_pagerank(graph)
  #   with open(args.pagerank_values, 'w') as f: 
  #     for node, rank in sorted(pr.items(), key=lambda x: -x[1]): 
  #       f.write(f"{node} {rank}\n")

if __name__ == "__main__": 
  main() 
        

    

  
