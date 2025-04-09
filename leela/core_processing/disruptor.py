"""
Disruptor Module - Creates conceptual superpositions by forcing paradoxical states and challenging assumptions.

Implements prompts: disruptor_assumption_detection.txt, disruptor_inversion.txt, disruptor_paradox_generation.txt
"""
from typing import Dict, List, Any, Optional, Tuple
import uuid
import asyncio
from pydantic import UUID4
from ..config import get_config
from ..knowledge_representation.models import (
    CreativeIdea, ThinkingStep, ShockProfile, Concept, ConceptState
)
from ..directed_thinking.claude_api import ClaudeAPIClient
from ..knowledge_representation.superposition_engine import SuperpositionEngine
from ..prompt_management import uses_prompt


@uses_prompt("disruptor_assumption_detection")
class AssumptionDetector:
    """
    Detects implicit assumptions in problem spaces across multiple dimensions.
    
    This class implements the disruptor_assumption_detection.txt prompt to identify
    hidden assumptions in a problem statement that might limit solution possibilities.
    It analyzes assumptions across technological, methodological, conceptual, 
    philosophical, and cultural dimensions.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Assumption Detector.
        
        Args:
            api_key: Optional API key for Claude. If not provided, will try to get from config.
        """
        config = get_config()
        self.api_key = api_key or config["api"]["anthropic_api_key"]
        self.claude_client = ClaudeAPIClient(self.api_key)
        
        # Common assumptions by domain
        self.domain_assumptions = {
            "physics": [
                "Locality in space and time",
                "Causal determinism",
                "Conservation laws are inviolable",
                "Uniform arrow of time",
                "Observer independence",
                "Reducibility to fundamental particles",
                "Symmetry as a guiding principle"
            ],
            "biology": [
                "Cellular basis of life",
                "DNA as primary information carrier",
                "Natural selection as primary evolutionary mechanism",
                "Biochemical basis of metabolism",
                "Species boundaries",
                "Predictable genetic expression",
                "Hierarchical organization of life"
            ],
            "computer_science": [
                "Binary logic",
                "Deterministic computation",
                "Church-Turing thesis",
                "Von Neumann architecture",
                "Sequential processing",
                "Scalability as essential",
                "Problem decomposition as optimal approach"
            ],
            "economics": [
                "Rational actors",
                "Scarcity as fundamental",
                "Value derived from scarcity",
                "Growth as essential",
                "Self-interest as driver",
                "Market efficiency",
                "Quantifiable utility"
            ],
            "mathematics": [
                "Logical consistency",
                "Set theory foundation",
                "Law of excluded middle",
                "Mathematical Platonism",
                "ZFC axioms",
                "Completeness as desirable",
                "Formal proof as ultimate verification"
            ],
            "art": [
                "Aesthetic value is subjective",
                "Originality as essential",
                "Expression of human emotion",
                "Cultural context shapes meaning",
                "Visual/auditory perception as primary",
                "Creator's intent matters",
                "Art serves social functions"
            ],
            "psychology": [
                "Mind emerges from brain",
                "Behavior can be predicted",
                "Personality is relatively stable",
                "Developmental stages are universal",
                "Cognition defines experience",
                "Mental disorders are identifiable patterns",
                "Individual as primary unit of analysis"
            ]
        }
        
        # Assumption categories for multidimensional analysis
        self.assumption_categories = [
            "Methodological assumptions",
            "Ontological assumptions",
            "Value systems",
            "Temporal assumptions",
            "Boundary assumptions",
            "Governance assumptions",
            "Core vocabulary"
        ]
    
    async def detect_assumptions(self, problem_statement: str, domain: str) -> Dict[str, Any]:
        """
        Detect implicit assumptions in a problem statement across multiple dimensions.
        
        Args:
            problem_statement: The problem statement to analyze
            domain: The domain of the problem
            
        Returns:
            Dict[str, Any]: Comprehensive assumption analysis including core assumptions,
                            hidden constraints, and revealing questions
        """
        # Use the prompt_loader to get the prompt from the file system
        from ..prompt_management.prompt_loader import PromptLoader
        prompt_loader = PromptLoader()
        
        # Render the prompt template with context
        prompt = prompt_loader.render_prompt(
            "disruptor_assumption_detection",
            {
                "domain": domain,
                "problem_statement": problem_statement
            }
        )
        
        if not prompt:
            # Fallback in case prompt loading fails
            raise ValueError(f"Failed to load disruptor_assumption_detection prompt template")
        
        # Generate thinking
        thinking_step = await self.claude_client.generate_thinking(
            prompt=prompt,
            thinking_budget=16000,  # Use a higher budget for deeper analysis
            max_tokens=20000  # Ensure max_tokens > thinking_budget
        )
        
        # Extract structured assumption analysis from thinking
        assumption_analysis = self._extract_assumption_analysis(thinking_step.reasoning_process)
        
        # Start with domain-specific common assumptions if available
        predefined_assumptions = self.domain_assumptions.get(domain, [])
        
        # Combine with extracted assumptions, prioritizing the LLM's extracted ones
        if "core_assumptions" in assumption_analysis and assumption_analysis["core_assumptions"]:
            # Keep any predefined assumptions that don't overlap with extracted ones
            core_assumptions_text = assumption_analysis["core_assumptions"].lower()
            additional_assumptions = [
                a for a in predefined_assumptions 
                if a.lower() not in core_assumptions_text
            ][:3]  # Take up to 3 additional predefined assumptions
            
            # Format the result
            result = assumption_analysis
            result["additional_assumptions"] = additional_assumptions
        else:
            # Fallback if no structured extraction was possible
            extracted_assumptions = self._extract_assumptions_fallback(thinking_step.reasoning_process)
            result = {
                "core_assumptions": self._format_unstructured_assumptions(extracted_assumptions),
                "additional_assumptions": predefined_assumptions[:5],
                "revealing_questions": self._extract_questions_fallback(thinking_step.reasoning_process)
            }
        
        # Include original thinking for reference
        result["thinking_process"] = thinking_step.reasoning_process
        
        return result
    
    def _extract_assumption_analysis(self, thinking_text: str) -> Dict[str, str]:
        """
        Extract structured assumption analysis from thinking text.
        
        Args:
            thinking_text: The thinking text to extract from
            
        Returns:
            Dict[str, str]: Extracted structured assumption analysis
        """
        result = {}
        
        # Extract core assumptions
        import re
        core_pattern = r'<core_assumptions>(.*?)</core_assumptions>'
        core_match = re.search(core_pattern, thinking_text, re.DOTALL)
        if core_match:
            result["core_assumptions"] = core_match.group(1).strip()
        
        # Extract hidden constraints
        constraints_pattern = r'<hidden_constraints>(.*?)</hidden_constraints>'
        constraints_match = re.search(constraints_pattern, thinking_text, re.DOTALL)
        if constraints_match:
            result["hidden_constraints"] = constraints_match.group(1).strip()
        
        # Extract revealing questions
        questions_pattern = r'<revealing_questions>(.*?)</revealing_questions>'
        questions_match = re.search(questions_pattern, thinking_text, re.DOTALL)
        if questions_match:
            result["revealing_questions"] = questions_match.group(1).strip()
        
        # Extract individual analysis sections if needed
        for category in ["domain_fundamentals", "core_vocabulary", "methodological_assumptions", 
                        "value_systems", "boundary_assumptions", "temporal_assumptions", 
                        "governance_assumptions", "ontological_assumptions"]:
            pattern = f'<{category}>(.*?)</{category}>'
            match = re.search(pattern, thinking_text, re.DOTALL)
            if match:
                result[category] = match.group(1).strip()
        
        return result
    
    def _extract_assumptions_fallback(self, thinking_text: str) -> List[str]:
        """
        Fallback method to extract assumptions from thinking text when structured extraction fails.
        
        Args:
            thinking_text: The thinking text to extract from
            
        Returns:
            List[str]: Extracted assumptions
        """
        assumptions = []
        
        # Look for numbered or bulleted lists
        import re
        
        # Pattern for numbered list items
        numbered_pattern = r'\d+\.\s+(.*?)(?=\d+\.\s+|\n\n|$)'
        numbered_matches = re.findall(numbered_pattern, thinking_text, re.DOTALL)
        
        # Pattern for bulleted list items
        bulleted_pattern = r'[-*•]\s+(.*?)(?=[-*•]\s+|\n\n|$)'
        bulleted_matches = re.findall(bulleted_pattern, thinking_text, re.DOTALL)
        
        # Combine matches
        matches = numbered_matches + bulleted_matches
        
        # Clean and add to assumptions
        for match in matches:
            assumption = match.strip()
            # Remove any trailing explanation after a colon or dash
            assumption = re.split(r'[:\-–]', assumption)[0].strip()
            
            # Only add if not too short and not too long
            if 5 < len(assumption) < 150:
                assumptions.append(assumption)
        
        # If no structured list is found, try to find sentences with assumption indicators
        if not assumptions:
            sentences = re.split(r'(?<=[.!?])\s+', thinking_text)
            assumption_indicators = [
                "assumes", "assumption", "presupposes", "takes for granted",
                "implicit", "underlying", "unstated"
            ]
            for sentence in sentences:
                if any(indicator in sentence.lower() for indicator in assumption_indicators):
                    # Clean the sentence
                    clean_sentence = sentence.strip()
                    if 10 < len(clean_sentence) < 150:
                        assumptions.append(clean_sentence)
        
        return assumptions[:7]  # Return up to 7 assumptions
    
    def _extract_questions_fallback(self, thinking_text: str) -> List[str]:
        """
        Extract revealing questions when structured extraction fails.
        
        Args:
            thinking_text: The thinking text to extract from
            
        Returns:
            List[str]: Extracted questions
        """
        # Find sentences that end with question marks
        import re
        questions = re.findall(r'[^.!?]*\?\s*', thinking_text)
        
        # Clean and filter questions
        filtered_questions = []
        for q in questions:
            q = q.strip()
            if 15 < len(q) < 200 and q not in filtered_questions:
                filtered_questions.append(q)
        
        return filtered_questions[:5]  # Return up to 5 questions
    
    def _format_unstructured_assumptions(self, assumptions: List[str]) -> str:
        """
        Format a list of assumptions into a structured text.
        
        Args:
            assumptions: List of assumption strings
            
        Returns:
            str: Formatted assumptions text
        """
        result = "Key assumptions identified in this domain:\n\n"
        for i, assumption in enumerate(assumptions, 1):
            result += f"{i}. {assumption}\n\n"
        return result


