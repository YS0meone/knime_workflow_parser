from collections import deque
from typing import Any


class NodeRetriever():
    """
    The main functionality of NodeRetriever is to find a node given a path to it
    (Node here means a name inside the dictionary) Currently NodeRetriever is 
    only used to retrieve operator property values.
    """

    def __init__(self, tree: dict):
        self.tree = tree

    def find_node(self, nodes_path: list[str]) -> str | None:
        """
            Returns the node value in the self.settings
        """
        # the element inside deque is guaranteed to be dictionary
        # return None when the path is not correct
        def helper(node: dict, target_node_key: str) -> dict | str | None:
            q = deque([node])
            while q:
                cur = q.popleft()
                for key in cur.keys():
                    if key == target_node_key:
                        return cur[key]
                    else:
                        if isinstance(cur[key], dict):
                            q.append(cur[key])
            return None
        cur_node = self.tree
        for next_node_key in nodes_path:
            if not isinstance(cur_node, dict):
                return None
            cur_node = helper(cur_node, next_node_key)
        return cur_node

    def str2path(self, str_path: str) -> list[str]:
        # convert a string path into a list format
        return [x for x in str_path.split('/') if x and x != "..."]

    def retrieve_nodes(self, nodes: list | dict, action: str) -> Any:
        # retrieve node takes into consideration that the mapping between nodes might be one2one one2many or one2zero. The path would variable stores all of the nodes to the desired value
        action = action.replace("$", "")
        try:
            if isinstance(nodes, dict):
                for var, path in nodes.items():
                    # store all needed local variables
                    ret = self.find_node(self.str2path(path))
                    if ret is None:
                        raise ValueError("The node path in the mapping configuration is wrong!")
                    locals()[var] = ret
            elif isinstance(nodes, list):
                for i in range(len(nodes)):
                    if not isinstance(nodes[i], dict):
                        raise TypeError("Nodes should be a list of dict or dict!")
                    for var, path in nodes[i].items():
                        ret = self.find_node(self.str2path(path))
                        if ret is None:
                            raise ValueError("The node path in the mapping configuration is wrong!")
                        nodes[i][var] = ret
            else:
                raise TypeError("Nodes should be a list of dict or dict!")
        except TypeError as t:
            print(f"TypeError: {t}")
        except ValueError as v:
            print(f"ValueError: {v}")
        try:
            exec(action, None, locals())
        except Exception as e:
            print(f"Error occurred while executing the user-defined python code: {e}")
        if "ret" in locals():
            return locals()["ret"]
        else:
            raise ValueError("Action does not contain a return value")
