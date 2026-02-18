# Fianco AI

This project is a Python implementation of the Fianco board game developed as part of the **Intelligent Search and Games** course.
It features an AI opponent built using classical adversarial search techniques and optimization heuristics.

## Overview

The system implements the full game logic for Fianco, including board representation, move validation, and interactive gameplay.
An AI agent selects moves through depth-limited search enhanced with pruning, move ordering, and evaluation heuristics.

The goal of the project is to apply and study search-based AI techniques in a two-player zero-sum game setting.

## AI Techniques Implemented

The AI combines several core concepts from the course:

* Negamax search (Minimax variant for zero-sum games)
* Alpha-Beta pruning for search efficiency
* Iterative deepening for time-aware decision making
* Transposition tables to reuse evaluated states
* Zobrist hashing for fast board hashing
* Killer move heuristic for improved move ordering
* History heuristic to prioritize effective past moves
* Quiescence search to handle tactical positions

These techniques allow deeper exploration of the game tree while maintaining reasonable computation time.

## Evaluation Function

Board positions are evaluated using a heuristic that considers:

* Difference in piece count between players
* Advancement of pieces toward the opponent’s side
* Stability of positions through capture-aware analysis

## Project Structure

* `main.py` — game loop and interaction
* `board.py` — board state, rules, and move generation
* `ai.py` — search algorithms and evaluation logic

## How to Run

Run the game:

```
python main.py
```

Then choose a side:

* Press **W** to play as White
* Press **B** to play as Black
