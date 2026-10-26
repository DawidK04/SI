#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import os
from collections import deque

if os.name == 'nt':
    os.system('')

COLOR_RED = "\033[1;31m"      
COLOR_GREEN = "\033[1;32m"    
COLOR_YELLOW = "\033[1;33m"   
COLOR_BLUE = "\033[1;34m"     
COLOR_RESET = "\033[0m"       

CHAR_DIRECTIONS = {
    '+': ['UP', 'DOWN', 'LEFT', 'RIGHT'],
    '┼': ['UP', 'DOWN', 'LEFT', 'RIGHT'],
    '|': ['UP', 'DOWN'],
    '│': ['UP', 'DOWN'],
    '-': ['LEFT', 'RIGHT'],
    '─': ['LEFT', 'RIGHT'],
    ' ': [],
    '┌': ['DOWN', 'RIGHT'],
    '┐': ['DOWN', 'LEFT'],
    '└': ['UP', 'RIGHT'],
    '┘': ['UP', 'LEFT'],
    '├': ['UP', 'DOWN', 'RIGHT'],
    '┤': ['UP', 'DOWN', 'LEFT'],
    '┬': ['DOWN', 'LEFT', 'RIGHT'],
    '┴': ['UP', 'LEFT', 'RIGHT'],
    '╷': ['UP'],
    '╵': ['DOWN'],
    '╴': ['LEFT'],
    '╶': ['RIGHT'],
}

def get_allowed_moves(char):
    return CHAR_DIRECTIONS.get(char, ['UP', 'DOWN', 'LEFT', 'RIGHT'])

def can_move(grid, r1, c1, r2, c2):
    rows = len(grid)
    cols = len(grid[0])
    if not (0 <= r2 < rows and 0 <= c2 < cols):
        return False
    
    char1 = grid[r1][c1]
    char2 = grid[r2][c2]
    
    dr = r2 - r1
    dc = c2 - c1
    
    dir1 = None
    if dr == -1: dir1 = 'UP'
    elif dr == 1: dir1 = 'DOWN'
    elif dc == -1: dir1 = 'LEFT'
    elif dc == 1: dir1 = 'RIGHT'
    
    dir2 = None
    if dr == 1: dir2 = 'UP'
    elif dr == -1: dir2 = 'DOWN'
    elif dc == 1: dir2 = 'LEFT'
    elif dc == -1: dir2 = 'RIGHT'
    
    moves1 = get_allowed_moves(char1)
    moves2 = get_allowed_moves(char2)
    
    return (dir1 in moves1) and (dir2 in moves2)

def print_map(grid, start, end, visited, queue_set, current=None):
    rows = len(grid)
    cols = len(grid[0])
    
    frame_lines = ["\033[H"]
    
    for r in range(rows):
        line_str = ""
        for c in range(cols):
            char = grid[r][c]
            pos = (r, c)
            
            if pos == start:
                line_str += f"{COLOR_RED}{char}{COLOR_RESET}"
            elif pos == end:
                line_str += f"{COLOR_BLUE}{char}{COLOR_RESET}"
            elif pos == current:
                line_str += f"{COLOR_YELLOW}{char}{COLOR_RESET}"
            elif pos in visited:
                line_str += f"{COLOR_GREEN}{char}{COLOR_RESET}"
            elif pos in queue_set:
                line_str += f"{COLOR_YELLOW}{char}{COLOR_RESET}"
            else:
                line_str += char
        frame_lines.append(line_str)
        
    sys.stdout.write("\n".join(frame_lines) + "\n")
    sys.stdout.flush()
    time.sleep(0.04)

def print_grid_with_axes(grid):
    rows = len(grid)
    cols = len(grid[0])
    
    tens_row = "      "
    units_row = "      "
    for c in range(cols):
        tens_row += str(c // 10) if c >= 10 else " "
        units_row += str(c % 10)
    
    print(tens_row)
    print(units_row)
    print("      " + "-" * cols)
    
    for r in range(rows):
        row_str = "".join(grid[r])
        print(f"{r:3d} | {row_str}")

def solve_maze(grid, start, end, algorithm='BFS'):
    if algorithm == 'BFS':
        frontier = deque([start])
    else:
        frontier = [start]
        
    came_from = {start: None}
    visited = set()
    queue_set = {start}
    
    found = False
    steps = 0
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    print("\033[2J\033[H", end="")
    
    while frontier:
        if algorithm == 'BFS':
            current = frontier.popleft()
        else:
            current = frontier.pop()
            
        queue_set.discard(current)
        
        if current in visited:
            continue
            
        visited.add(current)
        steps += 1
        
        print_map(grid, start, end, visited, queue_set, current)
        
        if current == end:
            found = True
            break
            
        r, c = current
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            next_pos = (nr, nc)
            
            if can_move(grid, r, c, nr, nc):
                if next_pos not in visited and next_pos not in queue_set:
                    came_from[next_pos] = current
                    frontier.append(next_pos)
                    queue_set.add(next_pos)
                    
    path = []
    if found:
        curr = end
        while curr is not None:
            path.append(curr)
            curr = came_from.get(curr)
        path.reverse()
        
    return found, steps, path

def main():
    if len(sys.argv) < 2:
        print("Użycie: python maze_solver.py <sciezka_do_mapy>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Błąd odczytu pliku: {e}")
        sys.exit(1)
        
    grid = [list(line.rstrip('\r\n')) for line in lines]
    max_cols = max(len(row) for row in grid)
    for row in grid:
        if len(row) < max_cols:
            row.extend([' '] * (max_cols - len(row)))
            
    print(f"Wczytano mapę: {len(grid)} wierszy, {max_cols} kolumn.\n")
    print("Podgląd mapy początkowej z osiami współrzędnych:")
    print_grid_with_axes(grid)
    print()
        
    try:
        print("Wprowadź współrzędne w formacie (wiersz, kolumna), numerowane od 0.")
        start_r = int(input("Wiersz startowy: "))
        start_c = int(input("Kolumna startowa: "))
        end_r = int(input("Wiersz końcowy: "))
        end_c = int(input("Kolumna końcowa: "))
        algo = input("Wybierz algorytm [BFS / DFS]: ").strip().upper()
        if algo not in ['BFS', 'DFS']:
            algo = 'BFS'
    except ValueError:
        print("Błąd: Wprowadzono niepoprawne współrzędne.")
        sys.exit(1)
        
    start = (start_r, start_c)
    end = (end_r, end_c)
    
    print("\nStart za 1 sekundę...")
    time.sleep(1)
    
    found, steps, path = solve_maze(grid, start, end, algo)
    
    print("\n" + "="*45)
    if found:
        print(f" [SUKCES] Znaleziono ścieżkę!")
        print(f" Liczba wykonanych kroków (odwiedzonych węzłów): {steps}")
        print(f" Długość znalezionej ścieżki: {len(path)} kroków.")
    else:
        print(f" [BRAK WYNIKU] Nie udało się znaleźć ścieżki między wybranymi punktami.")
        print(f" Liczba wykonanych kroków: {steps}")
    print("="*45)

if __name__ == "__main__":
    main()