@uses_prompt("disruptor_inversion")
class InversionEngine:
    """
    Generates systematic inversions of identified assumptions across multiple dimensions.
    
    This class implements the disruptor_inversion.txt prompt to create inversions
    of conventional assumptions, enabling the exploration of unconventional solution spaces.
    It applies multiple inversion techniques including direct reversal, dimensional inversion,
    hierarchical inversion, relational inversion, and contextual inversion.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Inversion Engine.
        
        Args:
            api_key: Optional API key for Claude. If not provided, will try to get from config.
        """
        config = get_config()
        self.api_key = api_key or config["api"]["anthropic_api_key"]
        self.claude_client = ClaudeAPIClient(self.api_key)
        
        # Common inversion patterns for different dimensions
        self.inversion_patterns = {
            # Direct opposites (presence/absence)
            "direct": [
                (r'always', 'never'),
                (r'never', 'always'),
                (r'all', 'none'),
                (r'none', 'all'),
                (r'must', 'cannot'),
                (r'cannot', 'must'),
                (r'is', 'is not'),
                (r'are', 'are not'),
                (r'will', 'will not'),
                (r'can', 'cannot'),
                (r'should', 'should not'),
                (r'possible', 'impossible'),
                (r'necessary', 'unnecessary'),
                (r'true', 'false'),
                (r'false', 'true'),
                (r'required', 'optional'),
                (r'certain', 'uncertain'),
                (r'known', 'unknown'),
                (r'complete', 'incomplete'),
                (r'universal', 'specific'),
            ],
            
            # Qualitative inversions
            "qualitative": [
                (r'increase', 'decrease'),
                (r'decrease', 'increase'),
                (r'positive', 'negative'),
                (r'negative', 'positive'),
                (r'high', 'low'),
                (r'low', 'high'),
                (r'large', 'small'),
                (r'small', 'large'),
                (r'fast', 'slow'),
                (r'slow', 'fast'),
                (r'more', 'less'),
                (r'less', 'more'),
                (r'strong', 'weak'),
                (r'weak', 'strong'),
                (r'complex', 'simple'),
                (r'simple', 'complex'),
                (r'efficient', 'inefficient'),
                (r'beneficial', 'harmful'),
                (r'abundant', 'scarce'),
                (r'scarce', 'abundant'),
            ],
            
            # Relationship inversions
            "relational": [
                (r'causes', 'is caused by'),
                (r'precedes', 'follows'),
                (r'follows', 'precedes'),
                (r'contains', 'is contained by'),
                (r'includes', 'is included in'),
                (r'creates', 'is created by'),
                (r'produces', 'is produced by'),
                (r'controls', 'is controlled by'),
                (r'influences', 'is influenced by'),
                (r'depends on', 'is depended upon by'),
                (r'requires', 'is required by'),
                (r'limits', 'is limited by'),
                (r'enables', 'is enabled by'),
                (r'constrains', 'is constrained by'),
                (r'determines', 'is determined by'),
                (r'shapes', 'is shaped by'),
                (r'defines', 'is defined by'),
                (r'affects', 'is affected by'),
            ],
            
            # Hierarchical inversions
            "hierarchical": [
                (r'primary', 'secondary'),
                (r'secondary', 'primary'),
                (r'central', 'peripheral'),
                (r'peripheral', 'central'),
                (r'dominant', 'subordinate'),
                (r'subordinate', 'dominant'),
                (r'essential', 'optional'),
                (r'optional', 'essential'),
                (r'fundamental', 'emergent'),
                (r'emergent', 'fundamental'),
                (r'explicit', 'implicit'),
                (r'implicit', 'explicit'),
                (r'leader', 'follower'),
                (r'follower', 'leader'),
                (r'macro', 'micro'),
                (r'micro', 'macro'),
                (r'global', 'local'),
                (r'local', 'global'),
            ],
            
            # Domain concepts
            "concepts": [
                (r'deterministic', 'probabilistic'),
                (r'discrete', 'continuous'),
                (r'linear', 'non-linear'),
                (r'sequential', 'parallel'),
                (r'centralized', 'decentralized'),
                (r'rational', 'irrational'),
                (r'finite', 'infinite'),
                (r'static', 'dynamic'),
                (r'homogeneous', 'heterogeneous'),
                (r'uniform', 'diverse'),
                (r'ordered', 'chaotic'),
                (r'bounded', 'unbounded'),
                (r'isolated', 'connected'),
                (r'competition', 'cooperation'),
                (r'individual', 'collective'),
                (r'specialized', 'generalized'),
                (r'predictable', 'unpredictable'),
                (r'mechanistic', 'organic'),
                (r'objective', 'subjective'),
                (r'convergent', 'divergent'),
            ],
            
            # Temporal inversions
            "temporal": [
                (r'past', 'future'),
                (r'future', 'past'),
                (r'begin', 'end'),
                (r'end', 'begin'),
                (r'early', 'late'),
                (r'late', 'early'),
                (r'young', 'old'),
                (r'old', 'young'),
                (r'temporary', 'permanent'),
                (r'permanent', 'temporary'),
                (r'constant', 'variable'),
                (r'variable', 'constant'),
                (r'instantaneous', 'gradual'),
                (r'gradual', 'instantaneous'),
                (r'sequential', 'simultaneous'),
                (r'modern', 'ancient'),
                (r'before', 'after'),
                (r'after', 'before'),
            ],
            
            # Contextual inversions
            "contextual": [
                (r'human', 'machine'),
                (r'machine', 'human'),
                (r'natural', 'artificial'),
                (r'artificial', 'natural'),
                (r'physical', 'virtual'),
                (r'virtual', 'physical'),
                (r'concrete', 'abstract'),
                (r'abstract', 'concrete'),
                (r'theoretical', 'practical'),
                (r'practical', 'theoretical'),
                (r'internal', 'external'),
                (r'external', 'internal'),
                (r'formal', 'informal'),
                (r'explicit', 'tacit'),
                (r'tacit', 'explicit'),
                (r'public', 'private'),
                (r'private', 'public'),
            ],
        }
        
        # Negation prefixes for fallback
        self.negation_prefixes = [
            "Not ", "The absence of ", "The inverse of ", "The opposite of ",
            "The rejection of ", "The negation of ", "Contrary to ", 
            "In opposition to ", "Abandoning the notion that ", "Reversing the idea that "
        ]
        
    def invert_assumption(self, assumption: str, inversion_type: Optional[str] = None) -> str:
        """
        Invert an assumption using specified or automatic inversion type.
        
        Args:
            assumption: The assumption to invert
            inversion_type: Optional type of inversion to apply (direct, qualitative, 
                           relational, hierarchical, concepts, temporal, contextual)
            
        Returns:
            str: The inverted assumption
        """
        import re
        
        # Clean the assumption text
        assumption = assumption.strip()
        
        # If specific inversion type is requested
        if inversion_type and inversion_type in self.inversion_patterns:
            patterns = self.inversion_patterns[inversion_type]
            
            # Try direct pattern replacement for this type
            for pattern, replacement in patterns:
                if re.search(r'\b' + re.escape(pattern) + r'\b', assumption, re.IGNORECASE):
                    return re.sub(r'\b' + re.escape(pattern) + r'\b', replacement, assumption, flags=re.IGNORECASE)
        
        else:
            # Try all pattern types in order of specificity
            for pattern_type in ["relational", "hierarchical", "qualitative", "concepts", 
                                "temporal", "contextual", "direct"]:
                patterns = self.inversion_patterns[pattern_type]
                
                for pattern, replacement in patterns:
                    if re.search(r'\b' + re.escape(pattern) + r'\b', assumption, re.IGNORECASE):
                        return re.sub(r'\b' + re.escape(pattern) + r'\b', replacement, assumption, flags=re.IGNORECASE)
        
        # If no direct pattern match, try structural inversions
        
        # "X is Y" -> "X is not Y"
        is_pattern = re.match(r'^(.+?)\s+is\s+(.+)$', assumption, re.IGNORECASE)
        if is_pattern:
            subject, predicate = is_pattern.groups()
            # Check if it's already negated
            if re.search(r'\bnot\b', predicate, re.IGNORECASE):
                # Remove the negation
                new_predicate = re.sub(r'\bnot\b\s*', '', predicate, flags=re.IGNORECASE)
                return f"{subject} is {new_predicate}"
            else:
                return f"{subject} is not {predicate}"
        
        # "X are Y" -> "X are not Y"
        are_pattern = re.match(r'^(.+?)\s+are\s+(.+)$', assumption, re.IGNORECASE)
        if are_pattern:
            subject, predicate = are_pattern.groups()
            # Check if it's already negated
            if re.search(r'\bnot\b', predicate, re.IGNORECASE):
                # Remove the negation
                new_predicate = re.sub(r'\bnot\b\s*', '', predicate, flags=re.IGNORECASE)
                return f"{subject} are {new_predicate}"
            else:
                return f"{subject} are not {predicate}"
        
        # If none of the above work, try knowledge-based negation
        
        # Common knowledge patterns
        # "X requires Y" -> "X does not require Y"
        requires_pattern = re.match(r'^(.+?)\s+requires?\s+(.+)$', assumption, re.IGNORECASE)
        if requires_pattern:
            subject, object = requires_pattern.groups()
            return f"{subject} does not require {object}"
        
        # "X leads to Y" -> "X does not lead to Y"
        leads_pattern = re.match(r'^(.+?)\s+leads\s+to\s+(.+)$', assumption, re.IGNORECASE)
        if leads_pattern:
            subject, object = leads_pattern.groups()
            return f"{subject} does not lead to {object}"
            
        # If no pattern matches at all, use a random negation prefix
        import random
        prefix = random.choice(self.negation_prefixes)
        # Ensure the assumption starts with lowercase after the prefix
        if assumption and assumption[0].isupper():
            assumption_text = assumption[0].lower() + assumption[1:]
        else:
            assumption_text = assumption
            
        return prefix + assumption_text
    
    async def generate_inversions(self, assumptions: List[str], domain: str = "") -> Dict[str, Any]:
        """
        Generate comprehensive inversions for a list of assumptions.
        
        Args:
            assumptions: List of assumptions to invert
            domain: Optional domain context for more intelligent inversions
            
        Returns:
            Dict[str, Any]: Dictionary containing:
                - direct_inversions: List of (assumption, inversion) pairs using direct inversion
                - dimensional_inversions: List of (assumption, inversion) pairs using dimensional inversion
                - hierarchical_inversions: List of (assumption, inversion) pairs using hierarchical inversion
                - relational_inversions: List of (assumption, inversion) pairs using relational inversion
                - contextual_inversions: List of (assumption, inversion) pairs using contextual inversion
                - emergent_possibilities: List of novel concepts that emerge from the inversions
                - coherent_framework: Description of an alternative framework where the inversions are valid
        """
        # For simpler cases or when API is not needed, use rule-based inversions
        if len(assumptions) <= 3 or not domain:
            return self._generate_rule_based_inversions(assumptions)
        
        # For more complex cases, use Claude to generate comprehensive inversions
        return await self._generate_api_based_inversions(assumptions, domain)
    
    def _generate_rule_based_inversions(self, assumptions: List[str]) -> Dict[str, Any]:
        """
        Generate rule-based inversions for a list of assumptions without using the API.
        
        Args:
            assumptions: List of assumptions to invert
            
        Returns:
            Dict[str, Any]: Dictionary of different types of inversions
        """
        result = {
            "direct_inversions": [],
            "dimensional_inversions": [],
            "hierarchical_inversions": [],
            "relational_inversions": [],
            "contextual_inversions": [],
            "emergent_possibilities": [],
            "coherent_framework": "A framework where conventional assumptions are systematically inverted, creating space for exploration beyond traditional thinking patterns."
        }
        
        for assumption in assumptions:
            # Generate different types of inversions
            direct = self.invert_assumption(assumption, "direct")
            result["direct_inversions"].append((assumption, direct))
            
            # Generate other inversion types if possible
            for inversion_type in ["qualitative", "relational", "hierarchical", "concepts", "temporal", "contextual"]:
                inversion = self.invert_assumption(assumption, inversion_type)
                # Only add if it's different from the direct inversion
                if inversion != direct:
                    key = f"{inversion_type}_inversions"
                    if key not in result:
                        if inversion_type == "qualitative":
                            key = "dimensional_inversions"
                        elif inversion_type == "concepts" or inversion_type == "temporal":
                            key = "contextual_inversions"
                    
                    result[key].append((assumption, inversion))
        
        # Generate emergent possibilities based on combined inversions
        if len(assumptions) >= 2:
            # Take a pair of inversions and combine them
            for i in range(min(len(result["direct_inversions"]), 3)):
                inversion1 = result["direct_inversions"][i][1]
                
                # Find a different inversion type if available
                if result["relational_inversions"] and i < len(result["relational_inversions"]):
                    inversion2 = result["relational_inversions"][i][1]
                elif result["dimensional_inversions"] and i < len(result["dimensional_inversions"]):
                    inversion2 = result["dimensional_inversions"][i][1]
                elif result["hierarchical_inversions"] and i < len(result["hierarchical_inversions"]):
                    inversion2 = result["hierarchical_inversions"][i][1]
                elif i+1 < len(result["direct_inversions"]):
                    inversion2 = result["direct_inversions"][i+1][1]
                else:
                    continue
                
                # Create an emergent possibility by combining two inversions
                possibility = f"A system where {inversion1.lower()} while simultaneously {inversion2.lower()}, leading to entirely new solution spaces."
                result["emergent_possibilities"].append(possibility)
        
        return result
    
    async def _generate_api_based_inversions(self, assumptions: List[str], domain: str) -> Dict[str, Any]:
        """
        Generate comprehensive inversions using the Claude API.
        
        Args:
            assumptions: List of assumptions to invert
            domain: Domain context for more intelligent inversions
            
        Returns:
            Dict[str, Any]: Comprehensive inversion results
        """
        # Format assumptions for the prompt context
        assumptions_text = "\n".join([f"{i+1}. {assumption}" for i, assumption in enumerate(assumptions)])
        
        # Use the prompt_loader to get the prompt from the file system
        from ..prompt_management.prompt_loader import PromptLoader
        prompt_loader = PromptLoader()
        
        # Render the prompt template with context
        prompt = prompt_loader.render_prompt(
            "disruptor_inversion",
            {
                "domain": domain,
                "assumptions": assumptions_text
            }
        )
        
        if not prompt:
            # Fallback in case prompt loading fails
            raise ValueError(f"Failed to load disruptor_inversion prompt template")
        
        # Generate thinking
        thinking_step = await self.claude_client.generate_thinking(
            prompt=prompt,
            thinking_budget=16000,
            max_tokens=20000  # Ensure max_tokens > thinking_budget
        )
        
        # Extract structured results from thinking
        result = self._extract_inversion_results(thinking_step.reasoning_process, assumptions)
        
        # Include original thinking process for reference
        result["thinking_process"] = thinking_step.reasoning_process
        
        return result
    
    def _extract_inversion_results(self, thinking_text: str, original_assumptions: List[str]) -> Dict[str, Any]:
        """
        Extract structured inversion results from thinking text.
        
        Args:
            thinking_text: The thinking text to extract from
            original_assumptions: The original list of assumptions
            
        Returns:
            Dict[str, Any]: Structured inversion results
        """
        import re
        result = {
            "direct_inversions": [],
            "dimensional_inversions": [],
            "hierarchical_inversions": [],
            "relational_inversions": [],
            "contextual_inversions": [],
            "emergent_possibilities": [],
            "coherent_framework": "",
            "breakthrough_implications": []
        }
        
        # Extract inverted assumptions
        inverted_section = re.search(r'<inverted_assumptions>(.*?)</inverted_assumptions>', 
                                    thinking_text, re.DOTALL)
        
        if inverted_section:
            inverted_text = inverted_section.group(1).strip()
            
            # Try to match the inversions to original assumptions
            for i, assumption in enumerate(original_assumptions):
                # Look for inversions that reference this assumption
                for line in inverted_text.split('\n'):
                    if line.strip() and (f"{i+1}." in line[:5] or assumption[:20] in line or 
                                        any(word in line.lower() for word in assumption.lower().split()[:3])):
                        # Extract the inversion part
                        inversion_match = re.search(r'[→:]\s*["\'"]?([^"\'"\n]+)["\'"]?', line)
                        if inversion_match:
                            inversion = inversion_match.group(1).strip()
                            result["direct_inversions"].append((assumption, inversion))
                            break
                
                # If we couldn't find a match, use our rule-based approach
                if i >= len(result["direct_inversions"]):
                    direct = self.invert_assumption(assumption, "direct")
                    result["direct_inversions"].append((assumption, direct))
        
        # Populate other inversion types
        for inversion_type in ["Dimensional", "Hierarchical", "Relational", "Contextual"]:
            section_pattern = f'{inversion_type} Inversion:'
            section_match = re.search(f'{re.escape(section_pattern)}(.*?)(?=\\d+\\.|\<\/inversion_analysis\>)', 
                                    thinking_text, re.DOTALL)
            
            if section_match:
                section_text = section_match.group(1).strip()
                
                # Extract example inversions
                examples = re.findall(r'(?:Example|For example):[^\n]*\n\s*(.+?)(?=\n\n|\n\s*-|\Z)', 
                                    section_text, re.DOTALL)
                
                result_key = f"{inversion_type.lower()}_inversions"
                
                for example in examples:
                    # Try to match to an original assumption
                    closest_match = None
                    highest_match_count = 0
                    
                    for assumption in original_assumptions:
                        # Count matching significant words
                        assumption_words = set(re.findall(r'\b\w{4,}\b', assumption.lower()))
                        example_words = set(re.findall(r'\b\w{4,}\b', example.lower()))
                        match_count = len(assumption_words.intersection(example_words))
                        
                        if match_count > highest_match_count:
                            highest_match_count = match_count
                            closest_match = assumption
                    
                    if closest_match and highest_match_count >= 1:
                        # Extract potential inversion from the example
                        inversion_parts = example.split(" -> ")
                        if len(inversion_parts) > 1:
                            inversion = inversion_parts[1].strip()
                        else:
                            inversion = example.strip()
                            
                        # Add to appropriate category
                        result[result_key].append((closest_match, inversion))
        
        # Extract emergent possibilities
        emergent_section = re.search(r'<emergent_possibilities>(.*?)</emergent_possibilities>', 
                                    thinking_text, re.DOTALL)
        
        if emergent_section:
            emergent_text = emergent_section.group(1).strip()
            
            # Extract numbered or bulleted items
            possibilities = re.findall(r'(?:\d+\.\s*|\*\s*|\-\s*)(.*?)(?=\n\s*\d+\.|\n\s*\*|\n\s*\-|\Z)', 
                                    emergent_text, re.DOTALL)
            
            for possibility in possibilities:
                clean_possibility = possibility.strip()
                if clean_possibility:
                    result["emergent_possibilities"].append(clean_possibility)
        
        # Extract coherent framework
        framework_section = re.search(r'<coherent_framework>(.*?)</coherent_framework>', 
                                    thinking_text, re.DOTALL)
        
        if framework_section:
            result["coherent_framework"] = framework_section.group(1).strip()
        else:
            # Fallback: look for "Coherence Development" section
            coherence_section = re.search(r'Coherence Development:(.*?)(?=\d+\.|\<\/inversion_analysis\>)', 
                                        thinking_text, re.DOTALL)
            if coherence_section:
                result["coherent_framework"] = coherence_section.group(1).strip()
        
        # Extract breakthrough implications
        breakthrough_section = re.search(r'<breakthrough_implications>(.*?)</breakthrough_implications>', 
                                        thinking_text, re.DOTALL)
        
        if breakthrough_section:
            breakthrough_text = breakthrough_section.group(1).strip()
            
            # Extract numbered or bulleted items
            implications = re.findall(r'(?:\d+\.\s*|\*\s*|\-\s*)(.*?)(?=\n\s*\d+\.|\n\s*\*|\n\s*\-|\Z)', 
                                    breakthrough_text, re.DOTALL)
            
            for implication in implications:
                clean_implication = implication.strip()
                if clean_implication:
                    result["breakthrough_implications"].append(clean_implication)
        
        # Fallback for emergent possibilities if none found
        if not result["emergent_possibilities"] and len(result["direct_inversions"]) >= 2:
            # Create some basic emergent possibilities
            inv1 = result["direct_inversions"][0][1]
            inv2 = result["direct_inversions"][1][1]
            
            result["emergent_possibilities"] = [
                f"A paradigm where {inv1.lower()} and {inv2.lower()} coexist, creating a novel approach to the domain.",
                f"A system that leverages both {inv1.lower()} and conventional thinking to create hybrid solutions.",
                f"A framework that transitions between {inv1.lower()} and {inv2.lower()} depending on context."
            ]
        
        # Fallback for coherent framework if none found
        if not result["coherent_framework"]:
            inversions = [inv for _, inv in result["direct_inversions"][:3]]
            result["coherent_framework"] = f"A coherent alternative framework where {', '.join(inversions)} work together to create a new paradigm for approaching problems in this domain."
        
        return result
        
    def get_inversion_patterns(self) -> Dict[str, List[Tuple[str, str]]]:
        """
        Get the current inversion patterns dictionary.
        
        Returns:
            Dict[str, List[Tuple[str, str]]]: Dictionary of inversion patterns by type
        """
        return self.inversion_patterns
    
    def add_inversion_pattern(self, pattern_type: str, pattern: str, replacement: str) -> bool:
        """
        Add a new inversion pattern to the patterns dictionary.
        
        Args:
            pattern_type: Type of pattern (direct, qualitative, relational, etc.)
            pattern: The pattern to match
            replacement: The replacement text
            
        Returns:
            bool: True if added successfully, False otherwise
        """
        if pattern_type not in self.inversion_patterns:
            self.inversion_patterns[pattern_type] = []
            
        # Check if pattern already exists
        for existing_pattern, _ in self.inversion_patterns[pattern_type]:
            if existing_pattern == pattern:
                return False
                
        # Add the new pattern
        self.inversion_patterns[pattern_type].append((pattern, replacement))
        return True


