# inspired by https://graph-tool.skewed.de/performance
# pgp.xml from:
# Richters O, Peixoto TP (2011) Trust Transitivity in Social Networks. PLoS ONE 6(4): e18384.
# doi 10.1371/journal.pone.0018384

import sys
import os

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
networkxdir = os.path.join(parentdir, "external", "networkx-1.11")
sys.path.append(networkxdir)
decoratordir = os.path.join(parentdir, "external", "decorator-4.0.10", "src")
sys.path.append(decoratordir)

import benchutil
import networkx

def func():
    g = networkx.read_graphml("pgp.xml")
    networkx.shortest_path_length(g, 'n0')
    networkx.pagerank(g, alpha=0.85, tol=1e-3, max_iter=10000000)
    networkx.core.core_number(g)
    u = g.to_undirected()

    networkx.minimum_spanning_tree(u)

if __name__ == '__main__':
    benchutil.main(func)

#print "betweenness_centrality"
#networkx.betweenness_centrality(g)
#
#print "edge_betweenness_centrality"
#networkx.edge_betweenness_centrality(g)
