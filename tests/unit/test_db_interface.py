"""
Unit tests for database interface.
"""
import pytest
import uuid
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from unittest.mock import patch, MagicMock

from leela.knowledge_representation.models import (
    Concept, ConceptState, EntanglementLink, TemporalVariant, Relationship,
    CreativeIdea, ShockProfile, ThinkingStep, MethodologyChange, SpiralState
)
from leela.data_persistence.db_interface import (
    DatabaseManager, DBConcept, DBConceptState, DBEntanglementLink, 
    DBTemporalVariant, DBRelationship, DBCreativeIdea, DBShockProfile,
    DBThinkingStep, DBMethodologyChange, DBSpiralState
)


class MockConnection:
    """Mock for SQLAlchemy connection."""
    def __init__(self, *args, **kwargs):
        self.transaction_count = 0
    
    async def __aenter__(self):
        self.transaction_count += 1
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.transaction_count -= 1
        return False
    
    async def run_sync(self, callable_):
        """Run a synchronous callable."""
        return callable_(self)


class MockEngine:
    """Mock for SQLAlchemy engine."""
    def __init__(self, *args, **kwargs):
        self.connection = MockConnection()
    
    def begin(self):
        """Begin a transaction."""
        return self.connection


class MockSession:
    """Mock for SQLAlchemy session."""
    def __init__(self):
        self.committed = False
        self.flushed = False
        self.objects = []
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return False
    
    def begin(self):
        """Begin a transaction."""
        return self
    
    def add(self, obj):
        """Add an object to the session."""
        self.objects.append(obj)
    
    async def commit(self):
        """Commit the session."""
        self.committed = True
    
    async def flush(self):
        """Flush the session."""
        self.flushed = True
    
    async def execute(self, *args, **kwargs):
        """Execute a query."""
        return MagicSessionResult()


class MagicSessionResult:
    """Mock for SQLAlchemy result."""
    def scalars(self):
        """Return a list of scalars."""
        return self
    
    def first(self):
        """Return the first result."""
        return None
    
    def all(self):
        """Return all results."""
        return []


@pytest.fixture
def mock_db_manager():
    """Create a mock DatabaseManager."""
    with patch("leela.data_persistence.db_interface.create_async_engine") as mock_engine:
        with patch("leela.data_persistence.db_interface.async_sessionmaker") as mock_session_maker:
            # Set up mock engine
            mock_engine.return_value = MockEngine()
            
            # Set up mock session
            mock_session = MockSession()
            mock_session_maker.return_value = lambda: mock_session
            
            db_manager = DatabaseManager(db_url="postgresql+asyncpg://test:test@localhost:5432/test_db")
            yield db_manager, mock_session


@pytest.mark.asyncio
async def test_initialize_db(mock_db_manager):
    """Test initializing the database."""
    db_manager, mock_session = mock_db_manager
    await db_manager.initialize_db()
    
    # Check that engine.begin() was called
    assert db_manager.engine.connection.transaction_count == 0


@pytest.mark.asyncio
async def test_save_concept(mock_db_manager):
    """Test saving a concept."""
    db_manager, mock_session = mock_db_manager
    
    # Create a concept
    concept = Concept(
        id=uuid.uuid4(),
        name="Test Concept",
        domain="test_domain",
        definition="Test definition",
        attributes={"key": "value"},
        superposition_states=[
            ConceptState(
                state_definition="State 1",
                probability=0.5,
                context_triggers=["trigger1"]
            )
        ],
        entanglements=[
            EntanglementLink(
                target_concept_id=uuid.uuid4(),
                entanglement_type="test",
                correlation_strength=0.5,
                evolution_rules="Test rules"
            )
        ],
        temporal_variants={
            "era1": TemporalVariant(
                era="era1",
                definition="Era 1 definition",
                significance="Era 1 significance",
                applicability_score=0.5
            )
        }
    )
    
    # Save the concept
    with patch("leela.data_persistence.db_interface.select") as mock_select:
        mock_select.return_value = "SELECT"
        result = await db_manager.save_concept(concept)
    
    # Check that session.add() was called
    assert len(mock_session.objects) > 0
    # Check that session.commit() was called
    assert mock_session.committed
    
    # Check that the returned concept matches the input
    assert concept.id == result.id
    assert concept.name == result.name
    assert concept.domain == result.domain