@uses_prompt("disruptor_paradox_generation")
class ParadoxGenerator:
    """
    Creates productive contradictions that force new thinking.
    
    This class implements the disruptor_paradox_generation.txt prompt to generate
    productive paradoxes that force contradictory concepts to coexist, leading to new insights.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Paradox Generator.
        
        Args:
            api_key: Optional API key for Claude. If not provided, will try to get from config.
        """
        config = get_config()
        self.api_key = api_key or config["api"]["anthropic_api_key"]
        self.claude_client = ClaudeAPIClient(self.api_key)
    
    async def generate_paradox(self, inversion_pairs: List[Tuple[str, str]], domain: str) -> str:
        """
        Generate a productive paradox from inversion pairs.
        
        Args:
            inversion_pairs: Pairs of (assumption, inversion)
            domain: The domain of the problem
            
        Returns:
            str: Generated paradox
        """
        # Select a random pair of inversions
        import random
        selected_pairs = random.sample(inversion_pairs, min(2, len(inversion_pairs)))
        
        # Create inversion text for the prompt context
        pairs_text = ""
        for i, (assumption, inversion) in enumerate(selected_pairs):
            pairs_text += f"{i+1}. Conventional assumption: {assumption}\n"
            pairs_text += f"   Inverted assumption: {inversion}\n\n"
        
        # Construct the problem statement from the inversions
        problem_statement = f"Exploring how contradictory assumptions can coexist in {domain}."
        
        # Use the prompt_loader to get the prompt from the file system
        from ..prompt_management.prompt_loader import PromptLoader
        prompt_loader = PromptLoader()
        
        # Render the prompt template with context
        prompt = prompt_loader.render_prompt(
            "disruptor_paradox_generation",
            {
                "domain": domain,
                "problem_statement": problem_statement + "\n\n" + pairs_text
            }
        )
        
        if not prompt:
            # Fallback in case prompt loading fails
            raise ValueError(f"Failed to load disruptor_paradox_generation prompt template")
        
        # Generate thinking
        thinking_step = await self.claude_client.generate_thinking(
            prompt=prompt,
            thinking_budget=8000,
            max_tokens=9000  # Ensure max_tokens > thinking_budget
        )
        
        # Extract paradox from thinking
        paradox = self._extract_paradox(thinking_step.reasoning_process)
        
        return paradox
    
    def _extract_paradox(self, thinking_text: str) -> str:
        """
        Extract a paradox from thinking text.
        
        Args:
            thinking_text: The thinking text to extract from
            
        Returns:
            str: Extracted paradox
        """
        # Look for paradox indicators
        paradox_indicators = [
            "Paradox:", "Paradoxical principle:", "Productive paradox:",
            "Paradoxical statement:", "The paradox is:"
        ]
        
        for indicator in paradox_indicators:
            if indicator in thinking_text:
                # Extract text after the indicator
                start_idx = thinking_text.find(indicator) + len(indicator)
                end_idx = thinking_text.find("\n\n", start_idx)
                if end_idx == -1:
                    end_idx = len(thinking_text)
                
                paradox = thinking_text[start_idx:end_idx].strip()
                if paradox:
                    return paradox
        
        # If no structured indicator, look for quotation marks
        import re
        quotes = re.findall(r'"([^"]*)"', thinking_text)
        if quotes:
            return quotes[0]
        
        # Fallback: return the last paragraph
        paragraphs = thinking_text.split("\n\n")
        if paragraphs:
            return paragraphs[-1].strip()
        
        return "No paradox found"


