import argparse
import os
import sys
from  utils.graph_utils import build_graph_from_gml, compute_pagerank, plot_loglog
# from crawler.my_crawler import run_crawler

"""
Reads or creates a graph by crawling the internet starting with web addresses in crawler.txt

python ./page_rank.py --crawler crawler.txt --loglogplot --crawler_graph out_graph.gml  --pagerank_values node_rank.txt

Generate directed graph using crawling and parameters in the .txt, performs page rank algorithm in create graph
Plots LogLog plot, writes resulting diagraph in out_graph.gml and writes the page rank of all the nodes in node_rank.txt
"""

def run_crawler(crawler_file): 
  """
  descrip: basic `Scrapy` crawling system using requests + BeautifulSoup
  param: .txt file (n: int, domain: string, webpage_1: string...) 
  return: generate a .gml directed graph using crawling 
  """
  pass 

def main(): 
  parser = argparse.ArgumentParser(description="Web Crawler and PageRank") 

  parser.add_argument('--crawler', help='Input crawler.txt file')
  parser.add_argument('--input', help="Input GML file') 
  parser.add_argument('--loglogplot', action='store_true', help='Generate log-log plot')
  parser.add_argument('--crawler_graph', help='Output GML file for crawled graph')
  parser.add_argument('--pagerank_values', help='Output text file for PageRank values')

  parser.parse_args()

  if args.crawler: 
    print("[INFO] Crawling websites...")
    graph = run_crawler(args.crawler) 
    if args.crawler_graph: 
      nx.write_gml(graph, args.crawler_graph) 
  elif args.input: 
    if not os.path.exists(args.input): 
      sys.exit(f"[ERROR] Input file {args.input} does not exist.") 
    graph = build_graph_from_gml(args.input)
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
        

    

  
