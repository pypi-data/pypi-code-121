#!/usr/bin/env python3
import pop.hub


def start():
    hub = pop.hub.Hub()
    hub.pop.sub.add(dyne_name="tree", omit_class=False)
    hub.tree.init.doc_cli()
