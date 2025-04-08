# Meta-Cognition Unit - Confidence Evaluator
# Evaluates the confidence of the AI's answers and revises them if necessary

from typing import Dict, List, Tuple, Any, Optional, Union
import numpy as np


class ConfidenceEvaluator:
    """Confidence evaluator for the Meta-Cognition Unit.
    
    This class is responsible for evaluating the confidence of the AI's answers
    and revising them if necessary. It implements the meta-cognitive abilities
    of the GODBRAIN system.
    """
    
    def __init__(self, confidence_threshold: float = 0.7):
        """Initialize the confidence evaluator.
        
        Args:
            confidence_threshold: The threshold below which answers should be revised.
        """
        self.confidence_threshold = confidence_threshold
        self.confidence_history = []  # Track confidence scores over time
        self.revision_history = []    # Track revisions made
    
    def evaluate_confidence(self, answer: Any, evidence: List[Any], 
                           certainty_factors: List[float]) -> float:
        """Evaluate the confidence of an answer based on evidence and certainty factors.
        
        Args:
            answer: The answer to evaluate.
            evidence: List of evidence supporting the answer.
            certainty_factors: List of certainty factors for each piece of evidence.
            
        Returns:
            A confidence score between 0.0 and 1.0.
        """
        if not evidence or not certainty_factors:
            return 0.0
        
        if len(evidence) != len(certainty_factors):
            raise ValueError("Evidence and certainty factors must have the same length")
        
        # Calculate weighted average of certainty factors
        weighted_sum = sum(cf for cf in certainty_factors)
        confidence = weighted_sum / len(certainty_factors)
        
        # Apply sigmoid function to smooth the confidence score
        confidence = 1.0 / (1.0 + np.exp(-5 * (confidence - 0.5)))
        
        # Ensure confidence is between 0 and 1
        confidence = max(0.0, min(1.0, confidence))
        
        # Record the confidence score
        self.confidence_history.append(confidence)
        
        return confidence
    
    def needs_revision(self, confidence: float) -> bool:
        """Determine if an answer needs revision based on its confidence score.
        
        Args:
            confidence: The confidence score of the answer.
            
        Returns:
            True if the answer needs revision, False otherwise.
        """
        return confidence < self.confidence_threshold
    
    def revise_answer(self, answer: Any, confidence: float, 
                     reasoning_engine: Any, query: str) -> Tuple[Any, float, str]:
        """Revise an answer if its confidence is below the threshold.
        
        Args:
            answer: The original answer.
            confidence: The confidence score of the original answer.
            reasoning_engine: The reasoning engine to use for revision.
            query: The original query.
            
        Returns:
            A tuple containing:
            - The revised answer (or the original if no revision was needed)
            - The revised confidence score
            - An explanation of the revision process
        """
        if not self.needs_revision(confidence):
            return answer, confidence, "No revision needed."
        
        # Record the revision attempt
        self.revision_history.append({
            'original_confidence': confidence,
            'query': query
        })
        
        # Use the reasoning engine to revise the answer
        # This is a simplified version; in a real system, this would be more sophisticated
        try:
            is_true, revised_confidence, explanation = reasoning_engine.revise_reasoning(query)
            
            # Update the revision history with the result
            self.revision_history[-1].update({
                'revised_confidence': revised_confidence,
                'successful': revised_confidence > confidence
            })
            
            return is_true, revised_confidence, explanation
        except Exception as e:
            # If revision fails, return the original answer with an explanation
            return answer, confidence, f"Revision failed: {str(e)}"
    
    def get_confidence_stats(self) -> Dict[str, float]:
        """Get statistics about the confidence scores.
        
        Returns:
            A dictionary containing statistics about the confidence scores.
        """
        if not self.confidence_history:
            return {
                'mean': 0.0,
                'median': 0.0,
                'min': 0.0,
                'max': 0.0,
                'std': 0.0
            }
        
        confidence_array = np.array(self.confidence_history)
        
        return {
            'mean': float(np.mean(confidence_array)),
            'median': float(np.median(confidence_array)),
            'min': float(np.min(confidence_array)),
            'max': float(np.max(confidence_array)),
            'std': float(np.std(confidence_array))
        }
    
    def get_revision_stats(self) -> Dict[str, Union[int, float]]:
        """Get statistics about the revisions made.
        
        Returns:
            A dictionary containing statistics about the revisions made.
        """
        total_revisions = len(self.revision_history)
        
        if total_revisions == 0:
            return {
                'total_revisions': 0,
                'successful_revisions': 0,
                'success_rate': 0.0,
                'average_confidence_improvement': 0.0
            }
        
        successful_revisions = sum(1 for rev in self.revision_history if rev.get('successful', False))
        
        confidence_improvements = [
            rev.get('revised_confidence', 0.0) - rev.get('original_confidence', 0.0)
            for rev in self.revision_history
            if 'revised_confidence' in rev and 'original_confidence' in rev
        ]
        
        avg_improvement = np.mean(confidence_improvements) if confidence_improvements else 0.0
        
        return {
            'total_revisions': total_revisions,
            'successful_revisions': successful_revisions,
            'success_rate': successful_revisions / total_revisions if total_revisions > 0 else 0.0,
            'average_confidence_improvement': float(avg_improvement)
        }
    
    def explain_confidence(self, confidence: float) -> str:
        """Provide a human-readable explanation of a confidence score.
        
        Args:
            confidence: The confidence score to explain.
            
        Returns:
            A string explaining the confidence score.
        """
        if confidence >= 0.9:
            return "I am very confident in this answer."
        elif confidence >= 0.7:
            return "I am reasonably confident in this answer."
        elif confidence >= 0.5:
            return "I am somewhat confident in this answer, but there is room for doubt."
        elif confidence >= 0.3:
            return "I am not very confident in this answer. It should be treated with caution."
        else:
            return "I have very low confidence in this answer. It is likely incorrect or incomplete."


# Example usage
def example():
    """Demonstrate the confidence evaluator with a simple example."""
    evaluator = ConfidenceEvaluator(confidence_threshold=0.7)
    
    # Simulate some answers with evidence and certainty factors
    answers = [
        ("Socrates is mortal", ["Socrates is human", "All humans are mortal"], [0.9, 0.95]),
        ("Plato is a philosopher", ["Plato taught at the Academy"], [0.8]),
        ("Aristotle was Plato's student", ["Historical records suggest this"], [0.6]),
        ("The Earth is flat", ["It looks flat from my perspective"], [0.2])
    ]
    
    for answer, evidence, certainty_factors in answers:
        confidence = evaluator.evaluate_confidence(answer, evidence, certainty_factors)
        
        print(f"\nAnswer: {answer}")
        print(f"Evidence: {evidence}")
        print(f"Certainty factors: {certainty_factors}")
        print(f"Confidence: {confidence:.2%}")
        print(f"Explanation: {evaluator.explain_confidence(confidence)}")
        
        if evaluator.needs_revision(confidence):
            print("This answer needs revision.")
        else:
            print("This answer does not need revision.")
    
    # Print confidence statistics
    print("\nConfidence Statistics:")
    stats = evaluator.get_confidence_stats()
    for key, value in stats.items():
        if key in ['mean', 'median', 'min', 'max']:
            print(f"- {key}: {value:.2%}")
        else:
            print(f"- {key}: {value:.4f}")


if __name__ == "__main__":
    example()