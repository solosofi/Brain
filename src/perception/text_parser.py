# Perception Layer - Text Parser
# Parses raw text input and converts it into a structured form for the Logical Core

import re
from typing import Dict, List, Tuple, Any, Optional


class TextParser:
    """Text parser for the Perception Layer.
    
    This class is responsible for parsing raw text input and converting it into
    a structured form that can be used by the Logical Core for reasoning.
    """
    
    def __init__(self):
        """Initialize the text parser."""
        # Regular expressions for identifying different types of statements
        self.fact_pattern = re.compile(r'^([A-Za-z]+)\s+is\s+([A-Za-z]+)\.$')
        self.relation_pattern = re.compile(r'^([A-Za-z]+)\s+([A-Za-z]+)\s+([A-Za-z]+)\.$')
        self.question_pattern = re.compile(r'^Is\s+([A-Za-z]+)\s+([A-Za-z]+)\?$')
        self.who_question_pattern = re.compile(r'^Who\s+is\s+([A-Za-z]+)\?$')
        self.what_question_pattern = re.compile(r'^What\s+is\s+([A-Za-z]+)\?$')
    
    def parse_input(self, text: str) -> Dict[str, Any]:
        """Parse raw text input and convert it into a structured form.
        
        Args:
            text: Raw text input to parse.
            
        Returns:
            A dictionary containing the parsed information, including:
            - type: The type of input (fact, relation, question)
            - content: The structured content of the input
        """
        text = text.strip()
        
        # Check if the input is a fact (e.g., "Socrates is human.")
        fact_match = self.fact_pattern.match(text)
        if fact_match:
            subject, predicate = fact_match.groups()
            return {
                'type': 'fact',
                'content': {
                    'subject': subject.lower(),
                    'predicate': predicate.lower()
                }
            }
        
        # Check if the input is a relation (e.g., "Socrates teaches Plato.")
        relation_match = self.relation_pattern.match(text)
        if relation_match:
            subject, verb, object_ = relation_match.groups()
            return {
                'type': 'relation',
                'content': {
                    'subject': subject.lower(),
                    'verb': verb.lower(),
                    'object': object_.lower()
                }
            }
        
        # Check if the input is a yes/no question (e.g., "Is Socrates human?")
        question_match = self.question_pattern.match(text)
        if question_match:
            subject, predicate = question_match.groups()
            return {
                'type': 'question',
                'subtype': 'yes_no',
                'content': {
                    'subject': subject.lower(),
                    'predicate': predicate.lower()
                }
            }
        
        # Check if the input is a "who" question (e.g., "Who is human?")
        who_question_match = self.who_question_pattern.match(text)
        if who_question_match:
            predicate = who_question_match.group(1)
            return {
                'type': 'question',
                'subtype': 'who',
                'content': {
                    'predicate': predicate.lower()
                }
            }
        
        # Check if the input is a "what" question (e.g., "What is Socrates?")
        what_question_match = self.what_question_pattern.match(text)
        if what_question_match:
            subject = what_question_match.group(1)
            return {
                'type': 'question',
                'subtype': 'what',
                'content': {
                    'subject': subject.lower()
                }
            }
        
        # If the input doesn't match any of the patterns, return an unknown type
        return {
            'type': 'unknown',
            'content': {
                'text': text
            }
        }
    
    def convert_to_prolog(self, parsed_input: Dict[str, Any]) -> Optional[str]:
        """Convert parsed input into Prolog format for the Logical Core.
        
        Args:
            parsed_input: The parsed input from parse_input().
            
        Returns:
            A string in Prolog format, or None if the input can't be converted.
        """
        input_type = parsed_input['type']
        content = parsed_input['content']
        
        if input_type == 'fact':
            # Convert a fact to Prolog (e.g., "human(socrates).")
            return f"{content['predicate']}({content['subject']})."
        
        elif input_type == 'relation':
            # Convert a relation to Prolog (e.g., "teaches(socrates, plato).")
            return f"{content['verb']}({content['subject']}, {content['object']})."
        
        elif input_type == 'question':
            subtype = parsed_input['subtype']
            
            if subtype == 'yes_no':
                # Convert a yes/no question to Prolog (e.g., "human(socrates)")
                return f"{content['predicate']}({content['subject']})"
            
            elif subtype == 'who':
                # Convert a "who" question to Prolog (e.g., "human(X)")
                return f"{content['predicate']}(X)"
            
            elif subtype == 'what':
                # Convert a "what" question to Prolog (e.g., "X(socrates)")
                # This is a bit tricky in Prolog, as predicates can't be variables
                # For now, we'll return None and handle this case specially
                return None
        
        # If the input can't be converted to Prolog, return None
        return None


# Example usage
def example():
    """Demonstrate the text parser with some examples."""
    parser = TextParser()
    
    examples = [
        "Socrates is human.",
        "Plato is human.",
        "Socrates teaches Plato.",
        "Is Socrates human?",
        "Who is human?",
        "What is Socrates?",
        "This is not a valid input."
    ]
    
    for text in examples:
        print(f"\nInput: {text}")
        parsed = parser.parse_input(text)
        print(f"Parsed: {parsed}")
        
        prolog = parser.convert_to_prolog(parsed)
        print(f"Prolog: {prolog}")


if __name__ == "__main__":
    example()