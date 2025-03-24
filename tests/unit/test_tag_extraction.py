"""
Test tag-based extraction methods across different classes.
"""
import sys
import os
import pytest

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from leela.directed_thinking.claude_api import ClaudeAPIClient
from leela.shock_generation.cognitive_dissonance_amplifier import CognitiveDissonanceAmplifier
from leela.shock_generation.impossibility_enforcer import ImpossibilityEnforcer
from leela.core_processing.explorer import MultiAgentDialecticSystem, TemporalPerspectiveShifter, ExplorerModule


def test_claude_api_extract_insights():
    """Test the _extract_insights method with different tag types."""
    client = ClaudeAPIClient("dummy_key")
    
    # Test with dialectic_analysis tag
    dialectic_text = """Some text before
    <dialectic_analysis>Analysis content here</dialectic_analysis>
    Some text after"""
    assert client._extract_insights(dialectic_text) == "Analysis content here"
    
    # Test with contradiction_analysis tag
    contradiction_text = """Some text before
    <contradiction_analysis>Contradiction content here</contradiction_analysis>
    Some text after"""
    assert client._extract_insights(contradiction_text) == "Contradiction content here"
    
    # Test with ideation_process tag
    ideation_text = """Some text before
    <ideation_process>Ideation content here</ideation_process>
    Some text after"""
    assert client._extract_insights(ideation_text) == "Ideation content here"
    
    # Test with synthesis_process tag
    synthesis_text = """Some text before
    <synthesis_process>Synthesis content here</synthesis_process>
    Some text after"""
    assert client._extract_insights(synthesis_text) == "Synthesis content here"
    
    # Test fallback with : used as marker
    fallback_text = "Thinking: This is thinking content"
    assert client._extract_insights(fallback_text) == "This is thinking content"
    
    # Test fallback with multiple fallback markers
    fallback_text2 = "Some text\nProcess: Process content\nMore text"
    assert client._extract_insights(fallback_text2) == "Process content"


def test_extract_idea_description_methods():
    """Test _extract_idea_description methods across different classes."""
    # Initialize test instances
    cda = CognitiveDissonanceAmplifier("dummy_key")
    ie = ImpossibilityEnforcer("dummy_key")
    mads = MultiAgentDialecticSystem("dummy_key")
    tps = TemporalPerspectiveShifter("dummy_key")
    em = ExplorerModule("dummy_key")
    
    # Create test texts with different tag types
    synthesis_text = """Thinking process...
    <synthesis>Synthesis idea content</synthesis>
    More text..."""
    
    final_idea_text = """Thinking process...
    <final_idea>Final idea content</final_idea>
    More text..."""
    
    revolutionary_text = """Thinking process...
    <revolutionary_idea>Revolutionary idea content</revolutionary_idea>
    More text..."""
    
    idea_text = """Thinking process...
    <idea>General idea content</idea>
    More text..."""
    
    # Test with fallback markers
    fallback_text = """Some text...
    
    In conclusion: This is the conclusion
    
    More text..."""
    
    # Test all classes with all text types to verify proper tag prioritization
    
    # Test CognitiveDissonanceAmplifier
    assert cda._extract_idea_description(synthesis_text) == "Synthesis idea content"
    assert cda._extract_idea_description(final_idea_text) == "Final idea content"
    assert cda._extract_idea_description(revolutionary_text) == "Revolutionary idea content"
    assert cda._extract_idea_description(idea_text) == "General idea content"
    assert "This is the conclusion" in cda._extract_idea_description(fallback_text)
    
    # Test ImpossibilityEnforcer
    assert ie._extract_idea_description(synthesis_text) == "Synthesis idea content"
    assert ie._extract_idea_description(final_idea_text) == "Final idea content"
    assert ie._extract_idea_description(revolutionary_text) == "Revolutionary idea content"
    assert ie._extract_idea_description(idea_text) == "General idea content"
    assert "This is the conclusion" in ie._extract_idea_description(fallback_text)
    
    # Test MultiAgentDialecticSystem
    assert mads._extract_idea_description(synthesis_text) == "Synthesis idea content"
    assert mads._extract_idea_description(final_idea_text) == "Final idea content"
    assert mads._extract_idea_description(revolutionary_text) == "Revolutionary idea content"
    assert mads._extract_idea_description(idea_text) == "General idea content"
    assert "This is the conclusion" in mads._extract_idea_description(fallback_text)
    
    # Test TemporalPerspectiveShifter
    assert tps._extract_idea_description(synthesis_text) == "Synthesis idea content"
    assert tps._extract_idea_description(final_idea_text) == "Final idea content"
    assert tps._extract_idea_description(revolutionary_text) == "Revolutionary idea content"
    assert tps._extract_idea_description(idea_text) == "General idea content"
    assert "This is the conclusion" in tps._extract_idea_description(fallback_text)
    
    # Test ExplorerModule
    assert em._extract_idea_description(synthesis_text) == "Synthesis idea content"
    assert em._extract_idea_description(final_idea_text) == "Final idea content"
    assert em._extract_idea_description(revolutionary_text) == "Revolutionary idea content"
    assert em._extract_idea_description(idea_text) == "General idea content"
    assert "This is the conclusion" in em._extract_idea_description(fallback_text)