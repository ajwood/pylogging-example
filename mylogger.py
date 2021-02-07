#!/usr/bin/env python

import time
import sys
import logging
import random

from logging.handlers import TimedRotatingFileHandler

import networkx as nx

# core functions to generate/combine/consume stuff
# It's tempting to combine these all to a generic class, but intentially
# keeping them separate to make it easier to play with the logger
def mine_iron():
    logging.info("mining iron")
    logging.debug("pulling iron out of the ground")
    return 1


def chop_tree():
    logging.info("chopping down a tree")
    logging.debug("getting out an axe and swingin it")
    return 1


def kill_cow():
    logging.info("slaughtering a cow")
    logging.debug("eep")
    return 1


def pack_steak(cow):
    logging.info("packaging a steak")
    logging.debug("wrapping some plastic around the food")
    return 1


def make_nails(iron):
    logging.info("making nails")
    logging.debug("shaping the iron into nails, put them in a box")
    return 1


def mill_lumber(tree):
    logging.info("milling lumber")
    logging.debug("firing up the saw")
    return 1


def build_table(lumber, nails):
    logging.info("building a table")
    logging.debug("hammer hammer etc")
    return 1


def have_meal(table, steak):
    logging.info("having a meal")
    logging.debug("yum yum")
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
    fmt = "%(asctime)-15s %(name)-5s %(levelname)-8s %(message)s"
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Make the default stream handler at INFO level
    rh = logging.StreamHandler()
    rh.setLevel(logging.INFO)
    rh.setFormatter(logging.Formatter(fmt))
    root_logger.addHandler(rh)

    # Add a new handler for DEBUG messages from some specific functions Just
    # for the hell of it, route into a logfile, set to rotate ever 10 seconds
    debug_h = TimedRotatingFileHandler(
        "/tmp/toy-whatever.log",
        when='S',
        interval=10,
    )
    debug_h.setLevel(logging.DEBUG)
    debug_f = logging.Formatter("%(asctime)-15s %(name)-5s %(levelname)-8s[[cool cool cool]] %(message)s")
    debug_h.setFormatter(debug_f)

    # Add a filter for events from specific function
    debug_h.addFilter(
        FuncNameWhitelistFilter([
            "make",
            "mine_iron",
            #"kill_cow"
        ])
    )
    root_logger.addHandler(debug_h)

    # Add a cusom filter, we want a way to blacklist/whitelist functions
    G = Economy(write_dot="/tmp/blamo.dot")
    nodes = list(G.G.nodes())
    while True:
        G.make(random.choice(nodes))
        time.sleep(random.random())

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
