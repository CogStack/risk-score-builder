#directed graph container

from collections import defaultdict

class Directed(object):
	"""A basic container around a collections.defaultdict which can traverse
	the graph (returns a set of nodes) and convert to a list of edges (returns
	list of lists))
	"""
	def __init__(self):
		self.edges = defaultdict(set)

	def add(self, source, target):
		self.edges[source].add(target)

	def count(self):
		c = 0
		for a in self.edges:
			c += len(self.edges[a])
		return c
		
	def list(self):
		result = []
		for a in self.edges:
			for b in self.edges[a]:
				result.append([a,b])
		return result
	
	def traverse(self, start, depth=0):
		if start not in self.edges:
			return []
		elif depth == 0:
			return [start]
		else:
			if depth == -1:
				#for unlimited depth, set max to a depth larger than max
				#possible in HPO
				depth = 10000
			seen = set()
			todo = set()
			todo.add(start)
			seen.add(start)
			for i in range(depth):
				child_nodes = set()
				for p in todo:
					child_nodes.update(self.edges[p])
					seen.update(self.edges[p])
				todo = child_nodes
				if len(todo) == 0:
					break
			return seen

if __name__ == "__main__":
	ed = Directed()
	ed.add('a','b')
	ed.add('b','c')
	ed.add('a','c')
	ed.add('b','d')
	print ed.traverse('a',0)
	print ed.traverse('a',1)
	print ed.traverse('a',100)
