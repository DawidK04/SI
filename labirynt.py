import sys
import time
import os
from collections import deque

COLOR_DEFAULT = "\033[0m"
COLOR_START = "\033[1;31m"   
COLOR_VISITED = "\033[1;32m" 
COLOR_QUEUE = "\033[1;33m"   
COLOR_END = "\033[1;34m"     

MOVES_MAP = {
    '+': [(-1, 0), (1, 0), (0, 1), (0, -1)], 
    '│': [(-1, 0), (1, 0)],                   
    '─': [(0, 1), (0, -1)],                  
    ' ': [],                                 
    '┐': [(1, 0), (0, -1)],                  
    '┘': [(-1, 0), (0, -1)],                 
    '└': [(-1, 0), (0, 1)],                  
    '┌': [(1, 0), (0, 1)],                   
    '├': [(-1, 0), (1, 0), (0, -1)],          
    '┴': [(-1, 0), (0, 1), (0, -1)],          
    '┤': [(-1, 0), (1, 0), (0, 1)],          
    '┬': [(1, 0), (0, 1), (0, -1)],          
    '╵': [(-1, 0)],                          
    '╹': [(1, 0)],                           
    '╶': [(0, -1)],                          
    '╴': [(0, 1)]                            
}

def load_map(filepath):
    if not os.path.exists(filepath):
        print(f"Błąd: Plik {filepath} nie istnieje.")
        sys.exit(1)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [line.rstrip('\n\r') for line in f.readlines()]
    
    if not lines:
        print("Błąd: Mapa jest pusta.")
        sys.exit(1)
        
    max_len = max(len(line) for line in lines)
    grid = [list(line.ljust(max_len, ' ')) for line in lines]
    return grid

def print_map(grid, start, end, visited, queue_set):
    os.system('cls' if os.name == 'nt' else 'clear')
    rows = len(grid)
    cols = len(grid[0])
    
    print("    " + "".join(str(c % 10) for c in range(cols)))
    print("   +" + "-" * cols + "+")
    
    for r in range(rows):
        row_str = f"{r:2d} |"
        for c in range(cols):
            char = grid[r][c]
            pos = (r, c)
            
            if pos == start:
                row_str += f"{COLOR_START}{char}{COLOR_DEFAULT}"
            elif pos == end:
                row_str += f"{COLOR_END}{char}{COLOR_DEFAULT}"
            elif pos in visited:
                row_str += f"{COLOR_VISITED}{char}{COLOR_DEFAULT}"
            elif pos in queue_set:
                row_str += f"{COLOR_QUEUE}{char}{COLOR_DEFAULT}"
            else:
                row_str += f"{COLOR_DEFAULT}{char}"
        row_str += "|"
        print(row_str)
    print("   +" + "-" * cols + "+")

def is_valid_move(grid, r, c, nr, nc):
    rows = len(grid)
    cols = len(grid[0])
    if not (0 <= nr < rows and 0 <= nc < cols):
        return False
    
    char_curr = grid[r][c]
    char_next = grid[nr][nc]
    dr = nr - r
    dc = nc - c
    
    if (dr, dc) not in MOVES_MAP.get(char_curr, []):
        return False
    if (-dr, -dc) not in MOVES_MAP.get(char_next, []):
        return False
        
    return True

def solve_maze(grid, start, end, algorithm):
    rows = len(grid)
    cols = len(grid[0])
    
    if not (0 <= start[0] < rows and 0 <= start[1] < cols) or grid[start[0]][start[1]] == ' ':
        print("Błąd: Nieprawidłowe lub niedostępne pole startowe.")
        return None, 0
    if not (0 <= end[0] < rows and 0 <= end[1] < cols) or grid[end[0]][end[1]] == ' ':
        print("Błąd: Nieprawidłowe lub niedostępne pole końcowe.")
        return None, 0

    visited = set()
    parent = {start: None}
    
    if algorithm == 'BFS':
        container = deque([start]) 
    else:
        container = [start]        
        
    queue_set = {start}
    steps_count = 0
    
    while container:
        if algorithm == 'BFS':
            current = container.popleft()
        else:
            current = container.pop()
            
        queue_set.remove(current)
            
        if current in visited:
            continue
            
        visited.add(current)
        steps_count += 1
        
        print_map(grid, start, end, visited, queue_set)
        time.sleep(0.1)
        
        if current == end:
            path = []
            curr = end
            while curr is not None:
                path.append(curr)
                curr = parent.get(curr)
            path.reverse()
            return path, steps_count
            
        r, c = current
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            neighbor = (nr, nc)
            
            if is_valid_move(grid, r, c, nr, nc):
                if neighbor not in visited and neighbor not in queue_set:
                    parent[neighbor] = current
                    container.append(neighbor)
                    queue_set.add(neighbor)
                    
    return None, steps_count

def main():
    if len(sys.argv) < 2:
        print("Użycie: python labirynt.py <ścieżka_do_mapy>")
        sys.exit(1)
        
    filepath = sys.argv[1]
    grid = load_map(filepath)
    
    print(f"Wczytano mapę o rozmiarze: {len(grid)} wierszy x {len(grid[0])} kolumn.")
    
    try:
        start_r = int(input("Podaj wiersz startowy: "))
        start_c = int(input("Podaj kolumnę startową: "))
        end_r = int(input("Podaj wiersz końcowy: "))
        end_c = int(input("Podaj kolumnę końcową: "))
        algorithm = input("Podaj rodzaj algorytmu (BFS / DFS): ").strip().upper()
        
        if algorithm not in ['BFS', 'DFS']:
            print("Nieznany algorytm. Wybierz BFS lub DFS.")
            sys.exit(1)
            
    except ValueError:
        print("Błąd: Współrzędne muszą być liczbami całkowitymi.")
        sys.exit(1)
        
    start = (start_r, start_c)
    end = (end_r, end_c)
    
    path, steps = solve_maze(grid, start, end, algorithm)
    
    if path:
        print(f"\n[SUKCES] Znaleziono ścieżkę między wybranymi polami[cite: 1]!")
        print(f"Liczba wykonanych kroków (odwiedzonych węzłów): {steps}[cite: 1]")
        print(f"Długość znalezionej ścieżki: {len(path)} kroków.")
    else:
        print(f"\n[BRAK ŚCIEŻKI] Brak ścieżki między wybranymi polami[cite: 1].")
        print(f"Liczba wykonanych kroków: {steps}[cite: 1]")

if __name__ == '__main__':
    main()
