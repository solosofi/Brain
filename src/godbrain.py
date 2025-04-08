# GODBRAIN - Main Integration Module
# Connects the different components of the GODBRAIN architecture

from typing import Dict, List, Tuple, Any, Optional

# Import components from different layers
try:
    from src.perception.text_parser import TextParser
    from src.logical_core.reasoning_engine import ReasoningEngine
    from src.world_model.knowledge_graph import KnowledgeGraph
    from src.metacognition.confidence_evaluator import ConfidenceEvaluator
    COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some components are not available: {e}")
    COMPONENTS_AVAILABLE = False


class GODBRAIN:
    """Main integration class for the GODBRAIN system.
    
    This class connects the different components of the GODBRAIN architecture,
    including the Perception Layer, Logical Core, World Model Layer, and
    Meta-Cognition Unit.
    """
    
    def __init__(self, confidence_threshold: float = 0.7):
        """Initialize the GODBRAIN system.
        
        Args:
            confidence_threshold: The threshold below which answers should be revised.
        """
        if not COMPONENTS_AVAILABLE:
            raise ImportError("Required components are not available. Please install the necessary dependencies.")
        
        # Initialize components
        self.perception = TextParser()
        self.logical_core = ReasoningEngine()
        self.world_model = KnowledgeGraph()
        self.metacognition = ConfidenceEvaluator(confidence_threshold=confidence_threshold)
        
        # Set up basic knowledge
        self._initialize_knowledge()
    
    def _initialize_knowledge(self) -> None:
        """Initialize the knowledge base with some basic facts and rules."""
        # Add some basic facts to the logical core
        self.logical_core.add_fact("human(socrates).")
        self.logical_core.add_fact("human(plato).")
        self.logical_core.add_fact("human(aristotle).")
        self.logical_core.add_fact("teacher(socrates, plato).")
        self.logical_core.add_fact("teacher(plato, aristotle).")
        
        # Add some basic rules to the logical core
        self.logical_core.add_rule("mortal(X) :- human(X).")
        self.logical_core.add_rule("student(X, Y) :- teacher(Y, X).")
        self.logical_core.add_rule("philosopher(X) :- human(X), teacher(X, _).")
        
        # Add corresponding entities and relationships to the world model
        self.world_model.add_entity('socrates', {'type': 'person'})
        self.world_model.add_entity('plato', {'type': 'person'})
        self.world_model.add_entity('aristotle', {'type': 'person'})
        self.world_model.add_entity('human', {'type': 'class'})
        self.world_model.add_entity('mortal', {'type': 'class'})
        self.world_model.add_entity('philosopher', {'type': 'class'})
        
        self.world_model.add_relationship('socrates', 'is_a', 'human')
        self.world_model.add_relationship('plato', 'is_a', 'human')
        self.world_model.add_relationship('aristotle', 'is_a', 'human')
        self.world_model.add_relationship('human', 'is_a', 'mortal')
        self.world_model.add_relationship('socrates', 'teacher_of', 'plato')
        self.world_model.add_relationship('plato', 'teacher_of', 'aristotle')
        self.world_model.add_relationship('socrates', 'is_a', 'philosopher')
        self.world_model.add_relationship('plato', 'is_a', 'philosopher')
    
    def process_input(self, text: str) -> Dict[str, Any]:
        """Process a natural language input and generate a response.
        
        Args:
            text: The natural language input to process.
            
        Returns:
            A dictionary containing the response, including:
            - answer: The answer to the input
            - confidence: The confidence score of the answer
            - explanation: An explanation of the reasoning process
        """
        # Parse the input using the Perception Layer
        parsed_input = self.perception.parse_input(text)
        
        # Convert the parsed input to Prolog format for the Logical Core
        prolog_query = self.perception.convert_to_prolog(parsed_input)
        
        if not prolog_query:
            return {
                'answer': "I don't understand the input.",
                'confidence': 0.0,
                'explanation': "The input could not be parsed into a format that I can reason about."
            }
        
        # Use the Logical Core to reason about the query
        is_true, confidence, results = self.logical_core.reason(prolog_query)
        
        # Generate an explanation using the Logical Core
        explanation = self.logical_core.explain(prolog_query)
        
        # Check if the answer needs revision using the Meta-Cognition Unit
        if self.metacognition.needs_revision(confidence):
            # Revise the answer
            is_true, confidence, revised_explanation = self.metacognition.revise_answer(
                is_true, confidence, self.logical_core, prolog_query
            )
            explanation = revised_explanation
        
        # Generate a natural language answer based on the query type
        answer = self._generate_answer(parsed_input, is_true, results)
        
        # Add a confidence explanation
        confidence_explanation = self.metacognition.explain_confidence(confidence)
        
        return {
            'answer': answer,
            'confidence': confidence,
            'explanation': explanation,
            'confidence_explanation': confidence_explanation
        }
    
    def _generate_answer(self, parsed_input: Dict[str, Any], is_true: bool, 
                        results: List[Dict[str, Any]]) -> str:
        """Generate a natural language answer based on the query type and reasoning results.
        
        Args:
            parsed_input: The parsed input from the Perception Layer.
            is_true: Whether the query is true according to the Logical Core.
            results: The variable bindings that satisfy the query.
            
        Returns:
            A natural language answer.
        """
        input_type = parsed_input['type']
        
        if input_type == 'question':
            subtype = parsed_input.get('subtype')
            content = parsed_input.get('content', {})
            
            if subtype == 'yes_no':
                # Yes/no question (e.g., "Is Socrates human?")
                subject = content.get('subject', '')
                predicate = content.get('predicate', '')
                
                if is_true:
                    return f"Yes, {subject} is {predicate}."
                else:
                    return f"No, {subject} is not {predicate} based on my knowledge."
            
            elif subtype == 'who':
                # "Who" question (e.g., "Who is human?")
                predicate = content.get('predicate', '')
                
                if results:
                    entities = [result.get('X', 'unknown') for result in results]
                    if len(entities) == 1:
                        return f"{entities[0]} is {predicate}."
                    else:
                        entity_list = ", ".join(entities[:-1]) + f" and {entities[-1]}"
                        return f"The following entities are {predicate}: {entity_list}."
                else:
                    return f"I don't know of any entities that are {predicate}."
            
            elif subtype == 'what':
                # "What" question (e.g., "What is Socrates?")
                subject = content.get('subject', '')
                
                # For "what" questions, we need to query the world model
                types = self.world_model.get_entity_types(subject)
                relationships = self.world_model.get_relationships(subject)
                
                if types:
                    type_list = ", ".join(types)
                    return f"{subject} is a {type_list}."
                elif relationships:
                    # Summarize relationships
                    rel_summary = []
                    for s, p, o, _ in relationships:
                        if s == subject:
                            rel_summary.append(f"{p} {o}")
                        else:
                            rel_summary.append(f"is {p} by {s}")
                    
                    if rel_summary:
                        rel_text = ", ".join(rel_summary)
                        return f"{subject} {rel_text}."
                    else:
                        return f"I know about {subject}, but I don't have specific information about what it is."
                else:
                    return f"I don't have any information about {subject}."
        
        # For other types of input, provide a generic response
        return "I've processed your input, but I'm not sure how to respond."
    
    def add_knowledge(self, text: str) -> Dict[str, Any]:
        """Add new knowledge to the system from natural language input.
        
        Args:
            text: The natural language input containing new knowledge.
            
        Returns:
            A dictionary containing the result of adding the knowledge.
        """
        # Parse the input using the Perception Layer
        parsed_input = self.perception.parse_input(text)
        
        if parsed_input['type'] not in ['fact', 'relation']:
            return {
                'success': False,
                'message': "The input does not appear to be a fact or relation that I can add to my knowledge base."
            }
        
        # Convert the parsed input to Prolog format for the Logical Core
        prolog_fact = self.perception.convert_to_prolog(parsed_input)
        
        if not prolog_fact:
            return {
                'success': False,
                'message': "The input could not be converted to a format that I can add to my knowledge base."
            }
        
        # Add the fact to the Logical Core
        try:
            self.logical_core.add_fact(prolog_fact)
            
            # Also add the corresponding entity or relationship to the World Model
            content = parsed_input.get('content', {})
            
            if parsed_input['type'] == 'fact':
                # Add entity to the world model
                subject = content.get('subject', '')
                predicate = content.get('predicate', '')
                
                self.world_model.add_entity(subject, {'type': 'entity'})
                self.world_model.add_entity(predicate, {'type': 'class'})
                self.world_model.add_relationship(subject, 'is_a', predicate)
            
            elif parsed_input['type'] == 'relation':
                # Add relationship to the world model
                subject = content.get('subject', '')
                verb = content.get('verb', '')
                object_ = content.get('object', '')
                
                self.world_model.add_entity(subject, {'type': 'entity'})
                self.world_model.add_entity(object_, {'type': 'entity'})
                self.world_model.add_relationship(subject, verb, object_)
            
            return {
                'success': True,
                'message': f"Successfully added new knowledge: {text}"
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f"Failed to add new knowledge: {str(e)}"
            }
    
    def get_confidence_stats(self) -> Dict[str, Any]:
        """Get statistics about the system's confidence in its answers.
        
        Returns:
            A dictionary containing confidence statistics.
        """
        return self.metacognition.get_confidence_stats()
    
    def get_revision_stats(self) -> Dict[str, Any]:
        """Get statistics about the system's revisions of its answers.
        
        Returns:
            A dictionary containing revision statistics.
        """
        return self.metacognition.get_revision_stats()
    
    def visualize_world_model(self, output_file: Optional[str] = None) -> None:
        """Visualize the world model.
        
        Args:
            output_file: Optional file path to save the visualization.
        """
        self.world_model.visualize(output_file)


