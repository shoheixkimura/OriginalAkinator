#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GUI version of the Akinator game using Tkinter.
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
import os
import sys
from akinator import Akinator


class AkinatorGUI:
    """GUI implementation of the Akinator game."""
    
    def __init__(self, root):
        """Initialize the GUI."""
        self.root = root
        self.root.title("OriginalAkinator")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Set background color
        self.root.configure(bg="#f0f0f0")
        
        # Create the Akinator instance
        self.akinator = Akinator()
        
        # Create GUI elements
        self.create_widgets()
        
        # Start a new game
        self.start_new_game()
    
    def create_widgets(self):
        """Create the GUI widgets."""
        # Title label
        self.title_label = tk.Label(
            self.root,
            text="OriginalAkinator",
            font=("Arial", 24, "bold"),
            bg="#f0f0f0"
        )
        self.title_label.pack(pady=20)
        
        # Question frame
        self.question_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.question_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Question label
        self.question_label = tk.Label(
            self.question_frame,
            text="",
            font=("Arial", 14),
            wraplength=400,
            justify=tk.CENTER,
            bg="#f0f0f0"
        )
        self.question_label.pack(pady=20)
        
        # Buttons frame
        self.buttons_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.buttons_frame.pack(pady=20)
        
        # Yes button
        self.yes_button = tk.Button(
            self.buttons_frame,
            text="Yes",
            font=("Arial", 12),
            width=10,
            command=lambda: self.answer(True)
        )
        self.yes_button.grid(row=0, column=0, padx=10)
        
        # No button
        self.no_button = tk.Button(
            self.buttons_frame,
            text="No",
            font=("Arial", 12),
            width=10,
            command=lambda: self.answer(False)
        )
        self.no_button.grid(row=0, column=1, padx=10)
        
        # Restart button
        self.restart_button = tk.Button(
            self.root,
            text="Restart",
            font=("Arial", 12),
            width=10,
            command=self.start_new_game
        )
        self.restart_button.pack(pady=10)
    
    def start_new_game(self):
        """Start a new game."""
        self.akinator.start_game()
        self.update_question()
    
    def update_question(self):
        """Update the question or guess text."""
        current_text = self.akinator.get_current_question()
        
        if not self.akinator.is_question():
            current_text = f"I think you're thinking of: {current_text}"
        
        self.question_label.configure(text=current_text)
    
    def answer(self, is_yes):
        """Process the user's answer."""
        if not self.akinator.is_question():
            # This is a guess
            if is_yes:
                messagebox.showinfo("Correct!", "Yay! I guessed correctly!")
                self.ask_play_again()
            else:
                self.learn_new_item()
        else:
            # This is a question
            if not self.akinator.answer(is_yes):
                messagebox.showinfo("Unknown", "Hmm, I don't know what to guess based on your answers.")
                self.learn_new_item()
            else:
                self.update_question()
    
    def learn_new_item(self):
        """Learn a new item when the guess was incorrect."""
        correct_answer = simpledialog.askstring("What was it?", "What were you thinking of?")
        
        if correct_answer:
            distinguishing_question = simpledialog.askstring(
                "New Question",
                f"Please enter a yes/no question that would distinguish {correct_answer} from {self.akinator.get_current_question()}:"
            )
            
            if distinguishing_question:
                answer_for_correct = messagebox.askyesno(
                    "Answer",
                    f"For {correct_answer}, is the answer to '{distinguishing_question}' yes?"
                )
                
                # Create new nodes (simplified version)
                last_guess = self.akinator.get_current_question()
                
                # Store the last node content
                if self.akinator.current_node:
                    self.akinator.current_node.content = distinguishing_question
                    self.akinator.current_node.is_question = True
                    
                    # Create new leaf nodes
                    from akinator import AkinatorNode
                    correct_node = AkinatorNode(correct_answer, False)
                    wrong_node = AkinatorNode(last_guess, False)
                    
                    if answer_for_correct:
                        self.akinator.current_node.yes_node = correct_node
                        self.akinator.current_node.no_node = wrong_node
                    else:
                        self.akinator.current_node.yes_node = wrong_node
                        self.akinator.current_node.no_node = correct_node
                
                # Save the updated tree
                self.akinator.save_tree()
                
                messagebox.showinfo("Thank you", "Thanks for teaching me something new!")
        
        self.ask_play_again()
    
    def ask_play_again(self):
        """Ask if the user wants to play again."""
        play_again = messagebox.askyesno("Play Again", "Do you want to play again?")
        
        if play_again:
            self.start_new_game()
        else:
            self.root.destroy()


def main():
    """Main function to run the GUI."""
    root = tk.Tk()
    app = AkinatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    # Add the src directory to the path
    src_dir = os.path.dirname(os.path.abspath(__file__))
    if src_dir not in sys.path:
        sys.path.append(src_dir)
    
    main()
