"""
Integration with Claude 3.7 Extended Thinking capabilities.
"""
import os
import asyncio
from typing import Dict, List, Any, Optional, Union
import json
import anthropic
from ..config import get_config
# Using direct import to break circular dependency
import uuid
import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, UUID4

# Define ThinkingStep and ShockDirective here instead of importing
class ThinkingStep(BaseModel):
    """Represents a single step in Claude's extended thinking process."""
    id: UUID4 = Field(default_factory=uuid.uuid4)
    step_type: str = Field(...)
    reasoning_process: str = Field(...)
    insights_generated: Optional[List[str]] = Field(default_factory=list)
    
class ShockDirective(BaseModel):
    """Directive for controlling the shock value of generated ideas."""
    impossibility_constraints: List[str] = Field(default_factory=list)
    contradiction_requirements: List[str] = Field(default_factory=list)
    shock_threshold: float = Field(0.6)
from ..prompt_management.prompt_loader import PromptLoader


class ClaudeAPIClient:
    """
    Client for interacting with Claude 3.7 API with Extended Thinking capabilities.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Claude API client.
        
        Args:
            api_key: Optional API key. If not provided, will try to get from config.
        """
        config = get_config()
        self.api_key = api_key or config["api"]["anthropic_api_key"]
        if not self.api_key:
            raise ValueError("Anthropic API key is required")
            
        self.model = config["api"]["model"]
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.prompt_loader = PromptLoader()
    
    async def generate_thinking(self, 
                              prompt: str, 
                              thinking_budget: int = 16000,
                              max_tokens: int = 40000) -> ThinkingStep:
        """
        Generate a thinking step using Claude's Extended Thinking capabilities.
        
        Args:
            prompt: The prompt to send to Claude
            thinking_budget: Maximum tokens to use for thinking
            max_tokens: Maximum tokens to generate for the response
            
        Returns:
            ThinkingStep: The thinking step generated
        """
        try:
            # Create the message with extended thinking enabled
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                thinking={
                    "type": "enabled",
                    "budget_tokens": thinking_budget
                },
                system="You are an advanced creative intelligence system called Leela. You generate genuinely shocking, novel outputs that transcend conventional thinking. Think step by step about the problem at hand, focusing on finding ideas that seem impossible or contradictory but might contain hidden value. Your thinking should deliberately violate established patterns and assumptions in the domain.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract thinking from the response
            thinking_text = ""
            insights = []
            token_usage = 0
            
            # Process content blocks
            for content_block in message.content:
                if content_block.type == "thinking":
                    thinking_text = content_block.thinking
                elif content_block.type == "text":
                    # The text content can be used to extract insights
                    insights = self._extract_insights(content_block.text)
            
            # Get token usage
            if hasattr(message, "usage") and hasattr(message.usage, "output_tokens"):
                token_usage = message.usage.output_tokens
            
            # Create a ThinkingStep object
            thinking_step = ThinkingStep(
                framework="extended_thinking",
                reasoning_process=thinking_text,
                insights_generated=insights if insights else self._extract_insights(thinking_text),
                token_usage=token_usage
            )
            
            return thinking_step
            
        except Exception as e:
            raise Exception(f"Error generating thinking: {str(e)}")
    
    async def execute_shock_directive(self, directive: ShockDirective) -> ThinkingStep:
        """
        Execute a shock directive using Claude's Extended Thinking.
        
        Args:
            directive: The shock directive to execute
            
        Returns:
            ThinkingStep: The thinking step generated
        """
        # Construct a prompt from the directive
        prompt = self._construct_directive_prompt(directive)
        
        # Calculate max_tokens to always be greater than thinking_budget
        # Make sure max_tokens is at least thinking_budget + 1000
        max_tokens_value = directive.thinking_budget + 1000
        
        # Generate thinking with the prompt
        return await self.generate_thinking(
            prompt=prompt, 
            thinking_budget=directive.thinking_budget,
            max_tokens=max_tokens_value  # Ensure max_tokens > thinking_budget
        )
    
    def _construct_directive_prompt(self, directive: ShockDirective) -> str:
        """
        Construct a prompt from a shock directive.
        
        Args:
            directive: The shock directive
            
        Returns:
            str: The prompt
        """
        # Try to load a template for the shock framework
        prompt_template = self.prompt_loader.load_prompt(directive.shock_framework.lower())
        
        if prompt_template:
            # Construct context for template rendering
            context = {
                "domain": directive.problem_domain,
                "problem_statement": directive.thinking_instructions,
                "impossibility_constraints": directive.impossibility_constraints,
                "contradiction_requirements": directive.contradiction_requirements,
                "antipattern_instructions": directive.antipattern_instructions,
                "shock_threshold": directive.minimum_shock_threshold,
                "thinking_budget": directive.thinking_budget
            }
            
            # Render the template
            rendered_prompt = self.prompt_loader.render_prompt(
                directive.shock_framework.lower(), context
            )
            
            if rendered_prompt:
                return rendered_prompt
        
        # Fallback to manual construction if template not found or rendering fails
        # Start with the domain information
        prompt = f"# Problem Domain\n{directive.problem_domain}\n\n"
        
        # Add shock framework
        prompt += f"# Creative Framework\n{directive.shock_framework}\n\n"
        
        # Add impossibility constraints
        prompt += "# Impossibility Constraints\n"
        for constraint in directive.impossibility_constraints:
            prompt += f"- {constraint}\n"
        prompt += "\n"
        
        # Add contradiction requirements
        prompt += "# Contradiction Requirements\n"
        for requirement in directive.contradiction_requirements:
            prompt += f"- {requirement}\n"
        prompt += "\n"
        
        # Add antipattern instructions
        prompt += f"# Pattern Violation Instructions\n{directive.antipattern_instructions}\n\n"
        
        # Add thinking instructions
        prompt += f"# Thinking Process\n{directive.thinking_instructions}\n\n"
        
        # Add shock threshold requirement
        prompt += f"# Shock Threshold\nYour ideas must exceed a shock value of {directive.minimum_shock_threshold}. This means they should violate established assumptions and create cognitive dissonance in domain experts.\n\n"
        
        # Final instruction
        prompt += "Think step by step. First, understand the conventional paradigms in this domain. Then identify the fundamental assumptions. Next, systematically invert or violate these assumptions while maintaining internal coherence. Finally, develop a shocking new idea or approach that experts would consider impossible yet contains potential value."
        
        return prompt
    
    def _extract_insights(self, text: str) -> List[str]:
        """
        Extract key insights from text.
        Looks for content in analysis tags or falls back to heuristics.
        
        Args:
            text: The text to extract insights from
            
        Returns:
            List[str]: Extracted insights
        """
        # Look for analysis tags in order of preference
        analysis_tag_pairs = [
            ("<contradiction_analysis>", "</contradiction_analysis>"),
            ("<dialectic_analysis>", "</dialectic_analysis>"),
            ("<ideation_process>", "</ideation_process>"),
            ("<synthesis_process>", "</synthesis_process>"),
            ("<analysis>", "</analysis>")
        ]
        
        for start_tag, end_tag in analysis_tag_pairs:
            analysis_start = text.find(start_tag)
            analysis_end = text.find(end_tag)
            
            if analysis_start != -1 and analysis_end != -1:
                # Extract content between tags
                analysis_start += len(start_tag)
                analysis_text = text[analysis_start:analysis_end].strip()
                
                # Split analysis into paragraphs for insights
                paragraphs = analysis_text.split("\n\n")
                insights = []
                
                for p in paragraphs:
                    p = p.strip()
                    # Skip very short paragraphs
                    if len(p) < 50:
                        continue
                    insights.append(p)
                
                # Return at most 5 key insights
                return insights[:5] if insights else [analysis_text[:500]]
        
        # Fallback to simple extraction based on paragraphs if tags not found
        paragraphs = text.split("\n\n")
        insights = []
        
        # Look for paragraphs that likely contain insights
        for p in paragraphs:
            # Skip very short paragraphs
            if len(p.strip()) < 50:
                continue
                
            # Look for conclusion indicators
            if any(marker in p.lower() for marker in ["therefore", "thus", "conclude", "insight", 
                                                     "implication", "suggests", "reveals",
                                                     "innovative", "breakthrough", "novel"]):
                insights.append(p.strip())
        
        # If no insights found, take the last paragraph as a conclusion
        if not insights and paragraphs:
            insights.append(paragraphs[-1].strip())
            
        return insights


