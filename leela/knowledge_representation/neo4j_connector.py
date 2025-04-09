"""
Neo4j connector for quantum entanglement relationships.
Provides a graph representation of concept networks and entanglement.

Implements prompt: quantum_entanglement.txt
"""
import os
import uuid
from typing import Dict, List, Any, Optional, Union, Set, Protocol, runtime_checkable
from typing_extensions import TypeAlias  # For Python 3.9 compatibility
from pydantic import UUID4
import asyncio
from dotenv import load_dotenv

from ..config import get_config
from ..knowledge_representation.models import (
    Concept, EntanglementLink, ConceptState
)
from ..prompt_management import uses_prompt

# Load environment variables and config
load_dotenv()
config = get_config()

# Get Neo4j configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# Try to import Neo4j
try:
    from neo4j import AsyncGraphDatabase, AsyncDriver
    NEO4J_AVAILABLE = True
except ImportError:
    print("Neo4j driver not available. You can install it with 'poetry install --with optional'.")
    NEO4J_AVAILABLE = False
    
    # Define protocol for type checking
    @runtime_checkable
    class AsyncDriver(Protocol):
        async def verify_connectivity(self) -> None:
            ...
        
        async def close(self) -> None:
            ...
        
        def session(self, *args, **kwargs) -> Any:
            ...
    
    class AsyncGraphDatabase:
        @staticmethod
        def driver(*args, **kwargs) -> None:
            return None


