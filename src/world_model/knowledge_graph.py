# World Model Layer - Knowledge Graph
# Creates a dynamic model of the world that the AI can reason about

import networkx as nx
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Any, Optional, Set
import json


class KnowledgeGraph:
    """Knowledge graph for the World Model Layer.
    
    This class is responsible for creating and maintaining a dynamic model of the world
    that the AI can reason about. It uses a graph structure to represent entities and
    their relationships.
    """
    
    def __init__(self):
        """Initialize the knowledge graph."""
        self.graph = nx.DiGraph()  # Directed graph for representing relationships
        self.entity_attributes = {}  # Dictionary to store entity attributes
    
    def add_entity(self, entity: str, attributes: Dict[str, Any] = None) -> None:
        """Add an entity to the knowledge graph.
        
        Args:
            entity: The name of the entity to add.
            attributes: Optional dictionary of attributes for the entity.
        """
        if attributes is None:
            attributes = {}
        
        # Add the entity as a node in the graph
        self.graph.add_node(entity)
        
        # Store the entity's attributes
        self.entity_attributes[entity] = attributes
    
    def add_relationship(self, subject: str, predicate: str, object_: str, attributes: Dict[str, Any] = None) -> None:
        """Add a relationship between two entities.
        
        Args:
            subject: The source entity.
            predicate: The type of relationship.
            object_: The target entity.
            attributes: Optional dictionary of attributes for the relationship.
        """
        if attributes is None:
            attributes = {}
        
        # Make sure both entities exist in the graph
        if subject not in self.graph:
            self.add_entity(subject)
        
        if object_ not in self.graph:
            self.add_entity(object_)
        
        # Add the relationship as an edge in the graph
        self.graph.add_edge(subject, object_, predicate=predicate, **attributes)
    
    def get_entity_attributes(self, entity: str) -> Dict[str, Any]:
        """Get the attributes of an entity.
        
        Args:
            entity: The name of the entity.
            
        Returns:
            A dictionary of attributes for the entity.
        """
        return self.entity_attributes.get(entity, {})
    
    def get_relationships(self, entity: str) -> List[Tuple[str, str, str, Dict[str, Any]]]:
        """Get all relationships involving an entity.
        
        Args:
            entity: The name of the entity.
            
        Returns:
            A list of tuples (subject, predicate, object, attributes) for each relationship.
        """
        relationships = []
        
        # Get outgoing relationships (where entity is the subject)
        for _, target, data in self.graph.out_edges(entity, data=True):
            predicate = data.pop('predicate')
            relationships.append((entity, predicate, target, data))
        
        # Get incoming relationships (where entity is the object)
        for source, _, data in self.graph.in_edges(entity, data=True):
            predicate = data.pop('predicate')
            relationships.append((source, predicate, entity, data))
        
        return relationships
    
    def query_relationship(self, subject: Optional[str] = None, predicate: Optional[str] = None, 
                          object_: Optional[str] = None) -> List[Tuple[str, str, str, Dict[str, Any]]]:
        """Query the knowledge graph for relationships matching the given pattern.
        
        Args:
            subject: Optional subject entity to match.
            predicate: Optional predicate to match.
            object_: Optional object entity to match.
            
        Returns:
            A list of tuples (subject, predicate, object, attributes) for each matching relationship.
        """
        results = []
        
        # Iterate through all edges in the graph
        for s, o, data in self.graph.edges(data=True):
            p = data.get('predicate')
            
            # Check if the edge matches the query pattern
            if ((subject is None or s == subject) and
                (predicate is None or p == predicate) and
                (object_ is None or o == object_)):
                
                # Copy the data dictionary and remove the predicate
                attrs = data.copy()
                attrs.pop('predicate')
                
                results.append((s, p, o, attrs))
        
        return results
    
    def get_entities_by_attribute(self, attribute: str, value: Any) -> List[str]:
        """Get all entities that have a specific attribute value.
        
        Args:
            attribute: The name of the attribute.
            value: The value to match.
            
        Returns:
            A list of entity names that have the specified attribute value.
        """
        results = []
        
        for entity, attrs in self.entity_attributes.items():
            if attribute in attrs and attrs[attribute] == value:
                results.append(entity)
        
        return results
    
    def get_entity_types(self, entity: str) -> Set[str]:
        """Get all types (classes) of an entity.
        
        Args:
            entity: The name of the entity.
            
        Returns:
            A set of type names for the entity.
        """
        types = set()
        
        # Look for 'is_a' or 'type' relationships
        for s, p, o, _ in self.query_relationship(subject=entity, predicate='is_a'):
            types.add(o)
        
        for s, p, o, _ in self.query_relationship(subject=entity, predicate='type'):
            types.add(o)
        
        return types
    
    def get_entities_of_type(self, type_name: str) -> List[str]:
        """Get all entities of a specific type.
        
        Args:
            type_name: The name of the type.
            
        Returns:
            A list of entity names of the specified type.
        """
        results = []
        
        # Look for 'is_a' or 'type' relationships
        for s, p, o, _ in self.query_relationship(predicate='is_a', object_=type_name):
            results.append(s)
        
        for s, p, o, _ in self.query_relationship(predicate='type', object_=type_name):
            results.append(s)
        
        return results
    
    def visualize(self, output_file: Optional[str] = None) -> None:
        """Visualize the knowledge graph.
        
        Args:
            output_file: Optional file path to save the visualization.
        """
        # Create a new graph with edge labels
        G = nx.DiGraph()
        
        # Add all nodes
        for node in self.graph.nodes():
            G.add_node(node)
        
        # Add all edges with predicates as labels
        for s, o, data in self.graph.edges(data=True):
            G.add_edge(s, o, label=data['predicate'])
        
        # Set up the plot
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G, seed=42)  # Position nodes using force-directed layout
        
        # Draw nodes and edges
        nx.draw_networkx_nodes(G, pos, node_size=500, node_color='lightblue')
        nx.draw_networkx_labels(G, pos, font_size=10)
        nx.draw_networkx_edges(G, pos, width=1, arrowsize=20)
        
        # Draw edge labels
        edge_labels = {(s, o): data['label'] for s, o, data in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
        
        plt.axis('off')  # Turn off axis
        
        if output_file:
            plt.savefig(output_file, bbox_inches='tight')
        else:
            plt.show()
    
    def to_json(self) -> str:
        """Convert the knowledge graph to a JSON string.
        
        Returns:
            A JSON string representation of the knowledge graph.
        """
        # Create a dictionary representation of the graph
        graph_dict = {
            'entities': {},
            'relationships': []
        }
        
        # Add entities and their attributes
        for entity, attrs in self.entity_attributes.items():
            graph_dict['entities'][entity] = attrs
        
        # Add relationships
        for s, o, data in self.graph.edges(data=True):
            relationship = {
                'subject': s,
                'predicate': data['predicate'],
                'object': o,
                'attributes': {k: v for k, v in data.items() if k != 'predicate'}
            }
            graph_dict['relationships'].append(relationship)
        
        # Convert to JSON string
        return json.dumps(graph_dict, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'KnowledgeGraph':
        """Create a knowledge graph from a JSON string.
        
        Args:
            json_str: A JSON string representation of a knowledge graph.
            
        Returns:
            A new KnowledgeGraph instance.
        """
        graph_dict = json.loads(json_str)
        kg = cls()
        
        # Add entities and their attributes
        for entity, attrs in graph_dict['entities'].items():
            kg.add_entity(entity, attrs)
        
        # Add relationships
        for rel in graph_dict['relationships']:
            kg.add_relationship(
                rel['subject'],
                rel['predicate'],
                rel['object'],
                rel['attributes']
            )
        
        return kg


# Example usage
def example():
    """Demonstrate the knowledge graph with a simple example."""
    kg = KnowledgeGraph()
    
    # Add entities with attributes
    kg.add_entity('socrates', {'birth_year': -470, 'death_year': -399})
    kg.add_entity('plato', {'birth_year': -428, 'death_year': -348})
    kg.add_entity('aristotle', {'birth_year': -384, 'death_year': -322})
    kg.add_entity('human', {'type': 'class'})
    kg.add_entity('mortal', {'type': 'class'})
    kg.add_entity('philosopher', {'type': 'class'})
    
    # Add relationships
    kg.add_relationship('socrates', 'is_a', 'human')
    kg.add_relationship('plato', 'is_a', 'human')
    kg.add_relationship('aristotle', 'is_a', 'human')
    kg.add_relationship('socrates', 'is_a', 'philosopher')
    kg.add_relationship('plato', 'is_a', 'philosopher')
    kg.add_relationship('aristotle', 'is_a', 'philosopher')
    kg.add_relationship('human', 'is_a', 'mortal')
    kg.add_relationship('socrates', 'teacher_of', 'plato')
    kg.add_relationship('plato', 'teacher_of', 'aristotle')
    
    # Query the knowledge graph
    print("Entities of type 'philosopher':")
    philosophers = kg.get_entities_of_type('philosopher')
    for philosopher in philosophers:
        print(f"- {philosopher}")
    
    print("\nRelationships involving Socrates:")
    socrates_relationships = kg.get_relationships('socrates')
    for s, p, o, attrs in socrates_relationships:
        print(f"- {s} {p} {o}")
    
    print("\nTeacher relationships:")
    teacher_relationships = kg.query_relationship(predicate='teacher_of')
    for s, p, o, attrs in teacher_relationships:
        print(f"- {s} {p} {o}")
    
    # Visualize the knowledge graph
    print("\nVisualizing the knowledge graph...")
    kg.visualize()
    
    # Convert to JSON and back
    json_str = kg.to_json()
    print("\nJSON representation:")
    print(json_str)
    
    new_kg = KnowledgeGraph.from_json(json_str)
    print("\nReconstructed knowledge graph:")
    print(f"Number of entities: {len(new_kg.entity_attributes)}")
    print(f"Number of relationships: {len(list(new_kg.graph.edges()))}")


if __name__ == "__main__":
    example()