#!/usr/bin/env python3
"""
OBINexus Pheno Token System with AVL Trie NexusSearch
=====================================================
Implements the witness/actor model for state observation with event bubbling.
Based on State Machine Minimization principles from OBINexus framework.

Token Structure: (Type, Value, Memory_Index)
- Type: Token classification (FILE, DIR, CHAR, etc.)
- Value: Actual token content
- Memory: Allocated memory index for witness tracking
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Set, Tuple, Any
from enum import Enum, auto
import hashlib
from collections import deque


class TokenType(Enum):
    """Pheno Token Types - Witness categorization"""
    EPSILON = auto()  # Empty state (nil/null) - minimized state
    FILE = auto()
    DIRECTORY = auto()
    CHARACTER = auto()
    WORD = auto()
    PATTERN = auto()
    DOCUMENT = auto()


class WitnessState(Enum):
    """Actor model state for witnessing changes"""
    UNOBSERVED = auto()
    OBSERVED = auto()
    CHANGED = auto()
    BUBBLING = auto()  # Event bubbling upward


@dataclass
class PhenoToken:
    """
    Pheno Token Structure with Type-Value-Memory separation
    Implements compile-time safety principles from OBINexus
    """
    token_type: TokenType
    token_value: Any
    token_memory_index: int
    witness_state: WitnessState = WitnessState.UNOBSERVED
    
    def __hash__(self):
        return hash((self.token_type, str(self.token_value), self.token_memory_index))
    
    def to_epsilon(self) -> 'PhenoToken':
        """State machine minimization - reduce to epsilon (empty) state"""
        return PhenoToken(
            token_type=TokenType.EPSILON,
            token_value=None,
            token_memory_index=self.token_memory_index,
            witness_state=WitnessState.UNOBSERVED
        )


class AVLTrieNode:
    """
    AVL Trie Node for NexusSearch - each character is a witness
    Implements self-balancing for O(log n) search complexity
    """
    def __init__(self, char: str = None):
        self.char = char
        self.children: Dict[str, 'AVLTrieNode'] = {}
        self.is_end_of_word = False
        self.height = 1
        self.balance_factor = 0
        
        # Witness sets - dual witness pattern
        self.witness_set_primary: Set[PhenoToken] = set()
        self.witness_set_secondary: Set[PhenoToken] = set()
        
        # Document references for this node
        self.document_refs: List[Tuple[str, int]] = []  # (doc_id, position)
        
    def get_height(self) -> int:
        """Get current height of node"""
        return self.height if self else 0
    
    def update_height(self):
        """Update height based on children"""
        left_height = self.children.get('_left', AVLTrieNode()).get_height()
        right_height = self.children.get('_right', AVLTrieNode()).get_height()
        self.height = 1 + max(left_height, right_height)
        
    def update_balance_factor(self):
        """Calculate balance factor for AVL property"""
        left_height = self.children.get('_left', AVLTrieNode()).get_height()
        right_height = self.children.get('_right', AVLTrieNode()).get_height()
        self.balance_factor = left_height - right_height


class NexusSearchAVL:
    """
    NexusSearch implementation using AVL Trie with witness pattern
    Supports BFS/DFS traversal with A* scoring for optimal search
    """
    
    def __init__(self):
        self.root = AVLTrieNode()
        self.memory_allocator = 0  # Pheno memory index tracker
        self.actor_event_queue: deque = deque()  # Event bubbling queue
        
    def allocate_memory_index(self) -> int:
        """Allocate next memory index for Pheno token"""
        self.memory_allocator += 1
        return self.memory_allocator
    
    def _rotate_right(self, node: AVLTrieNode) -> AVLTrieNode:
        """Right rotation for AVL rebalancing (LL case)"""
        left_child = node.children.get('_left')
        if not left_child:
            return node
            
        # Perform rotation
        node.children['_left'] = left_child.children.get('_right')
        left_child.children['_right'] = node
        
        # Update heights
        node.update_height()
        left_child.update_height()
        
        return left_child
    
    def _rotate_left(self, node: AVLTrieNode) -> AVLTrieNode:
        """Left rotation for AVL rebalancing (RR case)"""
        right_child = node.children.get('_right')
        if not right_child:
            return node
            
        # Perform rotation
        node.children['_right'] = right_child.children.get('_left')
        right_child.children['_left'] = node
        
        # Update heights
        node.update_height()
        right_child.update_height()
        
        return right_child
    
    def _balance_node(self, node: AVLTrieNode) -> AVLTrieNode:
        """Balance node using AVL rotations"""
        node.update_height()
        node.update_balance_factor()
        
        # Left-Left case
        if node.balance_factor > 1:
            left_child = node.children.get('_left')
            if left_child and left_child.balance_factor >= 0:
                return self._rotate_right(node)
            # Left-Right case
            elif left_child:
                node.children['_left'] = self._rotate_left(left_child)
                return self._rotate_right(node)
        
        # Right-Right case
        if node.balance_factor < -1:
            right_child = node.children.get('_right')
            if right_child and right_child.balance_factor <= 0:
                return self._rotate_left(node)
            # Right-Left case
            elif right_child:
                node.children['_right'] = self._rotate_right(right_child)
                return self._rotate_left(node)
        
        return node
    
    def insert_word(self, word: str, doc_id: str, position: int = 0) -> PhenoToken:
        """
        Insert word into AVL trie with witness tracking
        Returns: PhenoToken for the inserted word
        """
        if not word:
            return PhenoToken(TokenType.EPSILON, None, 0)
        
        # Create Pheno token for this word
        token = PhenoToken(
            token_type=TokenType.WORD,
            token_value=word,
            token_memory_index=self.allocate_memory_index(),
            witness_state=WitnessState.OBSERVED
        )
        
        # Insert into trie
        current = self.root
        for i, char in enumerate(word):
            # Create character token witness
            char_token = PhenoToken(
                token_type=TokenType.CHARACTER,
                token_value=char,
                token_memory_index=self.allocate_memory_index(),
                witness_state=WitnessState.OBSERVED
            )
            
            if char not in current.children:
                current.children[char] = AVLTrieNode(char)
            
            current = current.children[char]
            
            # Add to witness sets (dual witness pattern)
            current.witness_set_primary.add(char_token)
            current.witness_set_secondary.add(token)
            
            # Balance after insertion
            current = self._balance_node(current)
        
        current.is_end_of_word = True
        current.document_refs.append((doc_id, position))
        
        # Trigger event bubbling
        self._bubble_event(token, WitnessState.CHANGED)
        
        return token
    
    def _bubble_event(self, token: PhenoToken, new_state: WitnessState):
        """
        Event bubbling upward - actor model notification
        Events bubble UP the source tree, not downstream
        """
        event = {
            'token': token,
            'old_state': token.witness_state,
            'new_state': new_state,
            'timestamp': self.allocate_memory_index()  # Use as timestamp proxy
        }
        
        token.witness_state = WitnessState.BUBBLING
        self.actor_event_queue.append(event)
        token.witness_state = new_state
    
    def search_bfs(self, pattern: str, max_results: int = 10) -> List[Tuple[str, float]]:
        """
        Breadth-First Search for pattern matching
        Returns: List of (word, score) tuples
        """
        if not pattern:
            return []
        
        results = []
        queue = deque([(self.root, "", 0)])  # (node, current_word, depth)
        
        while queue and len(results) < max_results:
            node, current_word, depth = queue.popleft()
            
            # Check if current word matches pattern (fuzzy)
            if node.is_end_of_word and current_word:
                score = self._calculate_score(pattern, current_word, depth)
                if score > 0.3:  # Threshold for relevance
                    results.append((current_word, score))
            
            # Add children to queue (BFS level-order traversal)
            for char, child in node.children.items():
                if char not in ['_left', '_right']:  # Skip AVL metadata
                    queue.append((child, current_word + char, depth + 1))
        
        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    
    def search_dfs(self, pattern: str, max_results: int = 10) -> List[Tuple[str, float]]:
        """
        Depth-First Search for pattern matching
        Returns: List of (word, score) tuples
        """
        if not pattern:
            return []
        
        results = []
        
        def dfs_helper(node: AVLTrieNode, current_word: str, depth: int):
            if len(results) >= max_results:
                return
            
            if node.is_end_of_word and current_word:
                score = self._calculate_score(pattern, current_word, depth)
                if score > 0.3:
                    results.append((current_word, score))
            
            # DFS: go deep first
            for char, child in node.children.items():
                if char not in ['_left', '_right']:
                    dfs_helper(child, current_word + char, depth + 1)
        
        dfs_helper(self.root, "", 0)
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    
    def _calculate_score(self, pattern: str, word: str, depth: int) -> float:
        """
        A* scoring algorithm for search relevance
        Combines multiple heuristics for optimal ranking
        """
        if not pattern or not word:
            return 0.0
        
        pattern_lower = pattern.lower()
        word_lower = word.lower()
        
        # Exact match
        if pattern_lower == word_lower:
            return 1.0
        
        # Prefix match (high score)
        if word_lower.startswith(pattern_lower):
            return 0.9
        
        # Contains match
        if pattern_lower in word_lower:
            return 0.7
        
        # Edit distance (Levenshtein approximation)
        edit_distance = self._levenshtein_distance(pattern_lower, word_lower)
        max_len = max(len(pattern_lower), len(word_lower))
        similarity = 1.0 - (edit_distance / max_len)
        
        # Depth penalty (prefer shorter paths)
        depth_penalty = 1.0 / (1.0 + depth * 0.1)
        
        return similarity * depth_penalty
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein edit distance"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def get_witness_state(self, token: PhenoToken) -> Dict[str, Any]:
        """Get current witness state for a token"""
        return {
            'token': token,
            'state': token.witness_state,
            'memory_index': token.token_memory_index,
            'events_pending': len(self.actor_event_queue)
        }
    
    def process_event_queue(self) -> List[Dict]:
        """Process all pending actor events (event bubbling)"""
        processed_events = []
        
        while self.actor_event_queue:
            event = self.actor_event_queue.popleft()
            processed_events.append(event)
            
            # Actor model: notify observers of state change
            # Events bubble upward through the tree
            print(f"Event bubbled: {event['token'].token_value} "
                  f"{event['old_state']} -> {event['new_state']}")
        
        return processed_events


# Example usage and testing
if __name__ == "__main__":
    # Initialize NexusSearch with AVL trie
    search_engine = NexusSearchAVL()
    
    # Insert test words with witness tracking
    words = ["cat", "cats", "dog", "dogs", "rat", "rats", "mat", "mats", "dot"]
    for i, word in enumerate(words):
        token = search_engine.insert_word(word, f"doc_{i}", i)
        print(f"Inserted: {token.token_value} (Memory: {token.token_memory_index})")
    
    # Process event bubbling
    print("\n=== Processing Event Queue ===")
    events = search_engine.process_event_queue()
    
    # Test BFS search
    print("\n=== BFS Search for 'cat' ===")
    results_bfs = search_engine.search_bfs("cat")
    for word, score in results_bfs:
        print(f"  {word}: {score:.3f}")
    
    # Test DFS search
    print("\n=== DFS Search for 'dot' ===")
    results_dfs = search_engine.search_dfs("dot")
    for word, score in results_dfs:
        print(f"  {word}: {score:.3f}")
    
    # Test state minimization (epsilon state)
    print("\n=== State Minimization Example ===")
    token = PhenoToken(TokenType.WORD, "test", 999)
    epsilon_token = token.to_epsilon()
    print(f"Original: {token}")
    print(f"Epsilon (minimized): {epsilon_token}")