# Example usage
def example():
    """Demonstrate the GODBRAIN system with a simple example."""
    try:
        # Initialize the GODBRAIN system
        brain = GODBRAIN()
        
        # Process some queries
        queries = [
            "Is Socrates mortal?",
            "Who is human?",
            "What is Socrates?",
            "Is Aristotle a philosopher?"
        ]
        
        for query in queries:
            print(f"\nQuery: {query}")
            response = brain.process_input(query)
            
            print(f"Answer: {response['answer']}")
            print(f"Confidence: {response['confidence']:.2%}")
            print(f"Confidence assessment: {response['confidence_explanation']}")
            print(f"Explanation: {response['explanation']}")
        
        # Add new knowledge
        new_facts = [
            "Alexander is human.",
            "Aristotle teaches Alexander."
        ]
        
        for fact in new_facts:
            print(f"\nAdding new knowledge: {fact}")
            result = brain.add_knowledge(fact)
            print(f"Result: {result['message']}")
        
        # Process a query about the new knowledge
        query = "Who is Alexander?"
        print(f"\nQuery: {query}")
        response = brain.process_input(query)
        
        print(f"Answer: {response['answer']}")
        print(f"Confidence: {response['confidence']:.2%}")
        print(f"Explanation: {response['explanation']}")
        
        # Get confidence and revision statistics
        print("\nConfidence Statistics:")
        stats = brain.get_confidence_stats()
        for key, value in stats.items():
            if isinstance(value, float):
                print(f"- {key}: {value:.2%}")
            else:
                print(f"- {key}: {value}")
        
        print("\nRevision Statistics:")
        stats = brain.get_revision_stats()
        for key, value in stats.items():
            if isinstance(value, float):
                print(f"- {key}: {value:.2%}")
            else:
                print(f"- {key}: {value}")
        
        # Visualize the world model
        print("\nVisualizing the world model...")
        brain.visualize_world_model()
    
    except ImportError as e:
        print(f"Error: {e}")
        print("This example requires all GODBRAIN components to be available.")
        print("Please install the necessary dependencies (pip install -r requirements.txt).")


if __name__ == "__main__":
    example()