# Logical Core - Reasoning Engine
# Implements basic symbolic reasoning capabilities using Prolog

import os
from typing import Dict, List, Tuple, Any, Optional

try:
    from pyswip import Prolog
    PYSWIP_AVAILABLE = True
except ImportError:
    PYSWIP_AVAILABLE = False
    print("Warning: pyswip not available. Install it with 'pip install pyswip' for Prolog integration.")


class ReasoningEngine:
    """Symbolic reasoning engine using Prolog for logical inference.
    
    This class implements the core reasoning capabilities of the GODBRAIN system,
    allowing it to make inferences and deductions from a given set of facts and rules.
    """
    
    def __init__(self):
        """Initialize the reasoning engine."""
        if not PYSWIP_AVAILABLE:
            raise ImportError("pyswip is required for the ReasoningEngine. Install it with 'pip install pyswip'")
        
        self.prolog = Prolog()
        self.knowledge_base = []
        self.confidence_threshold = 0.7  # Default confidence threshold (70%)
    
    def add_fact(self, fact: str) -> None:
        """Add a fact to the knowledge base.
        
        Args:
            fact: A string representing a Prolog fact (e.g., "human(socrates).").
        """
        self.prolog.assertz(fact)
        self.knowledge_base.append(fact)
    
    def add_rule(self, rule: str) -> None:
        """Add a rule to the knowledge base.
        
        Args:
            rule: A string representing a Prolog rule (e.g., "mortal(X) :- human(X).").
        """
        self.prolog.assertz(rule)
        self.knowledge_base.append(rule)
    
    def query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a query against the knowledge base.
        
        Args:
            query: A string representing a Prolog query (e.g., "mortal(socrates)").
            
        Returns:
            A list of dictionaries containing variable bindings that satisfy the query.
        """
        return list(self.prolog.query(query))
    
    def reason(self, query: str) -> Tuple[bool, float, List[Dict[str, Any]]]:
        """Reason about a query and provide a confidence score.
        
        Args:
            query: A string representing a Prolog query.
            
        Returns:
            A tuple containing:
            - Boolean indicating if the query is true
            - Confidence score (0.0 to 1.0)
            - List of variable bindings that satisfy the query
        """
        results = self.query(query)
        
        # Simple confidence calculation based on the number and quality of results
        # In a real system, this would be more sophisticated
        if results:
            # Some basic heuristics for confidence
            confidence = min(1.0, 0.8 + (len(results) * 0.05))
            return True, confidence, results
        else:
            return False, 0.0, []
    
    def explain(self, query: str) -> str:
        """Provide an explanation for a reasoning result.
        
        Args:
            query: A string representing a Prolog query.
            
        Returns:
            A string explaining the reasoning process.
        """
        is_true, confidence, results = self.reason(query)
        
        if is_true:
            explanation = f"The query '{query}' is true with {confidence:.2%} confidence.\n"
            explanation += "This conclusion is based on the following facts and rules:\n"
            
            # In a real system, we would trace the actual inference path
            # For now, we just list the relevant parts of the knowledge base
            for item in self.knowledge_base:
                if any(term in item for term in query.split('(')[0:1]):
                    explanation += f"- {item}\n"
            
            return explanation
        else:
            return f"The query '{query}' could not be proven based on the current knowledge base."
    
    def revise_reasoning(self, query: str) -> Tuple[bool, float, str]:
        """Attempt to improve reasoning if confidence is low.
        
        Args:
            query: A string representing a Prolog query.
            
        Returns:
            A tuple containing:
            - Boolean indicating if the query is true after revision
            - Revised confidence score
            - Explanation of the revised reasoning
        """
        is_true, confidence, results = self.reason(query)
        
        if confidence < self.confidence_threshold:
            # In a real system, this would implement more sophisticated revision strategies
            # For now, we just try a simple generalization
            
            # Extract the predicate and arguments
            parts = query.split('(')
            if len(parts) > 1:
                predicate = parts[0]
                args = parts[1].rstrip(')').split(',')
                
                # Try to find related facts or rules
                related_knowledge = []
                for item in self.knowledge_base:
                    if predicate in item:
                        related_knowledge.append(item)
                
                if related_knowledge:
                    new_confidence = min(1.0, confidence + 0.15)  # Boost confidence a bit
                    explanation = f"After revision, confidence increased from {confidence:.2%} to {new_confidence:.2%}.\n"
                    explanation += "Revision considered these related facts and rules:\n"
                    for item in related_knowledge:
                        explanation += f"- {item}\n"
                    
                    return is_true, new_confidence, explanation
        
        # If no revision was done or needed
        return is_true, confidence, self.explain(query)


# Example usage
def example():
    """Demonstrate the reasoning engine with a classic syllogism example."""
    engine = ReasoningEngine()
    
    # Add facts and rules
    engine.add_fact("human(socrates).")
    engine.add_rule("mortal(X) :- human(X).")
    
    # Query and explain
    query = "mortal(socrates)"
    is_true, confidence, results = engine.reason(query)
    
    print(f"Query: {query}")
    print(f"Result: {is_true} (Confidence: {confidence:.2%})")
    print("\nExplanation:")
    print(engine.explain(query))
    
    # Try a query with lower confidence
    uncertain_query = "philosopher(socrates)"
    is_true, confidence, results = engine.reason(uncertain_query)
    
    print(f"\nUncertain Query: {uncertain_query}")
    print(f"Initial Result: {is_true} (Confidence: {confidence:.2%})")
    
    # Revise reasoning
    is_true, revised_confidence, explanation = engine.revise_reasoning(uncertain_query)
    print("\nAfter revision:")
    print(f"Result: {is_true} (Confidence: {revised_confidence:.2%})")
    print("\nRevised Explanation:")
    print(explanation)


if __name__ == "__main__":
    if PYSWIP_AVAILABLE:
        example()
    else:
        print("Cannot run example: pyswip is not installed.")