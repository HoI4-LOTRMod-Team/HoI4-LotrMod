def get_connected_network_ordered(start_node):
    """
    Returns a list of all nodes connected to start_node (including itself),
    ordered from the highest 'root' node down to the 'leaves'.
    """
    
    # --- PHASE 1: FIND THE ROOT ---
    # Traverse upstream via the single input to find the top-most node.
    
    current_node = start_node
    # We keep a visited set just for the upstream walk to detect immediate upstream cycles
    visited_upstream = {current_node} 
    
    while True:
        # Get the first (and only) input port
        input_ports = current_node.inputs()
        
        # Stop if node has no input ports defined
        if not input_ports:
            break
            
        # We assume the prompt constraint: "Nodes all have only one input"
        # We take the first input port (index 0)
        in_port = list(input_ports.values())[0]
        
        # Get connected ports
        connected_ports = in_port.connected_ports()
        
        # If nothing is connected, we found the root
        if not connected_ports:
            break
            
        # Get the parent node (assuming single connection logic)
        parent_node = connected_ports[0].node()
        
        # If we hit a cycle (parent is already in our path), stop here
        if parent_node in visited_upstream:
            break
            
        visited_upstream.add(parent_node)
        current_node = parent_node

    root_node = current_node

    # --- PHASE 2: COLLECT DOWNSTREAM (BFS) ---
    # Traverse downwards from the root to gather all nodes in order.
    
    ordered_nodes = []
    queue = [root_node]
    visited = {root_node} # Set to prevent processing same node twice (circular handling)

    while queue:
        node = queue.pop(0) # Pop from start (FIFO) for Breadth-First order
        ordered_nodes.append(node)
        
        # Iterate over all output ports of the current node
        for out_port in node.outputs().values():
            for connected_port in out_port.connected_ports():
                child_node = connected_port.node()
                
                if child_node not in visited:
                    visited.add(child_node)
                    queue.append(child_node)

    return ordered_nodes