@uses_prompt("disruptor_paradox_generation", dependencies=["disruptor_assumption_detection", "disruptor_inversion"])
class DisruptorModule:
    """
    Creates conceptual superpositions by forcing paradoxical states and challenging assumptions.
    
    This class coordinates the detection of assumptions, creation of inversions, and generation
    of paradoxes to disrupt conventional thinking and create novel solution spaces.
    
    Depends on prompts: disruptor_assumption_detection.txt, disruptor_inversion.txt
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Disruptor Module.
        
        Args:
            api_key: Optional API key for Claude. If not provided, will try to get from config.
        """
        config = get_config()
        self.api_key = api_key or config["api"]["anthropic_api_key"]
        
        # Initialize components
        self.assumption_detector = AssumptionDetector(self.api_key)
        self.inversion_engine = InversionEngine()
        self.paradox_generator = ParadoxGenerator(self.api_key)
        self.claude_client = ClaudeAPIClient(self.api_key)
        self.superposition_engine = SuperpositionEngine()
    
    async def disrupt(self, problem_statement: str, domain: str) -> Dict[str, Any]:
        """
        Disrupt a problem by challenging assumptions and generating paradoxes.
        
        Args:
            problem_statement: The problem statement to disrupt
            domain: The domain of the problem
            
        Returns:
            Dict[str, Any]: Results of the disruption including assumptions, inversions, paradoxes, and ideas
        """
        # Step 1: Detect assumptions
        assumptions_data = await self.assumption_detector.detect_assumptions(problem_statement, domain)
        
        # Extract the core assumptions as a list
        if "core_assumptions" in assumptions_data:
            # Extract assumptions from the structured text
            import re
            assumptions_list = re.findall(r'\d+\.\s+(.*?)(?=\d+\.|\n\n|$)', 
                                        assumptions_data["core_assumptions"], re.DOTALL)
            assumptions_list = [a.strip() for a in assumptions_list if a.strip()]
            
            # If we couldn't extract from numbered list, try to split by newlines
            if not assumptions_list:
                assumptions_list = [line.strip() for line in assumptions_data["core_assumptions"].split("\n") 
                                  if line.strip() and not line.strip().startswith("Rank")]
            
            # Add additional assumptions if any
            if "additional_assumptions" in assumptions_data:
                assumptions_list.extend(assumptions_data["additional_assumptions"])
        else:
            # Fallback to empty list
            assumptions_list = []
            
        # Ensure we have at least some assumptions to work with
        if not assumptions_list:
            # Create generic assumptions for the domain
            assumptions_list = [
                f"{domain} requires conventional approaches",
                f"{domain} processes are fundamentally linear",
                f"Progress in {domain} is incremental rather than revolutionary",
                f"Expertise in {domain} comes from established educational paths"
            ]
            
        # Step 2: Generate comprehensive inversions
        inversions_data = await self.inversion_engine.generate_inversions(assumptions_list, domain)
        
        # Extract direct inversion pairs for paradox generation
        direct_inversions = inversions_data.get("direct_inversions", [])
        
        # Step 3: Generate paradoxes using the direct inversions
        paradox = await self.paradox_generator.generate_paradox(direct_inversions, domain)
        
        # Step 4: Generate disruptive idea based on paradox and all inversion types
        idea = await self._generate_disruptive_idea(
            problem_statement=problem_statement, 
            paradox=paradox, 
            inversion_pairs=direct_inversions,
            inversions_data=inversions_data,
            domain=domain
        )
        
        # Create comprehensive results
        results = {
            "assumptions": assumptions_data,
            "inversions": inversions_data,
            "paradox": paradox,
            "idea": idea,
            "emergent_possibilities": inversions_data.get("emergent_possibilities", []),
            "coherent_framework": inversions_data.get("coherent_framework", "")
        }
        
        return results
    
    async def _generate_disruptive_idea(self, problem_statement: str, paradox: str, 
                                  inversion_pairs: List[Tuple[str, str]], 
                                  inversions_data: Dict[str, Any],
                                  domain: str) -> CreativeIdea:
        """
        Generate a disruptive idea based on paradoxes and comprehensive inversions.
        
        Args:
            problem_statement: The problem statement
            paradox: The generated paradox
            inversion_pairs: Pairs of (assumption, inversion) from direct inversions
            inversions_data: Comprehensive inversion data including multiple inversion types
            domain: The domain of the problem
            
        Returns:
            CreativeIdea: The generated disruptive idea with associated metadata
        """
        # Compile the different inversion types for a more comprehensive prompt
        direct_inversions = inversions_data.get("direct_inversions", inversion_pairs)
        dimensional_inversions = inversions_data.get("dimensional_inversions", [])
        hierarchical_inversions = inversions_data.get("hierarchical_inversions", [])
        relational_inversions = inversions_data.get("relational_inversions", [])
        contextual_inversions = inversions_data.get("contextual_inversions", [])
        emergent_possibilities = inversions_data.get("emergent_possibilities", [])
        coherent_framework = inversions_data.get("coherent_framework", "")
        
        # Create formatted texts for each inversion type
        direct_text = self._format_inversion_pairs(direct_inversions, "Direct Inversions")
        dimensional_text = self._format_inversion_pairs(dimensional_inversions, "Dimensional Inversions")
        hierarchical_text = self._format_inversion_pairs(hierarchical_inversions, "Hierarchical Inversions")
        relational_text = self._format_inversion_pairs(relational_inversions, "Relational Inversions")
        contextual_text = self._format_inversion_pairs(contextual_inversions, "Contextual Inversions")
        
        # Format emergent possibilities if available
        emergent_text = ""
        if emergent_possibilities:
            emergent_text = "Emergent Possibilities from Inversions:\n"
            for i, possibility in enumerate(emergent_possibilities, 1):
                emergent_text += f"{i}. {possibility}\n"
        
        # Format the coherent framework
        framework_text = ""
        if coherent_framework:
            framework_text = f"Coherent Alternative Framework:\n{coherent_framework}\n\n"
        
        # Use the prompt_loader to get the prompt template
        from ..prompt_management.prompt_loader import PromptLoader
        prompt_loader = PromptLoader()
        
        # Format all inversions into a single text block
        inversions_text = f"{direct_text}\n\n{dimensional_text}\n\n{hierarchical_text}\n\n{relational_text}\n\n{contextual_text}"
        
        # Prepare context for template rendering
        context = {
            "problem_statement": problem_statement,
            "domain": domain,
            "paradox": paradox,
            "inversions": inversions_text,
            "emergent_possibilities": emergent_text,
            "coherent_framework": framework_text
        }
        
        # Render the prompt template
        prompt = prompt_loader.render_prompt("disruptor_idea_generation", context)
        
        if not prompt:
            # Fallback in case prompt loading fails
            raise ValueError(f"Failed to load disruptor_idea_generation prompt template")
        
        # Generate thinking using Claude's extended thinking capabilities
        thinking_step = await self.claude_client.generate_thinking(
            prompt=prompt,
            thinking_budget=16000,  # Substantial thinking budget for complex creative process
            max_tokens=20000  # Ensure max_tokens > thinking_budget
        )
        
        # Extract idea description and other elements from thinking
        idea_components = self._extract_comprehensive_idea(thinking_step.reasoning_process)
        
        # Create a more nuanced shock profile based on the idea components
        shock_profile = self._calculate_shock_profile(
            idea_components, 
            domain, 
            direct_inversions, 
            dimensional_inversions
        )
        
        # Extract related concepts from the thinking process
        related_concepts = self._extract_related_concepts(
            thinking_step.reasoning_process,
            domain
        )
        
        # Create a comprehensive disruptive idea
        disruptive_idea = CreativeIdea(
            id=uuid.uuid4(),
            title=idea_components.get("title", f"Disruptive Idea for {domain}"),
            description=idea_components.get("description", ""),
            summary=idea_components.get("summary", ""),
            generative_framework="disruptor",
            domain=domain,
            impossibility_elements=[pair[1] for pair in direct_inversions[:3]],  # Use direct inversions
            contradiction_elements=[paradox] + [pair[1] for pair in hierarchical_inversions[:2] if hierarchical_inversions],
            related_concepts=related_concepts,
            shock_metrics=shock_profile
        )
        
        return disruptive_idea
    
    def _format_inversion_pairs(self, pairs: List[Tuple[str, str]], section_title: str) -> str:
        """
        Format inversion pairs for inclusion in a prompt.
        
        Args:
            pairs: List of (assumption, inversion) pairs
            section_title: Title for this section of inversions
            
        Returns:
            str: Formatted text for the inversions
        """
        if not pairs:
            return ""
            
        result = f"{section_title}:\n"
        for i, (assumption, inversion) in enumerate(pairs, 1):
            result += f"{i}. Conventional: {assumption} ↔ Inverted: {inversion}\n"
        
        return result
    
    def _extract_comprehensive_idea(self, thinking_text: str) -> Dict[str, str]:
        """
        Extract comprehensive idea components from thinking text.
        
        Args:
            thinking_text: The thinking text to extract from
            
        Returns:
            Dict[str, str]: Components of the idea including title, description, 
                          summary, and additional elements
        """
        import re
        result = {}
        
        # Look for title markers
        title_patterns = [
            r'<title>(.*?)</title>',
            r'Title:\s*(.*?)(?:\n\n|\n(?=Description:|Summary:))',
            r'# (.*?)(?:\n\n|\n(?=##))'
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, thinking_text, re.DOTALL)
            if match:
                result["title"] = match.group(1).strip()
                break
                
        # If no title found, look for key phrases that might indicate a title
        if "title" not in result:
            title_phrases = ["I call this", "This idea is called", "Introducing the"]
            for phrase in title_phrases:
                if phrase in thinking_text:
                    # Extract the sentence containing the phrase
                    sentences = re.split(r'(?<=[.!?])\s+', thinking_text)
                    for sentence in sentences:
                        if phrase in sentence:
                            # Extract what comes after the phrase
                            title_part = sentence.split(phrase)[1].strip()
                            # Clean up punctuation and quotes
                            title_part = re.sub(r'^[:"\']*|[:"\',.]*$', '', title_part)
                            if title_part:
                                result["title"] = title_part
                                break
                    if "title" in result:
                        break
        
        # Description patterns
        description_patterns = [
            r'<description>(.*?)</description>',
            r'Description:\s*(.*?)(?:\n\n|\n(?=Summary:|Implementation:|Applications:))',
            r'(?:^|\n\n)(?!Title:)(?!Summary:)(.*?)(?:\n\n(?=Summary:|Implementation:|Applications:)|$)'
        ]
        
        for pattern in description_patterns:
            match = re.search(pattern, thinking_text, re.DOTALL)
            if match:
                result["description"] = match.group(1).strip()
                break
        
        # If no structured description, use conclusion markers
        if "description" not in result:
            conclusion_markers = [
                "In conclusion", "Therefore", "Thus", "The final idea", 
                "The disruptive concept", "The breakthrough idea", 
                "This revolutionary approach", "The innovative solution"
            ]
            
            for marker in conclusion_markers:
                if marker in thinking_text:
                    # Find the marker and extract text until the next paragraph break
                    start_idx = thinking_text.find(marker)
                    end_idx = thinking_text.find("\n\n", start_idx)
                    if end_idx == -1:
                        end_idx = len(thinking_text)
                    
                    # Extract and clean the text
                    description = thinking_text[start_idx:end_idx].strip()
                    
                    # Remove the marker itself if at the beginning
                    if description.startswith(marker):
                        description = description[len(marker):].strip()
                        # Remove any leading colon
                        if description.startswith(":"):
                            description = description[1:].strip()
                    
                    result["description"] = description
                    break
        
        # If still no description, use the last significant paragraph
        if "description" not in result:
            paragraphs = thinking_text.split("\n\n")
            significant_paragraphs = [p for p in paragraphs if len(p) > 100]
            if significant_paragraphs:
                result["description"] = significant_paragraphs[-1].strip()
            else:
                result["description"] = thinking_text[-500:].strip()  # Last 500 characters
        
        # Summary patterns
        summary_patterns = [
            r'<summary>(.*?)</summary>',
            r'Summary:\s*(.*?)(?:\n\n|\n(?=Implementation:|Applications:))',
            r'In summary[,:]\s*(.*?)(?:\n\n|$)'
        ]
        
        for pattern in summary_patterns:
            match = re.search(pattern, thinking_text, re.DOTALL)
            if match:
                result["summary"] = match.group(1).strip()
                break
        
        # Additional elements that might be useful
        for element in ["applications", "implementation", "implications", "benefits", "challenges"]:
            pattern = rf'<{element}>(.*?)</{element}>'
            match = re.search(pattern, thinking_text, re.DOTALL)
            if not match:
                pattern = rf'{element.capitalize()}:\s*(.*?)(?:\n\n|\n(?=[A-Z][a-z]+:))'
                match = re.search(pattern, thinking_text, re.DOTALL)
            
            if match:
                result[element] = match.group(1).strip()
        
        return result
    
    def _calculate_shock_profile(self, 
                              idea_components: Dict[str, str], 
                              domain: str,
                              direct_inversions: List[Tuple[str, str]],
                              dimensional_inversions: List[Tuple[str, str]]) -> ShockProfile:
        """
        Calculate a nuanced shock profile based on idea components and inversions.
        
        Args:
            idea_components: Components of the idea extracted from thinking
            domain: The domain of the problem
            direct_inversions: Direct inversion pairs
            dimensional_inversions: Dimensional inversion pairs
            
        Returns:
            ShockProfile: A shock profile with calculated metrics
        """
        # Start with base values
        novelty_score = 0.8
        contradiction_score = 0.85
        impossibility_score = 0.75
        utility_potential = 0.6
        expert_rejection_probability = 0.8
        
        # Refine based on the number and types of inversions
        if len(direct_inversions) >= 5:
            impossibility_score += 0.05
            contradiction_score += 0.05
            
        # Dimensional inversions indicate deeper conceptual shifts
        if dimensional_inversions:
            novelty_score += 0.05
            expert_rejection_probability += 0.05
            
        # Analyze the description for indicators of high shock value
        description = idea_components.get("description", "")
        
        # Check for radical terminology
        radical_terms = [
            "paradigm shift", "revolutionary", "breakthrough", "impossible", 
            "unprecedented", "fundamental rethinking", "transformative",
            "violates", "contradicts", "defies", "reverses", "transcends"
        ]
        
        term_count = sum(1 for term in radical_terms if term.lower() in description.lower())
        
        # Adjust novelty based on radical terminology
        if term_count >= 3:
            novelty_score += 0.05
            expert_rejection_probability += 0.05
        
        # Domains with more rigid conventions tend to have higher shock values
        conservative_domains = ["physics", "mathematics", "medicine", "law", "finance"]
        if domain.lower() in conservative_domains:
            contradiction_score += 0.05
            expert_rejection_probability += 0.05
        
        # Adjust utility based on presence of implementation details
        if "implementation" in idea_components or "applications" in idea_components:
            utility_potential += 0.1
        
        # Calculate composite shock value
        # Weight impossibility and contradiction more heavily than utility
        composite_shock_value = (
            novelty_score * 0.25 +
            contradiction_score * 0.25 +
            impossibility_score * 0.25 +
            (1 - utility_potential) * 0.1 +  # Lower utility can increase shock
            expert_rejection_probability * 0.15
        )
        
        # Ensure values are capped at 1.0
        return ShockProfile(
            novelty_score=min(novelty_score, 1.0),
            contradiction_score=min(contradiction_score, 1.0),
            impossibility_score=min(impossibility_score, 1.0),
            utility_potential=min(utility_potential, 1.0),
            expert_rejection_probability=min(expert_rejection_probability, 1.0),
            composite_shock_value=min(composite_shock_value, 1.0)
        )
    
    def _extract_related_concepts(self, thinking_text: str, domain: str) -> List[Concept]:
        """
        Extract related concepts from thinking text to create a concept network.
        
        Args:
            thinking_text: The thinking text to extract from
            domain: The domain for context
            
        Returns:
            List[Concept]: List of related concepts
        """
        import re
        concepts = []
        
        # Look for explicit concept lists
        concept_patterns = [
            r'<related_concepts>(.*?)</related_concepts>',
            r'Related concepts:\s*(.*?)(?:\n\n|\n(?=[A-Z][a-z]+:))',
            r'Key concepts:\s*(.*?)(?:\n\n|\n(?=[A-Z][a-z]+:))'
        ]
        
        found_concepts = False
        for pattern in concept_patterns:
            match = re.search(pattern, thinking_text, re.DOTALL)
            if match:
                concept_text = match.group(1).strip()
                # Extract bulleted or numbered list items
                concept_items = re.findall(r'(?:\d+\.|\*|\-)\s*(.*?)(?=\n(?:\d+\.|\*|\-)|\n\n|$)', 
                                        concept_text, re.DOTALL)
                
                if not concept_items:
                    # Try splitting by lines
                    concept_items = [line.strip() for line in concept_text.split('\n') 
                                   if line.strip() and not line.strip().startswith('#')]
                
                for item in concept_items:
                    # Extract the concept name and state if present
                    concept_parts = re.split(r'[-–:]', item, 1)
                    concept_name = concept_parts[0].strip()
                    concept_state = concept_parts[1].strip() if len(concept_parts) > 1 else "potential"
                    
                    if concept_name:
                        concept_id = uuid.uuid4()
                        concepts.append(Concept(
                            id=concept_id,
                            name=concept_name,
                            domain=domain,
                            state=ConceptState(
                                id=uuid.uuid4(),
                                concept_id=concept_id,
                                state_type=concept_state,
                                probability=0.8
                            )
                        ))
                
                found_concepts = True
                break
        
        # If no explicit concepts were found, extract significant terms
        if not found_concepts:
            # Extract domain-specific significant noun phrases
            description = re.sub(r'<.*?>', '', thinking_text)  # Remove XML tags
            sentences = re.split(r'(?<=[.!?])\s+', description)
            
            # Look for capitalized technical terms and phrases
            technical_terms = set()
            term_pattern = r'\b([A-Z][a-z]+(?:\s+[a-z]+)*|[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b'
            for sentence in sentences:
                terms = re.findall(term_pattern, sentence)
                for term in terms:
                    if len(term) > 3 and term.lower() not in ["this", "that", "these", "those", "their"]:
                        technical_terms.add(term)
            
            # Add significant technical terms as concepts
            for term in list(technical_terms)[:5]:  # Limit to top 5
                concept_id = uuid.uuid4()
                concepts.append(Concept(
                    id=concept_id,
                    name=term,
                    domain=domain,
                    state=ConceptState(
                        id=uuid.uuid4(),
                        concept_id=concept_id,
                        state_type="extracted",
                        probability=0.7
                    )
                ))
        
        return concepts
    
