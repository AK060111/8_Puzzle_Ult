from collections import deque
import random
import tkinter as tk
import heapq

# Rules
MOVES = [
    (-3, lambda i: i >= 3),
    (3, lambda i: i <= 5),
    (-1, lambda i: i % 3 != 0),
    (1, lambda i: i % 3 != 2),
]


def count_inversions(state):
    arr = [x for x in state if x != 0]
    count = 0

    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if arr[i] > arr[j]:
                count += 1

    return count


def is_solvable(start, goal):
    return (count_inversions(start) - count_inversions(goal)) % 2 == 0


def random_state():
    state = list(range(9))
    random.shuffle(state)
    return state


def generate_puzzle():
    while True:
        start = random_state()
        goal = random_state()

        if start != goal and is_solvable(start, goal):
            return start, goal


def get_neighbors(state):
    zero = state.index(0)

    for move, valid in MOVES:
        if valid(zero):
            new_zero = zero + move
            new_state = list(state)
            new_state[zero], new_state[new_zero] = new_state[new_zero], new_state[zero]
            yield tuple(new_state)


def build_path(parent, node):
    path = []

    while node is not None:
        path.append(list(node))
        node = parent[node]

    return path[::-1]
def misplaced_tiles(state, goal):
    count = 0

    for s, g in zip(state, goal):
        if s != 0 and s != g:
            count += 1

    return count


# Aglorithm
def bfs(start, goal):
    start = tuple(start)
    goal = tuple(goal)

    queue = deque([start])
    parent = {start: None}
    expanded = 0

    while queue:
        current = queue.popleft()
        expanded += 1

        if current == goal:
            return build_path(parent, current), expanded

        for neighbor in get_neighbors(current):
            if neighbor not in parent:
                parent[neighbor] = current
                queue.append(neighbor)

    return None, expanded


def dfs(start, goal, max_depth=1000):
    start = tuple(start)
    goal = tuple(goal)

    stack = [(start, 0)]
    parent = {start: None}
    expanded = 0

    while stack:
        current, depth = stack.pop()
        expanded += 1

        if current == goal:
            return build_path(parent, current), expanded

        if depth >= max_depth:
            continue

        for neighbor in get_neighbors(current):
            if neighbor not in parent:
                parent[neighbor] = current
                stack.append((neighbor, depth + 1))

    return None, expanded


def depth_limited_search(start, goal, limit):
    start = tuple(start)
    goal = tuple(goal)

    stack = [(start, 0)]
    parent = {start: None}
    expanded = 0

    while stack:
        current, depth = stack.pop()
        expanded += 1

        if current == goal:
            return build_path(parent, current), expanded, False

        if depth >= limit:
            continue

        for neighbor in get_neighbors(current):
            if neighbor not in parent:
                parent[neighbor] = current
                stack.append((neighbor, depth + 1))

    return None, expanded, True


def ids(start, goal, max_depth=50):
    total_expanded = 0

    for depth in range(max_depth + 1):
        path, expanded, cutoff = depth_limited_search(start, goal, depth)
        total_expanded += expanded

        if path is not None:
            return path, total_expanded

    return None, total_expanded
def ucs(start, goal):
    start = tuple(start)
    goal = tuple(goal)

    frontier = []
    heapq.heappush(frontier, (0, start))

    parent = {start: None}
    cost_so_far = {start: 0}
    expanded = 0

    while frontier:
        current_cost, current = heapq.heappop(frontier)
        expanded += 1

        if current == goal:
            return build_path(parent, current), expanded

        for neighbor in get_neighbors(current):
            step_cost = misplaced_tiles(neighbor, goal)
            new_cost = current_cost + step_cost

            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                parent[neighbor] = current
                heapq.heappush(frontier, (new_cost, neighbor))

    return None, expanded


def greedy_search(start, goal):
    start = tuple(start)
    goal = tuple(goal)

    frontier = []
    heapq.heappush(frontier, (misplaced_tiles(start, goal), start))

    parent = {start: None}
    reached = set()
    expanded = 0

    while frontier:
        current_h, current = heapq.heappop(frontier)

        if current in reached:
            continue

        expanded += 1

        if current == goal:
            return build_path(parent, current), expanded

        reached.add(current)

        for neighbor in get_neighbors(current):
            in_frontier = neighbor in parent and neighbor not in reached

            if neighbor not in reached and not in_frontier:
                parent[neighbor] = current
                h = misplaced_tiles(neighbor, goal)
                heapq.heappush(frontier, (h, neighbor))

    return None, expanded