class InMemoryNeo4jMock:
    """
    In-memory mock implementation of Neo4j for development without Neo4j installed.
    This provides the same API as the Neo4j connector but stores data in memory.
    """
    
    def __init__(self):
        """Initialize the in-memory Neo4j mock."""
        self.concepts = {}  # Dict[str, Dict] - concept_id -> concept
        self.states = {}    # Dict[str, Dict] - state_id -> state
        self.entanglements = {}  # Dict[str, Dict] - source_id -> Dict[target_id, entanglement]
    
    async def connect(self) -> bool:
        """Mock connection that always succeeds."""
        print("Connected to in-memory Neo4j mock.")
        return True
    
    async def close(self) -> None:
        """Mock closing connection."""
        self.concepts = {}
        self.states = {}
        self.entanglements = {}
    
    async def initialize_schema(self) -> None:
        """Mock schema initialization."""
        print("Initialized in-memory Neo4j mock schema.")
    
    async def store_concept(self, concept: Concept) -> bool:
        """Store a concept in memory."""
        concept_id = str(concept.id)
        self.concepts[concept_id] = {
            "id": concept_id,
            "name": concept.name,
            "domain": concept.domain,
            "definition": concept.definition,
            "attributes": concept.attributes,
            "updated_at": asyncio.get_event_loop().time()
        }
        
        # Store states
        for state in concept.superposition_states:
            state_id = str(uuid.uuid4())
            self.states[state_id] = {
                "id": state_id,
                "concept_id": concept_id,
                "state_definition": state.state_definition,
                "probability": state.probability,
                "context_triggers": state.context_triggers,
                "created_at": asyncio.get_event_loop().time()
            }
        
        return True
    
    async def store_entanglement(self, source_id: Union[UUID4, str], target_id: Union[UUID4, str],
                               entanglement_type: str, correlation_strength: float,
                               evolution_rules: str) -> bool:
        """Store an entanglement relationship in memory."""
        source_id_str = str(source_id)
        target_id_str = str(target_id)
        
        if source_id_str not in self.entanglements:
            self.entanglements[source_id_str] = {}
        
        self.entanglements[source_id_str][target_id_str] = {
            "type": entanglement_type,
            "strength": correlation_strength,
            "rules": evolution_rules,
            "updated_at": asyncio.get_event_loop().time()
        }
        
        return True
    
    async def get_entangled_concepts(self, concept_id: Union[UUID4, str],
                                  min_correlation: float = 0.0) -> List[Dict[str, Any]]:
        """Get all concepts entangled with the specified concept."""
        concept_id_str = str(concept_id)
        result = []
        
        if concept_id_str in self.entanglements:
            for target_id, entanglement in self.entanglements[concept_id_str].items():
                if entanglement["strength"] >= min_correlation and target_id in self.concepts:
                    concept = self.concepts[target_id]
                    result.append({
                        "id": target_id,
                        "name": concept["name"],
                        "domain": concept["domain"],
                        "entanglement_type": entanglement["type"],
                        "correlation_strength": entanglement["strength"],
                        "evolution_rules": entanglement["rules"]
                    })
        
        return result
    
    async def delete_concept(self, concept_id: Union[UUID4, str]) -> bool:
        """Delete a concept and its relationships from memory."""
        concept_id_str = str(concept_id)
        
        # Remove concept
        if concept_id_str in self.concepts:
            del self.concepts[concept_id_str]
        
        # Remove states
        self.states = {k: v for k, v in self.states.items() if v["concept_id"] != concept_id_str}
        
        # Remove entanglements
        if concept_id_str in self.entanglements:
            del self.entanglements[concept_id_str]
        
        # Remove entanglements where this concept is a target
        for source_id in self.entanglements:
            if concept_id_str in self.entanglements[source_id]:
                del self.entanglements[source_id][concept_id_str]
        
        return True
    
    async def entanglement_exists(self, source_id: Union[UUID4, str],
                                target_id: Union[UUID4, str]) -> bool:
        """Check if an entanglement relationship exists between two concepts."""
        source_id_str = str(source_id)
        target_id_str = str(target_id)
        
        return (source_id_str in self.entanglements and
                target_id_str in self.entanglements[source_id_str])
    
    async def find_concept_by_name(self, name: str, domain: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Find a concept by name, optionally filtering by domain."""
        for concept_id, concept in self.concepts.items():
            if concept["name"] == name:
                if domain is None or concept["domain"] == domain:
                    return {
                        "id": concept_id,
                        "name": concept["name"],
                        "domain": concept["domain"],
                        "definition": concept["definition"],
                        "attributes": concept["attributes"]
                    }
        return None
    
    async def get_entanglement_network(self, root_concept_id: Union[UUID4, str],
                                    max_depth: int = 2) -> Dict[str, Any]:
        """Get the entanglement network surrounding a concept to a specified depth."""
        root_id_str = str(root_concept_id)
        visited = set([root_id_str])
        queue = [(root_id_str, 0)]  # (concept_id, depth)
        nodes = []
        edges = []
        
        # Add root node
        if root_id_str in self.concepts:
            root_concept = self.concepts[root_id_str]
            nodes.append({
                "id": root_id_str,
                "name": root_concept["name"],
                "domain": root_concept["domain"],
                "definition": root_concept["definition"]
            })
        
        # BFS traversal
        i = 0
        while i < len(queue):
            concept_id, depth = queue[i]
            i += 1
            
            if depth >= max_depth:
                continue
            
            # Get entangled concepts
            if concept_id in self.entanglements:
                for target_id, entanglement in self.entanglements[concept_id].items():
                    if target_id not in visited and target_id in self.concepts:
                        visited.add(target_id)
                        queue.append((target_id, depth + 1))
                        
                        # Add node
                        target_concept = self.concepts[target_id]
                        nodes.append({
                            "id": target_id,
                            "name": target_concept["name"],
                            "domain": target_concept["domain"],
                            "definition": target_concept["definition"]
                        })
                        
                        # Add edge
                        edges.append({
                            "source": concept_id,
                            "target": target_id,
                            "type": entanglement["type"],
                            "strength": entanglement["strength"]
                        })
        
        return {
            "nodes": nodes,
            "edges": edges
        }


@uses_prompt("quantum_entanglement")
class Neo4jConnector:
    """
    Connector for Neo4j graph database to store quantum entanglement relationships.
    Falls back to in-memory implementation if Neo4j is not available.
    
    This class implements the quantum_entanglement.txt prompt to create and manage
    entanglement relationships between concepts, storing them in a graph database.
    """
    
    def __init__(self, uri: Optional[str] = None, user: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize the Neo4j connector.
        
        Args:
            uri: Neo4j URI (defaults to environment variable or localhost)
            user: Neo4j username (defaults to environment variable or 'neo4j')
            password: Neo4j password (defaults to environment variable)
        """
        self.uri = uri or NEO4J_URI
        self.user = user or NEO4J_USER
        self.password = password or NEO4J_PASSWORD
        self.driver = None
        
        # Use in-memory implementation if Neo4j is not available
        if not NEO4J_AVAILABLE:
            self.in_memory = InMemoryNeo4jMock()
        else:
            self.in_memory = None
    
    async def connect(self) -> bool:
        """Connect to Neo4j database or initialize in-memory implementation."""
        # Use in-memory implementation
        if not NEO4J_AVAILABLE:
            return await self.in_memory.connect()
        
        # Connect to Neo4j
        try:
            self.driver = AsyncGraphDatabase.driver(
                self.uri, 
                auth=(self.user, self.password)
            )
            # Test connection
            await self.driver.verify_connectivity()
            print(f"Successfully connected to Neo4j at {self.uri}")
            return True
        except Exception as e:
            print(f"Error connecting to Neo4j: {e}")
            print("Falling back to in-memory implementation.")
            self.in_memory = InMemoryNeo4jMock()
            return await self.in_memory.connect()
    
    async def close(self) -> None:
        """Close the Neo4j connection or clean up in-memory implementation."""
        if self.in_memory:
            await self.in_memory.close()
        elif self.driver:
            await self.driver.close()
            self.driver = None
    
    async def initialize_schema(self) -> None:
        """Create constraints and indexes for the graph schema."""
        if self.in_memory:
            await self.in_memory.initialize_schema()
            return
            
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j. Call connect() first.")
        
        # Create constraints
        constraints = [
            "CREATE CONSTRAINT concept_id IF NOT EXISTS FOR (c:Concept) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT concept_state_id IF NOT EXISTS FOR (s:ConceptState) REQUIRE s.id IS UNIQUE"
        ]
        
        # Create indexes
        indexes = [
            "CREATE INDEX concept_domain_idx IF NOT EXISTS FOR (c:Concept) ON (c.domain)",
            "CREATE INDEX entanglement_type_idx IF NOT EXISTS FOR ()-[r:ENTANGLED]-() ON (r.type)"
        ]
        
        async with self.driver.session() as session:
            # Execute constraints
            for constraint in constraints:
                try:
                    await session.run(constraint)
                except Exception as e:
                    print(f"Error creating constraint: {e}")
            
            # Execute indexes
            for index in indexes:
                try:
                    await session.run(index)
                except Exception as e:
                    print(f"Error creating index: {e}")
            
            print("Neo4j schema initialized successfully")
    
    async def store_concept(self, concept: Concept) -> bool:
        """
        Store a concept and its superposition states in Neo4j.
        
        Args:
            concept: The concept to store
            
        Returns:
            bool: True if successful, False otherwise
        """
        if self.in_memory:
            return await self.in_memory.store_concept(concept)
            
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j. Call connect() first.")
        
        try:
            async with self.driver.session() as session:
                # Convert UUID to string for Neo4j
                concept_id = str(concept.id)
                
                # Create or update concept node
                concept_query = """
                MERGE (c:Concept {id: $id})
                SET c.name = $name,
                    c.domain = $domain,
                    c.definition = $definition,
                    c.attributes = $attributes,
                    c.updated_at = timestamp()
                RETURN c
                """
                
                concept_params = {
                    "id": concept_id,
                    "name": concept.name,
                    "domain": concept.domain,
                    "definition": concept.definition,
                    "attributes": concept.attributes
                }
                
                await session.run(concept_query, concept_params)
                
                # Handle superposition states
                # First, delete existing states
                delete_states_query = """
                MATCH (c:Concept {id: $concept_id})-[r:HAS_STATE]->(s:ConceptState)
                DELETE r, s
                """
                
                await session.run(delete_states_query, {"concept_id": concept_id})
                
                # Create new states
                for i, state in enumerate(concept.superposition_states):
                    state_id = str(uuid.uuid4())
                    state_query = """
                    MATCH (c:Concept {id: $concept_id})
                    CREATE (s:ConceptState {
                        id: $state_id,
                        state_definition: $definition,
                        probability: $probability,
                        context_triggers: $triggers,
                        created_at: timestamp()
                    })
                    CREATE (c)-[r:HAS_STATE]->(s)
                    RETURN s
                    """
                    
                    state_params = {
                        "concept_id": concept_id,
                        "state_id": state_id,
                        "definition": state.state_definition,
                        "probability": state.probability,
                        "triggers": state.context_triggers
                    }
                    
                    await session.run(state_query, state_params)
                
                return True
                
        except Exception as e:
            print(f"Error storing concept in Neo4j: {e}")
            return False
    
    async def store_entanglement(self, source_id: Union[UUID4, str], target_id: Union[UUID4, str], 
                               entanglement_type: str, correlation_strength: float,
                               evolution_rules: str) -> bool:
        """
        Create an entanglement relationship between two concepts.
        
        Args:
            source_id: ID of the source concept
            target_id: ID of the target concept
            entanglement_type: Type of entanglement
            correlation_strength: Strength of the correlation (0.0-1.0)
            evolution_rules: Rules for how changes propagate
            
        Returns:
            bool: True if successful, False otherwise
        """
        if self.in_memory:
            return await self.in_memory.store_entanglement(
                source_id, target_id, entanglement_type, correlation_strength, evolution_rules
            )
            
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j. Call connect() first.")
        
        try:
            # Convert IDs to strings if they are UUIDs
            source_id_str = str(source_id)
            target_id_str = str(target_id)
            
            async with self.driver.session() as session:
                # Create or update entanglement relationship
                entanglement_query = """
                MATCH (source:Concept {id: $source_id})
                MATCH (target:Concept {id: $target_id})
                MERGE (source)-[r:ENTANGLED]->(target)
                SET r.type = $type,
                    r.correlation_strength = $strength,
                    r.evolution_rules = $rules,
                    r.updated_at = timestamp()
                RETURN r
                """
                
                entanglement_params = {
                    "source_id": source_id_str,
                    "target_id": target_id_str,
                    "type": entanglement_type,
                    "strength": correlation_strength,
                    "rules": evolution_rules
                }
                
                await session.run(entanglement_query, entanglement_params)
                return True
                
        except Exception as e:
            print(f"Error storing entanglement in Neo4j: {e}")
            return False
    
    async def get_entangled_concepts(self, concept_id: Union[UUID4, str], 
                                  min_correlation: float = 0.0) -> List[Dict[str, Any]]:
        """
        Get all concepts entangled with the specified concept.
        
        Args:
            concept_id: ID of the concept
            min_correlation: Minimum correlation strength to include
            
        Returns:
            List[Dict[str, Any]]: List of entangled concepts with relationship details
        """
        if self.in_memory:
            return await self.in_memory.get_entangled_concepts(concept_id, min_correlation)
            
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j. Call connect() first.")
        
        try:
            # Convert ID to string if it's a UUID
            concept_id_str = str(concept_id)
            
            async with self.driver.session() as session:
                # Query entangled concepts
                entanglement_query = """
                MATCH (c:Concept {id: $concept_id})-[r:ENTANGLED]->(target:Concept)
                WHERE r.correlation_strength >= $min_correlation
                RETURN target.id as id, target.name as name, target.domain as domain,
                       r.type as entanglement_type, r.correlation_strength as strength,
                       r.evolution_rules as rules
                """
                
                result = await session.run(entanglement_query, {
                    "concept_id": concept_id_str,
                    "min_correlation": min_correlation
                })
                
                entangled_concepts = []
                async for record in result:
                    entangled_concepts.append({
                        "id": record["id"],
                        "name": record["name"],
                        "domain": record["domain"],
                        "entanglement_type": record["entanglement_type"],
                        "correlation_strength": record["strength"],
                        "evolution_rules": record["rules"]
                    })
                
                return entangled_concepts
                
        except Exception as e:
            print(f"Error getting entangled concepts from Neo4j: {e}")
            return []
    
    async def delete_concept(self, concept_id: Union[UUID4, str]) -> bool:
        """
        Delete a concept and all its relationships from Neo4j.
        
        Args:
            concept_id: ID of the concept to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        if self.in_memory:
            return await self.in_memory.delete_concept(concept_id)
            
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j. Call connect() first.")
        
        try:
            # Convert ID to string if it's a UUID
            concept_id_str = str(concept_id)
            
            async with self.driver.session() as session:
                # Delete concept, states, and relationships
                delete_query = """
                MATCH (c:Concept {id: $concept_id})
                OPTIONAL MATCH (c)-[r1:HAS_STATE]->(s:ConceptState)
                OPTIONAL MATCH (c)-[r2:ENTANGLED]-()
                OPTIONAL MATCH ()-[r3:ENTANGLED]->(c)
                DELETE r1, s, r2, r3, c
                """
                
                await session.run(delete_query, {"concept_id": concept_id_str})
                return True
                
        except Exception as e:
            print(f"Error deleting concept from Neo4j: {e}")
            return False
    
    async def entanglement_exists(self, source_id: Union[UUID4, str], 
                                target_id: Union[UUID4, str]) -> bool:
        """
        Check if an entanglement relationship exists between two concepts.
        
        Args:
            source_id: ID of the source concept
            target_id: ID of the target concept
            
        Returns:
            bool: True if entanglement exists, False otherwise
        """
        if self.in_memory:
            return await self.in_memory.entanglement_exists(source_id, target_id)
            
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j. Call connect() first.")
        
        try:
            # Convert IDs to strings if they are UUIDs
            source_id_str = str(source_id)
            target_id_str = str(target_id)
            
            async with self.driver.session() as session:
                # Check for entanglement
                query = """
                MATCH (source:Concept {id: $source_id})-[r:ENTANGLED]->(target:Concept {id: $target_id})
                RETURN count(r) > 0 as exists
                """
                
                result = await session.run(query, {
                    "source_id": source_id_str,
                    "target_id": target_id_str
                })
                
                record = await result.single()
                return record["exists"] if record else False
                
        except Exception as e:
            print(f"Error checking entanglement in Neo4j: {e}")
            return False
    
    async def find_concept_by_name(self, name: str, domain: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Find a concept by name, optionally filtering by domain.
        
        Args:
            name: Concept name to search for
            domain: Optional domain to filter by
            
        Returns:
            Optional[Dict[str, Any]]: Concept data if found
        """
        if self.in_memory:
            return await self.in_memory.find_concept_by_name(name, domain)
            
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j. Call connect() first.")
        
        try:
            async with self.driver.session() as session:
                # Build query based on whether domain is provided
                if domain:
                    query = """
                    MATCH (c:Concept)
                    WHERE c.name = $name AND c.domain = $domain
                    RETURN c.id as id, c.name as name, c.domain as domain,
                           c.definition as definition, c.attributes as attributes
                    LIMIT 1
                    """
                    params = {"name": name, "domain": domain}
                else:
                    query = """
                    MATCH (c:Concept)
                    WHERE c.name = $name
                    RETURN c.id as id, c.name as name, c.domain as domain,
                           c.definition as definition, c.attributes as attributes
                    LIMIT 1
                    """
                    params = {"name": name}
                
                result = await session.run(query, params)
                record = await result.single()
                
                if record:
                    return {
                        "id": record["id"],
                        "name": record["name"],
                        "domain": record["domain"],
                        "definition": record["definition"],
                        "attributes": record["attributes"]
                    }
                return None
                
        except Exception as e:
            print(f"Error finding concept in Neo4j: {e}")
            return None
    
    async def get_entanglement_network(self, root_concept_id: Union[UUID4, str], 
                                    max_depth: int = 2) -> Dict[str, Any]:
        """
        Get the entanglement network surrounding a concept to a specified depth.
        
        Args:
            root_concept_id: ID of the root concept
            max_depth: Maximum depth to traverse
            
        Returns:
            Dict[str, Any]: Network with nodes and edges
        """
        if self.in_memory:
            return await self.in_memory.get_entanglement_network(root_concept_id, max_depth)
            
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j. Call connect() first.")
        
        try:
            # Convert ID to string if it's a UUID
            root_id_str = str(root_concept_id)
            
            async with self.driver.session() as session:
                # Query the entanglement network
                query = f"""
                MATCH path = (root:Concept {{id: $root_id}})-[:ENTANGLED*1..{max_depth}]-(c:Concept)
                WITH collect(path) as paths
                UNWIND paths as p
                UNWIND nodes(p) as n
                WITH DISTINCT n
                RETURN collect({{
                    id: n.id,
                    name: n.name,
                    domain: n.domain,
                    definition: n.definition
                }}) as nodes
                """
                
                nodes_result = await session.run(query, {"root_id": root_id_str})
                nodes_record = await nodes_result.single()
                nodes = nodes_record["nodes"] if nodes_record else []
                
                # Get relationships between these nodes
                edges_query = f"""
                MATCH path = (root:Concept {{id: $root_id}})-[:ENTANGLED*1..{max_depth}]-(c:Concept)
                UNWIND relationships(path) as r
                WITH DISTINCT r, startNode(r) as source, endNode(r) as target
                RETURN collect({{
                    source: source.id,
                    target: target.id,
                    type: r.type,
                    strength: r.correlation_strength
                }}) as edges
                """
                
                edges_result = await session.run(edges_query, {"root_id": root_id_str})
                edges_record = await edges_result.single()
                edges = edges_record["edges"] if edges_record else []
                
                return {
                    "nodes": nodes,
                    "edges": edges
                }
                
        except Exception as e:
            print(f"Error getting entanglement network from Neo4j: {e}")
            return {"nodes": [], "edges": []}


async def test_neo4j_connector():
    """Test function for Neo4j connector."""
    connector = Neo4jConnector()
    
    try:
        # Connect to Neo4j
        connected = await connector.connect()
        if not connected:
            print("Failed to connect to Neo4j or initialize in-memory implementation.")
            return
        
        # Initialize schema
        await connector.initialize_schema()
        
        # Create test concepts
        test_concept1 = Concept(
            id=uuid.uuid4(),
            name="Quantum Entanglement",
            domain="physics",
            definition="A quantum phenomenon where entangled particles remain connected",
            attributes={"field": "quantum mechanics", "complexity": "high"},
            superposition_states=[
                ConceptState(
                    state_definition="Physical phenomenon",
                    probability=0.6,
                    context_triggers=["experiment", "measurement"]
                ),
                ConceptState(
                    state_definition="Metaphorical connection",
                    probability=0.4,
                    context_triggers=["philosophy", "metaphor"]
                )
            ],
            entanglements=[],
            temporal_variants={}
        )
        
        test_concept2 = Concept(
            id=uuid.uuid4(),
            name="Knowledge Graph",
            domain="computer_science",
            definition="A graph-based knowledge representation",
            attributes={"field": "AI", "complexity": "medium"},
            superposition_states=[
                ConceptState(
                    state_definition="Data structure",
                    probability=0.7,
                    context_triggers=["database", "storage"]
                ),
                ConceptState(
                    state_definition="Conceptual model",
                    probability=0.3,
                    context_triggers=["ontology", "semantics"]
                )
            ],
            entanglements=[],
            temporal_variants={}
        )
        
        # Store concepts
        await connector.store_concept(test_concept1)
        await connector.store_concept(test_concept2)
        print(f"Stored test concepts: {test_concept1.name}, {test_concept2.name}")
        
        # Create entanglement
        await connector.store_entanglement(
            source_id=test_concept1.id,
            target_id=test_concept2.id,
            entanglement_type="conceptual_bridge",
            correlation_strength=0.8,
            evolution_rules="Bidirectional influence with probabilistic updates"
        )
        print(f"Created entanglement between {test_concept1.name} and {test_concept2.name}")
        
        # Query entangled concepts
        entangled = await connector.get_entangled_concepts(test_concept1.id)
        print(f"Entangled concepts: {entangled}")
        
        # Get entanglement network
        network = await connector.get_entanglement_network(test_concept1.id)
        print(f"Network nodes: {len(network['nodes'])}, edges: {len(network['edges'])}")
        
        # Clean up
        await connector.delete_concept(test_concept1.id)
        await connector.delete_concept(test_concept2.id)
        print("Test concepts deleted")
        
    finally:
        # Close connection
        await connector.close()
        
        
if __name__ == "__main__":
    # Run test if executed directly
    asyncio.run(test_neo4j_connector())