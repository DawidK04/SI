import math
import heapq
import tkinter as tk
from tkinter import filedialog, messagebox


class PathfindingApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Wizualizator algorytmów: Best First / Dijkstra / A*")
    self.root.geometry("950x750")

    self.nodes = {}
    self.adj = {}
    self.screen_coords = {}
    self.start_node = None
    self.goal_node = None

    self.algorithm = tk.StringVar(value="A*")
    self.pq = []
    self.g_cost = {}
    self.came_from = {}
    self.visited = set()
    self.frontier = set()
    self.path = []
    self.is_running = False

    self.create_widgets()

  def create_widgets(self):
    control_frame = tk.Frame(
        self.root, width=280, bg="#f0f0f0", padx=10, pady=10
    )
    control_frame.pack(side=tk.LEFT, fill=tk.Y)

    canvas_frame = tk.Frame(self.root, bg="white")
    canvas_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

    tk.Button(
        control_frame,
        text="📁 Wczytaj plik grafu (.txt)",
        command=self.load_file,
        bg="#4CAF50",
        fg="white",
        font=("Arial", 10, "bold"),
        cursor="hand2",
    ).pack(fill=tk.X, pady=5)

    tk.Label(
        control_frame,
        text="Wybierz algorytm:",
        bg="#f0f0f0",
        font=("Arial", 10, "bold"),
    ).pack(anchor="w", pady=(15, 5))

    for algo in ["Best First Search", "Dijkstra", "A*"]:
      tk.Radiobutton(
          control_frame,
          text=algo,
          variable=self.algorithm,
          value=algo,
          bg="#f0f0f0",
          font=("Arial", 9),
      ).pack(anchor="w")

    tk.Button(
        control_frame,
        text="🔄 Reset / Inicjalizacja",
        command=self.init_search,
        bg="#2196F3",
        fg="white",
        font=("Arial", 9, "bold"),
        cursor="hand2",
    ).pack(fill=tk.X, pady=(20, 5))

    tk.Button(
        control_frame,
        text="▶ Następny krok",
        command=self.step_search,
        bg="#FF9800",
        fg="white",
        font=("Arial", 9, "bold"),
        cursor="hand2",
    ).pack(fill=tk.X, pady=2)

    tk.Button(
        control_frame,
        text="▶▶ Start automatyczny",
        command=self.toggle_auto_run,
        bg="#009688",
        fg="white",
        font=("Arial", 9, "bold"),
        cursor="hand2",
    ).pack(fill=tk.X, pady=2)

    self.status_label = tk.Label(
        control_frame,
        text=(
            "Status: Oczekiwanie na plik...\nKoszt ścieżki: -\nOdwiedzonych:"
            " 0"
        ),
        bg="#f0f0f0",
        justify=tk.LEFT,
        font=("Arial", 9, "bold"),
        fg="#333",
    )
    self.status_label.pack(anchor="w", pady=20)

    self.canvas = tk.Canvas(canvas_frame, bg="white")
    self.canvas.pack(expand=True, fill=tk.BOTH)
    self.canvas.bind("<Button-1>", self.on_canvas_click)
    self.canvas.bind("<Configure>", lambda e: self.redraw())

  def load_file(self):
    self.is_running = False
    file_path = filedialog.askopenfilename(
        title="Wybierz plik z grafem", filetypes=[("Pliki tekstowe", "*.txt")]
    )
    if not file_path:
      return
    try:
      with open(file_path, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

      n = int(lines[0])
      self.nodes = {}
      self.adj = {}

      for i in range(1, n + 1):
        parts = list(map(float, lines[i].split()))
        self.nodes[i] = (parts[0], parts[1])

      for i in range(1, n + 1):
        parts = list(map(int, lines[n + i].split()))
        count = parts[0]
        neighbors = parts[1 : count + 1]
        self.adj[i] = neighbors

      self.start_node = 1
      self.goal_node = n
      self.init_search()
      self.redraw()
      messagebox.showinfo(
          "Sukces",
          f"Wczytano graf o {n} wierzchołkach!\nStart: 1, Cel: {n}",
      )
    except Exception as e:
      messagebox.showerror("Błąd", f"Nie udało się wczytać pliku:\n{str(e)}")

  def on_canvas_click(self, event):
    if not self.nodes:
      return
    self.is_running = False
    clicked_x, clicked_y = event.x, event.y
    min_dist = float("inf")
    closest_node = None
    for node_id, (nx, ny) in self.screen_coords.items():
      dist = math.hypot(nx - clicked_x, ny - clicked_y)
      if dist < min_dist and dist < 25:
        min_dist = dist
        closest_node = node_id

    if closest_node:
      if self.start_node is None or (
          self.start_node and self.goal_node and self.start_node != closest_node
      ):
        self.start_node = closest_node
        self.goal_node = None
      elif self.start_node and self.goal_node is None:
        self.goal_node = closest_node
      else:
        self.start_node = closest_node
        self.goal_node = None
      self.init_search()
      self.redraw()

  def redraw(self):
    self.canvas.delete("all")
    if not self.nodes:
      return

    width = self.canvas.winfo_width()
    height = self.canvas.winfo_height()
    if width < 10:
      width, height = 650, 650

    xs = [coord[0] for coord in self.nodes.values()]
    ys = [coord[1] for coord in self.nodes.values()]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    margin = 50
    avail_w = width - 2 * margin
    avail_h = height - 2 * margin

    span_x = max_x - min_x if max_x != min_x else 1
    span_y = max_y - min_y if max_y != min_y else 1

    self.screen_coords = {}
    for node_id, (x, y) in self.nodes.items():
      sx = margin + (x - min_x) / span_x * avail_w
      sy = height - (margin + (y - min_y) / span_y * avail_h)
      self.screen_coords[node_id] = (sx, sy)

    drawn_edges = set()
    for u, neighbors in self.adj.items():
      ux, uy = self.screen_coords[u]
      for v in neighbors:
        if v in self.screen_coords and (v, u) not in drawn_edges:
          vx, vy = self.screen_coords[v]
          self.canvas.create_line(
              ux, uy, vx, vy, fill="#d0d0d0", width=1.5, smooth=True
          )
          drawn_edges.add((u, v))

    if len(self.path) > 1:
      for i in range(len(self.path) - 1):
        u, v = self.path[i], self.path[i + 1]
        if u in self.screen_coords and v in self.screen_coords:
          ux, uy = self.screen_coords[u]
          vx, vy = self.screen_coords[v]
          self.canvas.create_line(ux, uy, vx, vy, fill="#9c27b0", width=4)

    r = 8
    for node_id, (sx, sy) in self.screen_coords.items():
      color = "#e0e0e0"
      if node_id in self.visited:
        color = "#90CAF9"
      if node_id in self.frontier:
        color = "#FFEE58"
      if node_id == self.start_node:
        color = "#4CAF50"
      if node_id == self.goal_node:
        color = "#F44336"
      if node_id in self.path:
        color = "#9C27B0"

      self.canvas.create_oval(
          sx - r, sy - r, sx + r, sy + r, fill=color, outline="#333", width=1.5
      )
      self.canvas.create_text(
          sx,
          sy - 14,
          text=str(node_id),
          font=("Arial", 8, "bold"),
          fill="#333",
      )

  def init_search(self):
    self.is_running = False
    if not self.nodes or self.start_node is None:
      return

    self.visited = set()
    self.frontier = {self.start_node}
    self.g_cost = {self.start_node: 0.0}
    self.came_from = {self.start_node: None}
    self.path = []
    self.pq = []

    def heuristic(u, v):
      ux, uy = self.nodes[u]
      vx, vy = self.nodes[v]
      return math.hypot(ux - vx, uy - vy)

    algo = self.algorithm.get()
    f_start = 0.0
    if algo in ["Best First Search", "A*"] and self.goal_node:
      f_start = heuristic(self.start_node, self.goal_node)

    heapq.heappush(self.pq, (f_start, self.start_node))
    self.update_status(
        "Gotowy do wyszukiwania.", path_cost="-", visited_count=0
    )
    self.redraw()

  def toggle_auto_run(self):
    if not self.is_running:
      if self.path or not self.pq:
        self.init_search()
      self.is_running = True
      self.auto_step()
    else:
      self.is_running = False

  def auto_step(self):
    if not self.is_running:
      return
    if not self.pq or self.path:
      self.is_running = False
      return

    self.step_search()

    if self.path or not self.pq:
      self.is_running = False
      return

    self.root.after(400, self.auto_step)

  def step_search(self):
    if not self.pq:
      self.update_status(
          "Brak ścieżki lub koniec przeszukiwania!",
          visited_count=len(self.visited),
      )
      self.is_running = False
      return

    def heuristic(u, v):
      ux, uy = self.nodes[u]
      vx, vy = self.nodes[v]
      return math.hypot(ux - vx, uy - vy)

    algo = self.algorithm.get()
    current_f, current = heapq.heappop(self.pq)

    if current in self.visited:
      if self.is_running:
        self.auto_step()
      else:
        self.step_search()
      return

    self.visited.add(current)
    if current in self.frontier:
      self.frontier.remove(current)

    if current == self.goal_node:
      self.reconstruct_path()
      self.is_running = False
      return

    for neighbor in self.adj.get(current, []):
      if neighbor in self.visited:
        continue

      ux, uy = self.nodes[current]
      vx, vy = self.nodes[neighbor]
      edge_cost = math.hypot(ux - vx, uy - vy)
      new_g = self.g_cost[current] + edge_cost

      if neighbor not in self.g_cost or new_g < self.g_cost[neighbor]:
        self.g_cost[neighbor] = new_g
        self.came_from[neighbor] = current

        h = heuristic(neighbor, self.goal_node) if self.goal_node else 0.0
        if algo == "Best First Search":
          f = h
        elif algo == "Dijkstra":
          f = new_g
        elif algo == "A*":
          f = new_g + h

        heapq.heappush(self.pq, (f, neighbor))
        self.frontier.add(neighbor)

    self.redraw()
    self.update_status(
        f"Przetwarzanie wierzchołka: {current}",
        visited_count=len(self.visited),
    )

  def reconstruct_path(self):
    current = self.goal_node
    self.path = []
    total_cost = 0.0
    while current is not None:
      self.path.append(current)
      prev = self.came_from.get(current)
      if prev is not None:
        ux, uy = self.nodes[current]
        vx, vy = self.nodes[prev]
        total_cost += math.hypot(ux - vx, uy - vy)
      current = prev
    self.path.reverse()
    self.redraw()
    self.update_status(
        "🎉 ZNALAZIONO ŚCIEŻKĘ!",
        path_cost=f"{total_cost:.2f}",
        visited_count=len(self.visited),
    )

  def update_status(self, text, path_cost="-", visited_count=0):
    self.status_label.config(
        text=(
            f"Status: {text}\nKoszt ścieżki:"
            f" {path_cost}\nOdwiedzonych węzłów: {visited_count}"
        )
    )


if __name__ == "__main__":
  root = tk.Tk()
  app = PathfindingApp(root)
  root.mainloop()
