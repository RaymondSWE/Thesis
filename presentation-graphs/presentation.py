from graphviz import Digraph

# Create a new directed graph
dot = Digraph(comment='Kubernetes Cluster')

# Add the load balancer
dot.node('LB', 'Load Balancer', shape='box', style='filled', color='lightblue')

# Add the master node
dot.node('M', 'Master Node', shape='ellipse', style='filled', color='lightgreen')

# Add the worker nodes
for i in range(1, 11):
    dot.node(f'W{i}', f'Worker Node {i}', shape='ellipse')

# Connect the load balancer to the master node
dot.edge('LB', 'M')

# Connect the master node to each worker node
for i in range(1, 11):
    dot.edge('M', f'W{i}')

# Render the graph to a file
dot.render('k8s_cluster', format='png', view=True)
