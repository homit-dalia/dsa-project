import networkx as nx
import itertools
import sys
import matplotlib.pyplot as plt


def transform_graph(G, budget):
    
    # Identify isolated vertices
    isolated_vertices = [n for n in G.nodes() if G.degree(n) == 0]
    
    # Add budget for isolated vertices
    adjusted_budget = budget + len(isolated_vertices)
    
    # Create a copy of the graph to work with
    graph = G.copy()
    
    # Add dummy nodes for each edge
    for u, v in list(graph.edges()):
        dummy_node = f"dummy_{u}_{v}"
        graph.add_node(dummy_node)
        graph.add_edge(u, dummy_node)
        graph.add_edge(v, dummy_node)
    
    return graph, adjusted_budget, isolated_vertices

# Helper function to check if a set is a dominating set
def is_dominating_set(G, dominating_set):
    uncovered_nodes = set()
    
    # Check all nodes
    for node in G.nodes():
        # If node is not in dominating set, check if it's adjacent to any node in the set
        if node not in dominating_set:
            if not any(G.has_edge(node, dom_node) for dom_node in dominating_set):
                uncovered_nodes.add(node)
    
    if uncovered_nodes:
        print("Uncovered nodes:", uncovered_nodes)
        return False
    print("All nodes dominated.")
    return True

def find_minimum_dominating_set(G, budget):
    
    # Brute force search for dominating set
    nodes = list(G.nodes())
    for k in range(budget + 1):
        for candidate_set in itertools.combinations(nodes, k):
            # Check if candidate set dominates the entire graph
            print("\nTrying set (dominating):", set(candidate_set))
            if is_dominating_set(G, set(candidate_set)):
                print("Found dominating set:", set(candidate_set))
                return len(set(candidate_set)), set(candidate_set)
    
    return None, None

# Helper function to check if a set is a vertex cover
def is_vertex_cover(G, vertex_cover):
    uncovered_edges = []
    
    # Check all edges
    for u, v in G.edges():
        # If neither endpoint of the edge is in the vertex cover, it's not a valid cover
        if u not in vertex_cover and v not in vertex_cover:
            uncovered_edges.append((u, v))
    
    if uncovered_edges:
        print("Uncovered edges:", uncovered_edges)
        return False
    print("All edges covered.")
    return True

def exhaustive_vertex_cover_search(G, budget):
    
    # Get all nodes
    nodes = list(G.nodes())
    
    # Try all possible combinations of nodes
    for k in range(budget + 1):
        for candidate_set in itertools.combinations(nodes, k):
            # Check if this set is a vertex cover
            print("\nTrying vertex set:", set(candidate_set))
            if is_vertex_cover(G, set(candidate_set)):
                print("Found vertex cover:", set(candidate_set))
                return set(candidate_set)
    
    return None

def visualize_graph(G, title, filename, highlight_nodes=None):
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, seed=42)  # consistent layout
    
    # Draw all nodes
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=300)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos)
    
    # Highlight specific nodes if provided
    if highlight_nodes:
        nx.draw_networkx_nodes(G, pos, 
                                nodelist=list(highlight_nodes), 
                                node_color='red', 
                                node_size=400)
    
    # Draw labels
    nx.draw_networkx_labels(G, pos)
    
    plt.title(title)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()  # Close the plot to free up memory

def main():
    
    budget = int(input("Enter budget: "))
    
    # Redirect stdout to output.txt
    original_stdout = sys.stdout
    with open('output.txt', 'w') as output_file:
        sys.stdout = output_file
        
        input_file = "input.csv"
        with open(input_file, 'r') as file:
            lines = file.readlines()
            
            # Separate edges and isolated vertices
            edges = []
            isolated_vertices = set()
            
            for line in lines:
                nodes = list(map(int, line.strip().split(',')))
                if len(nodes) == 2:
                    edges.append(tuple(nodes))  # Add as an edge
                elif len(nodes) == 1:
                    isolated_vertices.add(nodes[0])  # Add as an isolated vertex

        # Create the graph
        G = nx.Graph()
        G.add_edges_from(edges)
        G.add_nodes_from(isolated_vertices)  # Add isolated vertices

        # Visualize original graph
        visualize_graph(G, "Original Graph", "original.png")

        # Problem 1 - Transform the graph
        # We overwrite the isolated vertices variable to store the isolated vertices obtained from the transformation
        transformed_graph, new_budget, isolated_vertices = transform_graph(G, budget)
        
        # Visualize transformed graph
        visualize_graph(transformed_graph, "Transformed Graph", "transform.png")
        
        print("Original Graph:")
        print("Edges:", list(G.edges()))
        print("Isolated vertices:", list(isolated_vertices))
        print("Original Budget:", budget)
        
        print("\nTransformed Graph:")
        print("Edges (including dummy nodes):", list(transformed_graph.edges()))
        print("Total Nodes:", list(transformed_graph.nodes()))
        print("New Budget:", new_budget)

        # Find minimum dominating set
        resulting_size, candidate_set = find_minimum_dominating_set(transformed_graph, new_budget)
        
        # Visualize Dominating Set if possible
        if resulting_size is not None:
            # Remove isolated vertices from the result
            non_isolated_result = resulting_size - len(set(isolated_vertices))
            non_isolated_result_vertex = set(candidate_set) - set(isolated_vertices)

            visualize_graph(transformed_graph, "Dominating Set in Transformed Graph", 
                            "ds.png", highlight_nodes=candidate_set)

            if non_isolated_result <= budget:
                print("\nIt is possible to find a Vertex Cover with original budget.")
                print("Vertex Cover of size", non_isolated_result, "is:", non_isolated_result_vertex)
            else:
                print("This line should not be printed.")
                print(f"\nIt is not possible to find a Vertex Cover with original budget.")
                print(f"However, it is possible to find a Vertex Cover with budget {non_isolated_result}.")
                print("Minimum Vertex Cover of size", non_isolated_result, "is:", non_isolated_result_vertex)

        # Exhaustive search to confirm no solution exists
        print("\nPerforming exhaustive search to confirm if a solution or no solution exists...")
        exhaustive_result = exhaustive_vertex_cover_search(G, budget)
        
        # Visualize Vertex Cover if found
        if exhaustive_result is not None:
            visualize_graph(G, "Vertex Cover in Original Graph", 
                            "vc.png", highlight_nodes=exhaustive_result)
            print("A Vertex Cover was found during exhaustive search.")
            print("Vertex Cover:", exhaustive_result)
        else:
            print(f"Confirmed: No Vertex Cover exists for the graph with budget {budget}.")
            print("Exhaustive search checked all possible combinations.")
        
        # Restore stdout
        sys.stdout = original_stdout
        
if __name__ == "__main__":
    main()