class ExtendedThinkingManager:
    """
    Manager for handling Claude 3.7's Extended Thinking capabilities,
    including multi-turn conversations and tool use.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Extended Thinking Manager.
        
        Args:
            api_key: Optional API key. If not provided, will try to get from config.
        """
        self.api_client = ClaudeAPIClient(api_key)
        self.thinking_history = []
    
    async def multi_step_thinking(self, 
                                prompts: List[str], 
                                thinking_budget: int = 16000,
                                max_tokens: int = 20000) -> List[ThinkingStep]:
        """
        Generate multiple thinking steps in sequence.
        
        Args:
            prompts: List of prompts to send to Claude in sequence
            thinking_budget: Maximum tokens to use for thinking
            max_tokens: Maximum tokens to generate for each response
            
        Returns:
            List[ThinkingStep]: The thinking steps generated
        """
        thinking_steps = []
        
        for prompt in prompts:
            # Generate a thinking step
            thinking_step = await self.api_client.generate_thinking(
                prompt=prompt,
                thinking_budget=thinking_budget,
                max_tokens=max_tokens
            )
            
            # Add to history
            self.thinking_history.append(thinking_step)
            thinking_steps.append(thinking_step)
        
        return thinking_steps
    
    async def dialectic_thinking(self, 
                               prompt: str, 
                               perspectives: List[str],
                               thinking_budget: int = 16000,
                               max_tokens: int = 20000) -> List[ThinkingStep]:
        """
        Generate thinking from multiple perspectives.
        
        Args:
            prompt: The base prompt to send to Claude
            perspectives: List of perspective descriptions for dialectic thinking
            thinking_budget: Maximum tokens to use for thinking
            max_tokens: Maximum tokens to generate for each response
            
        Returns:
            List[ThinkingStep]: The thinking steps generated from different perspectives
        """
        thinking_steps = []
        
        for perspective in perspectives:
            # Construct a perspective-specific prompt
            perspective_prompt = f"{prompt}\n\nApproach this problem from the following perspective:\n{perspective}"
            
            # Generate a thinking step
            thinking_step = await self.api_client.generate_thinking(
                prompt=perspective_prompt,
                thinking_budget=thinking_budget,
                max_tokens=max_tokens
            )
            
            # Add to history
            self.thinking_history.append(thinking_step)
            thinking_steps.append(thinking_step)
        
        return thinking_steps