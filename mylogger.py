#!/usr/bin/env python

import sys
import logging
import random

import networkx as nx

# core functions to generate/combine/consume stuff
# It's tempting to combine these all to a generic class, but intentially
# keeping them separate to make it easier to play with the logger
def mine_iron():
    logging.info("mining iron")
    return 1


def chop_tree():
    logging.info("chopping down a tree")
    return 1


def kill_cow():
    logging.info("slaughtering a cow")
    return 1


def pack_steak(cow):
    logging.info("packaging a steak")
    return 1


def make_nails(iron):
    logging.info("making nails")
    return 1


def mill_lumber(tree):
    logging.info("milling lumber")
    return 1


def build_table(lumber, nails):
    logging.info("building a table")
    return 1


def have_meal(table, steak):
    logging.info("having a meal")
    return None


#
# end core functions


class Economy:
    """
    Define a dependency graph that reflects the core functions above (feels
    like there's probably a more clever/strucured/automatic way to do this).
    """

    def __init__(self, *, write_dot=None):
        G = nx.DiGraph()

        # Nodes contain a reference to their core callback handler
        G.add_nodes_from(
            [
                ("iron", {"handler": mine_iron}),
                ("tree", {"handler": chop_tree}),
                ("cow", {"handler": kill_cow}),
                ("steak", {"handler": pack_steak}),
                ("nails", {"handler": make_nails}),
                ("lumber", {"handler": mill_lumber}),
                ("table", {"handler": build_table}),
                ("meal", {"handler": have_meal}),
            ]
        )

        # Connect them up
        G.add_edge("cow", "steak")
        G.add_edge("iron", "nails")
        G.add_edge("tree", "lumber")
        G.add_edge("lumber", "table")
        G.add_edge("nails", "table")
        G.add_edge("table", "meal")
        G.add_edge("steak", "meal")

        # dump it to a graphviz file to visualize
        if write_dot is not None:
            nx.drawing.nx_pydot.write_dot(G, write_dot)

        self.G = G

    def make(self, item):
        """
        Make an item (including its dependencies)
        """
        logging.debug(f"making a '%s'", item)

        # TODO not sure ancestors guaranteed a good ordering, might need to
        # sort. Also I'm pretty sure there are tidier ways to store/access info
        # in a DiGraph than what we're doing here
        upstream = self.G.subgraph(nx.ancestors(self.G, item))
        for node in nx.topological_sort(upstream):
            logging.debug("satisfying upstream requirement (%s)", node)

            # Get our handler callback
            handler = self.G.nodes(data=True)[node]["handler"]

            # Get prereqs. Could add an inventory check here, either grab a
            # preexisting instance, or call the handler to produce
            parents = list(self.G.predecessors(node))
            materials = {n: 1 for n in parents}
            handler(**materials)

        return 1


class FuncNameWhitelistFilter(logging.Filter):
    """
    logging Filter to whitelist events in specific named functions
    """

    def __init__(self, whitelist):
        self.whitelist = whitelist

    def filter(self, record):
        return record.funcName in self.whitelist


def main(argv):

    # initialize the logger
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)-15s %(name)-5s %(levelname)-8s %(message)s",
    )

    # Add a filter for events from specific function
    logging.getLogger().addFilter(
        FuncNameWhitelistFilter([
            "make",
            "mine_iron",
            "kill_cow"
        ])
    )

    # Add a cusom filter, we want a way to blacklist/whitelist functions
    G = Economy(write_dot="/tmp/blamo.dot")
    meal = G.make("meal")

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