ALGORITHMS = {
    "BFS": bfs,
    "DFS": dfs,
    "IDS": ids,
    "UCS": ucs,
    "Greedy": greedy_search,
}


# GUI
class PuzzleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("8 Puzzle Search")
        self.root.geometry("980x720")
        self.root.configure(bg="#f4f6f8")
        self.root.resizable(False, False)

        self.start, self.goal = generate_puzzle()
        self.selected_algorithm = tk.StringVar(value="BFS")
        self.animation_job = None

        self.start_cells = []
        self.goal_cells = []

        self.setup_ui()
        self.draw_main_grids()
        self.paused = False
        self.current_path = []
        self.current_index = 0

    # UI
    def setup_ui(self):
        container = tk.Frame(self.root, bg="#f4f6f8")
        container.pack(fill="both", expand=True, padx=24, pady=20)

        self.left_panel(container)
        self.control_panel(container)
        self.states_panel(container)

    def panel(self, parent):
        return tk.Frame(
            parent,
            bg="white",
            bd=0,
            highlightthickness=1,
            highlightbackground="#d9dee3"
        )

    def left_panel(self, parent):
        left = self.panel(parent)
        left.pack(side="left", fill="y", padx=(0, 18))

        self.title(left, "Start").pack(pady=(18, 8))
        start_frame = tk.Frame(left, bg="white")
        start_frame.pack(padx=28)
        self.start_cells = self.create_grid(start_frame, big=True)

        self.title(left, "Goal").pack(pady=(28, 8))
        goal_frame = tk.Frame(left, bg="white")
        goal_frame.pack(padx=28, pady=(0, 20))
        self.goal_cells = self.create_grid(goal_frame, big=True)

    def control_panel(self, parent):
        control = self.panel(parent)
        control.pack(side="left", fill="y", padx=(0, 18))

        self.title(control, "Algorithm").pack(pady=(20, 10))

        # Vùng chọn thuật toán có scroll riêng.
        # Khi thêm nhiều thuật toán, phần này sẽ cuộn được
        # còn các nút Solve/New/Pause/Resume vẫn cố định bên dưới.
        algo_area = tk.Frame(control, bg="white")
        algo_area.pack(fill="x", padx=12, pady=(0, 8))

        self.algo_canvas = tk.Canvas(
            algo_area,
            width=155,
            height=235,
            bg="white",
            highlightthickness=0
        )
        self.algo_canvas.pack(side="left", fill="x", expand=True)

        algo_scrollbar = tk.Scrollbar(
            algo_area,
            orient="vertical",
            command=self.algo_canvas.yview
        )
        algo_scrollbar.pack(side="right", fill="y")

        self.algo_canvas.configure(yscrollcommand=algo_scrollbar.set)

        self.algo_container = tk.Frame(self.algo_canvas, bg="white")
        self.algo_canvas_window = self.algo_canvas.create_window(
            (0, 0),
            window=self.algo_container,
            anchor="nw"
        )

        self.algo_container.bind(
            "<Configure>",
            lambda e: self.algo_canvas.configure(
                scrollregion=self.algo_canvas.bbox("all")
            )
        )

        self.algo_canvas.bind(
            "<Configure>",
            lambda e: self.algo_canvas.itemconfigure(
                self.algo_canvas_window,
                width=e.width
            )
        )

        self.algo_canvas.bind(
            "<Enter>",
            lambda e: self.root.bind_all("<MouseWheel>", self.scroll_algorithm_mouse)
        )
        self.algo_canvas.bind(
            "<Leave>",
            lambda e: self.root.unbind_all("<MouseWheel>")
        )

        for name in ALGORITHMS:
            tk.Radiobutton(
                self.algo_container,
                text=name,
                value=name,
                variable=self.selected_algorithm,
                font=("Arial", 14, "bold"),
                bg="white",
                activebackground="white",
                selectcolor="#e8f0fe",
                indicatoron=False,
                width=12,
                pady=7
            ).pack(fill="x", padx=8, pady=5)

        buttons = tk.Frame(control, bg="white")
        buttons.pack(fill="x", padx=20, pady=(8, 0))

        tk.Button(
            buttons,
            text="Solve",
            font=("Arial", 15, "bold"),
            width=12,
            bg="#2f80ed",
            fg="white",
            activebackground="#1c6dd0",
            activeforeground="white",
            relief="flat",
            command=self.solve
        ).pack(pady=(0, 8), ipady=6)

        tk.Button(
            buttons,
            text="New Puzzle",
            font=("Arial", 13, "bold"),
            width=12,
            bg="#e9eef5",
            fg="#222",
            activebackground="#dce3ec",
            relief="flat",
            command=self.new_puzzle
        ).pack(pady=6, ipady=5)

        tk.Button(
            buttons,
            text="Pause",
            font=("Arial", 13, "bold"),
            width=12,
            bg="#f4b400",
            fg="white",
            relief="flat",
            command=self.pause_animation
        ).pack(pady=6, ipady=5)

        tk.Button(
            buttons,
            text="Resume",
            font=("Arial", 13, "bold"),
            width=12,
            bg="#34a853",
            fg="white",
            relief="flat",
            command=self.resume_animation
        ).pack(pady=6, ipady=5)

        self.info_label = tk.Label(
            control,
            text="Steps: 0\nNodes: 0",
            font=("Arial", 13),
            bg="white",
            justify="left"
        )
        self.info_label.pack(side="bottom", pady=(8, 18))

    def states_panel(self, parent):
        states = self.panel(parent)
        states.pack(side="left", fill="both", expand=True)

        self.title(states, "States").pack(pady=(18, 8))

        canvas_area = tk.Frame(states, bg="white")
        canvas_area.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        self.canvas = tk.Canvas(
            canvas_area,
            width=300,
            height=520,
            bg="white",
            highlightthickness=0
        )
        self.canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(
            canvas_area,
            orient="vertical",
            command=self.canvas.yview
        )
        scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.states_container = tk.Frame(self.canvas, bg="white")
        self.canvas_window = self.canvas.create_window(
            (150, 0),
            window=self.states_container,
            anchor="n"
        )

        self.states_container.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.bind(
            "<Enter>",
            lambda e: self.root.bind_all("<MouseWheel>", self.scroll_mouse)
        )
        self.canvas.bind(
            "<Leave>",
            lambda e: self.root.unbind_all("<MouseWheel>")
        )

    def title(self, parent, text):
        return tk.Label(
            parent,
            text=text,
            font=("Arial", 20, "bold"),
            bg="white",
            fg="#111"
        )

    # Table(Grid)
    def create_grid(self, parent, big=False):
        cells = []

        font_size = 22 if big else 16
        width = 4 if big else 4
        height = 2 if big else 2
        border = 3 if big else 2

        for i in range(9):
            cell = tk.Label(
                parent,
                width=width,
                height=height,
                font=("Arial", font_size, "bold"),
                bg="#f8fafc",
                fg="#111",
                bd=border,
                relief="solid"
            )

            cell.grid(row=i // 3, column=i % 3)
            cells.append(cell)

        return cells

    def draw_grid(self, cells, state):
        for cell, value in zip(cells, state):
            cell.config(text=" " if value == 0 else str(value))

    def draw_main_grids(self):
        self.draw_grid(self.start_cells, self.start)
        self.draw_grid(self.goal_cells, self.goal)

    def draw_state_card(self, state):
        frame = tk.Frame(self.states_container, bg="white")
        frame.pack(pady=8)

        cells = self.create_grid(frame, big=False)
        self.draw_grid(cells, state)

    # Actions
    def clear_states(self):

        self.paused = False

        if self.animation_job:
            self.root.after_cancel(self.animation_job)
            self.animation_job = None

        for widget in self.states_container.winfo_children():
            widget.destroy()

        self.canvas.yview_moveto(0)

    def solve(self):

        self.clear_states()

        algo_name = self.selected_algorithm.get()
        search = ALGORITHMS[algo_name]

        result, nodes = search(self.start, self.goal)

        if result is None:
            self.info_label.config(
                text=f"Steps: Not found\nNodes: {nodes}"
            )

            return

        self.current_path = result
        self.current_index = 0
        self.paused = False

        self.info_label.config(
            text=f"Steps: {len(result) - 1}\nNodes: {nodes}"
        )

        self.show_states()

    def show_states(self):

        if self.paused:
            return

        if self.current_index >= len(self.current_path):
            return

        self.draw_state_card(
            self.current_path[self.current_index]
        )

        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

        self.current_index += 1

        self.animation_job = self.root.after(
            250,
            self.show_states
        )

    def new_puzzle(self):
        self.clear_states()
        self.start, self.goal = generate_puzzle()
        self.draw_main_grids()
        self.info_label.config(text="Steps: 0\nNodes: 0")

    def scroll_algorithm_mouse(self, event):
        self.algo_canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )

    def scroll_mouse(self, event):
        self.canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )

    def pause_animation(self):

        self.paused = True

        if self.animation_job:
            self.root.after_cancel(self.animation_job)
            self.animation_job = None

    def resume_animation(self):

        if not self.paused:
            return

        self.paused = False
        self.show_states()

if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleApp(root)
    root.mainloop()
