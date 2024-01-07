import ast
from collections import deque
from typing import Any
from copy import deepcopy
from pprint import pprint


class NodeRetriever():
    """
    The main functionality of NodeRetriever is to find a node given a path to it (Node here means a name inside the dictionary) 
    """

    def __init__(self, tree: dict):
        self.tree = tree

    def find_node(self, stops: list[str]) -> str | None:
        """
            Returns the node value in the self.settings
        """
        # we check before we put the element inside the deque
        # the element inside deque is guaranteed to be dictionary
        # need to use exception to check for correct path
        def helper(start: dict, stop: str) -> dict | str | None:
            q = deque([start])
            while q:
                cur = q.popleft()
                for key in cur.keys():
                    if key == stop:
                        return cur[key]
                    else:
                        if isinstance(cur[key], dict):
                            q.append(cur[key])
            return None
        start = deepcopy(self.tree)
        for stop in stops:
            if not isinstance(start, dict):
                return None
            start = helper(start, stop)
        return start

    def type_cast(self, target_value, type):
        type_cast = __builtins__[type]
        return type_cast(target_value)

    def one_to_one(self, target_value, mapping):
        if target_value in mapping:
            return mapping[target_value]
        else:
            return mapping["_DEFAULT"]
    
    def str2path(self, str_path: str) -> list[str]:
        # convert a string path into a list format
        return [x for x in str_path.split('/') if x and x != "..."]

    def retrieve_node(self, nodes: list | dict, action: str) -> Any:
        # retrieve node takes into consideration that the mapping between nodes might be one2one one2many or one2zero. The path would variable stores all of the nodes to the desired value
        action = action.replace("$", "")
        if isinstance(nodes, dict):
            for var, path in nodes.items():
                # store all needed local variables
                locals()[var] = self.find_node(self.str2path(path))
            # need to guard
            # TODO: make the action to be a string of python code
            # TODO: Need to guard agains malicious lambda function
        if isinstance(nodes, list):
            for i in range(len(nodes)):
                for var, path in nodes[i].items():
                    nodes[i][var] = self.find_node(self.str2path(path))
                    
        exec(action, None, locals())
        if "ret" in locals():
            return locals()["ret"]
        else:
            raise ValueError("Action does not contain a return value")

