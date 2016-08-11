# inspired by https://graph-tool.skewed.de/performance
# pgp.xml from:
# Richters O, Peixoto TP (2011) Trust Transitivity in Social Networks. PLoS ONE 6(4): e18384.
# doi 10.1371/journal.pone.0018384

import benchutil
benchutil.add_external_path("networkx-1.11")
benchutil.add_external_path("decorator-4.0.10/src")

import networkx

def func():
    g = networkx.read_graphml(os.path.join(thisdir, "pgp.xml"))
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
