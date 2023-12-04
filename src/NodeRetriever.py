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

    def retrieve_node(self, paths: list[list[str]], action: str, action_config: dict) -> Any:
        # retrieve node takes into consideration that the mapping between nodes might be one2one one2many or one2zero. The path would variable stores all of the paths to the desired value
        target_values = []
        for path in paths:
            target_values.append(self.find_node(path))
        # need to guard
        if action == "type_casting":
            # in case we didn't find the node
            if len(target_values) != 1:
                raise ValueError(
                    "Incorrect number of target values for type casting!")
            if target_values == "COUNT":
                pprint(self.tree)
            return self.type_cast(target_values[0], action_config["type"])
        elif action == "conditional_type_casting":
            if len(target_values) != 1:
                raise ValueError(
                    "Incorrect number of target values for conditional type casting!")
            if self.find_node(action_config["condition"]["flag"]) == action_config["condition"]["value"]:
                return self.type_cast(target_values[0], action_config["type"])
        elif action == "one_to_one":
            if len(target_values) != 1:
                raise ValueError(
                    "Incorrect number of target values for one to one!")
            return self.one_to_one(target_values[0], action_config["map"])

        elif action == "sequential_retrieve":
            ret = []
            for i in range(len(target_values)):
                if action_config["value_mappings"][i][0] == "type_casting":
                    ret.append(self.type_cast(
                        target_values[i], action_config["value_mappings"][i][1]))
                elif action_config["value_mappings"][i][0] == "one_to_one":
                    ret.append(self.one_to_one(
                        target_values[i], action_config["value_mappings"][i][1]))
            return ret
        elif action == "recursive_retrieve":
            ret = {}
            for key, config in action_config["group"].items():
                ret[key] = self.retrieve_node(
                    config["paths"], config["action"], config["action_config"])
            return [ret]
