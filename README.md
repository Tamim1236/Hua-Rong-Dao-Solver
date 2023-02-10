# Hua-Rong-Dao-Solver

- In this Python program I implement search algorithms to solve the classic Huarong Dao sliding block puzzle game (a.k.a Klotski):
  https://chinesepuzzles.org/huarong-pass-sliding-block-puzzle/
  
- At each state of the board, I am generating successor states (future possible board configurations) to aid the search process.

- The implemented search algorithms are Depth First Search (DFS) and A*, where the admissible heuristic chosen for the A* algorithm is the Manhattan distance from the 
  2x2 main puzzle puece to the goal coordinate. 
