class Node:
    def __init__(self, name):
        self.name = name
        self.children = []
        self.parents = []
        self.auth = 1.0
        self.hub = 1.0

    def HITS_one_iter(graph):
        node_list = graph.nodes

        for node in node_list:
            node.update_auth()
        for node in node_list:
            node.update_hub()

        graph.normalize_auth_hub()

    def update_auth(self):
        self.auth = sum(node.hub for node in self.parents)
    def update_hub(self):
        self.hub = sum(node.auth for node in self.children)
 
    def normalize_auth_hub(self):
        auth_sum = sum(node.auth for node in self.nodes)
        hub_sum = sum(node.hub for node in self.nodes)

        for node in self.nodes:
            node.auth /= auth_sum
            node.hub /= hub_sum