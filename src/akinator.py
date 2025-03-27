#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Akinator-like game implementation that guesses what the player is thinking about
by asking yes/no questions based on a decision tree.
"""

import json
import os
import random
from typing import Dict, List, Optional, Tuple, Union


class AkinatorNode:
    """A node in the Akinator decision tree."""
    
    def __init__(self, content: str, is_question: bool = True):
        """
        Initialize a node.
        
        Args:
            content: The question text or guess text
            is_question: True if this is a question node, False if it's a guess/leaf node
        """
        self.content = content
        self.is_question = is_question
        self.yes_node = None
        self.no_node = None
    
    def to_dict(self) -> Dict:
        """Convert the node and its children to a dictionary for serialization."""
        result = {
            "content": self.content,
            "is_question": self.is_question,
        }
        
        if self.yes_node:
            result["yes_node"] = self.yes_node.to_dict()
        
        if self.no_node:
            result["no_node"] = self.no_node.to_dict()
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AkinatorNode':
        """Create a node from a dictionary (deserialization)."""
        node = cls(data["content"], data["is_question"])
        
        if "yes_node" in data and data["yes_node"]:
            node.yes_node = cls.from_dict(data["yes_node"])
            
        if "no_node" in data and data["no_node"]:
            node.no_node = cls.from_dict(data["no_node"])
            
        return node


class Akinator:
    """The main Akinator game class."""
    
    def __init__(self, data_file: str = None):
        """
        Initialize the Akinator game.
        
        Args:
            data_file: Path to a JSON file containing the decision tree data
        """
        self.current_node = None
        self.root_node = None
        self.data_file = data_file or os.path.join("data", "knowledge_tree.json")
        
        # Try to load the decision tree
        if os.path.exists(self.data_file):
            self.load_tree()
        else:
            # Create a simple default tree if no data file exists
            self.create_default_tree()
    
    def create_default_tree(self):
        """Create a simple default decision tree with a few examples."""
        # Create a root question
        self.root_node = AkinatorNode("生物ですか？")
        
        # Yes branch - living things
        living = AkinatorNode("動物ですか？")
        self.root_node.yes_node = living
        
        animal = AkinatorNode("四本足がありますか？")
        living.yes_node = animal
        
        plant = AkinatorNode("花を咲かせますか？")
        living.no_node = plant
        
        # Four-legged animals
        four_legged = AkinatorNode("ペットとして飼われますか？")
        animal.yes_node = four_legged
        
        # Pets
        dog = AkinatorNode("犬", False)
        cat = AkinatorNode("猫", False)
        four_legged.yes_node = dog
        four_legged.no_node = cat
        
        # Non-four-legged animals
        bird = AkinatorNode("空を飛びますか？")
        animal.no_node = bird
        
        eagle = AkinatorNode("鷲", False)
        fish = AkinatorNode("魚", False)
        bird.yes_node = eagle
        bird.no_node = fish
        
        # Plants
        flower = AkinatorNode("バラ", False)
        tree = AkinatorNode("木", False)
        plant.yes_node = flower
        plant.no_node = tree
        
        # No branch - non-living things
        non_living = AkinatorNode("電子機器ですか？")
        self.root_node.no_node = non_living
        
        electronic = AkinatorNode("コミュニケーションに使いますか？")
        non_living.yes_node = electronic
        
        phone = AkinatorNode("スマートフォン", False)
        computer = AkinatorNode("コンピュータ", False)
        electronic.yes_node = phone
        electronic.no_node = computer
        
        # Non-electronic things
        object_node = AkinatorNode("座ることができますか？")
        non_living.no_node = object_node
        
        chair = AkinatorNode("椅子", False)
        table = AkinatorNode("テーブル", False)
        object_node.yes_node = chair
        object_node.no_node = table
        
        # Save the tree
        self.save_tree()
    
    def load_tree(self):
        """Load the decision tree from a JSON file."""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.root_node = AkinatorNode.from_dict(data)
        except Exception as e:
            print(f"Error loading knowledge tree: {e}")
            self.create_default_tree()
    
    def save_tree(self):
        """Save the decision tree to a JSON file."""
        if not self.root_node:
            return
        
        # Create the data directory if it doesn't exist
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.root_node.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving knowledge tree: {e}")
    
    def start_game(self):
        """Start a new game."""
        self.current_node = self.root_node
    
    def get_current_question(self) -> str:
        """Get the current question or guess."""
        if not self.current_node:
            self.start_game()
        
        return self.current_node.content
    
    def is_question(self) -> bool:
        """Check if the current node is a question or a guess."""
        if not self.current_node:
            self.start_game()
        
        return self.current_node.is_question
    
    def answer(self, is_yes: bool) -> bool:
        """
        Process the user's answer.
        
        Args:
            is_yes: True if the user answered "yes", False for "no"
        
        Returns:
            bool: True if the game should continue, False if we reached a leaf node
        """
        if not self.current_node:
            self.start_game()
            return True
        
        # Navigate to the next node based on the answer
        if is_yes:
            self.current_node = self.current_node.yes_node
        else:
            self.current_node = self.current_node.no_node
        
        # If we've reached a None node or a guess node, return False to end the game
        return self.current_node is not None and self.current_node.is_question
    
    def learn(self, correct_answer: str, distinguishing_question: str, answer_for_correct: bool):
        """
        Learn from a wrong guess by adding a new node to the tree.
        
        Args:
            correct_answer: The correct answer (what the user was thinking of)
            distinguishing_question: A question that distinguishes between the guess and the correct answer
            answer_for_correct: Whether the answer to the distinguishing question is yes for the correct answer
        """
        if not self.current_node:
            return
        
        last_guess = self.current_node.content
        
        # Update the current node to be a question
        self.current_node.content = distinguishing_question
        self.current_node.is_question = True
        
        # Create new leaf nodes
        correct_node = AkinatorNode(correct_answer, False)
        wrong_node = AkinatorNode(last_guess, False)
        
        if answer_for_correct:
            self.current_node.yes_node = correct_node
            self.current_node.no_node = wrong_node
        else:
            self.current_node.yes_node = wrong_node
            self.current_node.no_node = correct_node
        
        # Save the updated tree
        self.save_tree()

    def add_character(self, character_name: str, character_attributes: Dict[str, bool]):
        """
        Add a new character to the knowledge base with specific attributes.
        
        Args:
            character_name: The name of the character
            character_attributes: A dictionary of attribute questions and yes/no answers
        """
        # Create a new leaf node for the character
        character_node = AkinatorNode(character_name, False)
        
        # If there's no root node yet, create one with the first attribute
        if not self.root_node:
            if character_attributes:
                first_attr, first_value = next(iter(character_attributes.items()))
                self.root_node = AkinatorNode(first_attr)
                
                if first_value:  # If the answer is yes
                    self.root_node.yes_node = character_node
                else:
                    self.root_node.no_node = character_node
                
                # Remove the used attribute
                del character_attributes[first_attr]
            else:
                # If no attributes, just set the character as root
                self.root_node = character_node
        else:
            # Start from the root
            current = self.root_node
            
            # Navigate to a leaf node based on the attributes
            while current.is_question:
                question = current.content
                
                # If we have an answer for this question
                if question in character_attributes:
                    is_yes = character_attributes[question]
                    
                    if is_yes:
                        if current.yes_node is None:
                            current.yes_node = character_node
                            break
                        current = current.yes_node
                    else:
                        if current.no_node is None:
                            current.no_node = character_node
                            break
                        current = current.no_node
                else:
                    # If we don't have an answer, choose a path randomly or stop here
                    if current.yes_node is None:
                        current.yes_node = character_node
                        break
                    elif current.no_node is None:
                        current.no_node = character_node
                        break
                    else:
                        # Just choose randomly
                        if random.choice([True, False]):
                            current = current.yes_node
                        else:
                            current = current.no_node
            
            # If we reached a leaf, we need to add a new question to distinguish
            if not current.is_question:
                # Find an unused attribute to distinguish
                for question, answer in character_attributes.items():
                    # Use this attribute to create a new question node
                    old_content = current.content
                    current.content = question
                    current.is_question = True
                    
                    old_node = AkinatorNode(old_content, False)
                    new_node = AkinatorNode(character_name, False)
                    
                    if answer:  # If the answer is yes for the new character
                        current.yes_node = new_node
                        current.no_node = old_node
                    else:
                        current.yes_node = old_node
                        current.no_node = new_node
                    
                    break
        
        # Save the tree
        self.save_tree()

    def get_all_questions(self) -> List[str]:
        """Get all unique questions in the tree."""
        questions = set()
        
        def traverse(node):
            if node and node.is_question:
                questions.add(node.content)
                traverse(node.yes_node)
                traverse(node.no_node)
        
        traverse(self.root_node)
        return list(questions)
