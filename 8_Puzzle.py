from collections import deque
import random
import tkinter as tk
import heapq
import math

# Rules
MOVES = [
    (-3, lambda i: i >= 3),
    (3, lambda i: i <= 5),
    (-1, lambda i: i % 3 != 0),
    (1, lambda i: i % 3 != 2),
]

# Limits for blind / heavy searches.
# 8-puzzle has at most 9! states, but if start and goal are not solvable
# with each other, we do not want the GUI to hang for too long.
MAX_EXPANDED_BLIND = 50000
MAX_EXPANDED_SEARCH = 200000
MAX_IDA_ITERATIONS = 80


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
    # Khong ep start/goal phai solvable.
    # Neu bai toan vo nghiem, thuat toan se bao Not found.
    while True:
        start = random_state()
        goal = random_state()

        if start != goal:
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

def manhattan_zero(state, goal):

    zero_state = state.index(0)

    zero_goal = goal.index(0)

    row1, col1 = divmod(zero_state, 3)

    row2, col2 = divmod(zero_goal, 3)

    return abs(row1 - row2) + abs(col1 - col2)

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


def bfs_limited(start, goal, max_expanded=MAX_EXPANDED_BLIND):
    start = tuple(start)
    goal = tuple(goal)

    queue = deque([start])
    parent = {start: None}
    expanded = 0

    while queue and expanded < max_expanded:
        current = queue.popleft()
        expanded += 1

        if current == goal:
            return build_path(parent, current), expanded

        for neighbor in get_neighbors(current):
            if neighbor not in parent:
                parent[neighbor] = current
                queue.append(neighbor)

    return None, expanded


def blind_start_search(start, goal):
    return bfs_limited(start, goal, MAX_EXPANDED_BLIND)


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

def astar(start, goal):
    start = tuple(start)
    goal = tuple(goal)

    frontier = []
    g_start = 0
    h_start = misplaced_tiles(start, goal)
    f_start = g_start + h_start

    heapq.heappush(frontier, (f_start, g_start, start))

    parent = {start: None}
    cost_so_far = {start: 0}
    reached = set()
    expanded = 0

    while frontier:
        current_f, current_g, current = heapq.heappop(frontier)

        if current in reached:
            continue

        expanded += 1

        if current == goal:
            return build_path(parent, current), expanded

        reached.add(current)

        for neighbor in get_neighbors(current):
            step_cost = misplaced_tiles(neighbor, goal)
            new_g = cost_so_far[current] + step_cost

            if neighbor in reached and new_g >= cost_so_far.get(neighbor, float("inf")):
                continue

            if new_g < cost_so_far.get(neighbor, float("inf")):
                cost_so_far[neighbor] = new_g
                parent[neighbor] = current

                h = misplaced_tiles(neighbor, goal)
                f = new_g + h

                heapq.heappush(frontier, (f, new_g, neighbor))

                if neighbor in reached:
                    reached.remove(neighbor)
    return None, expanded
def ida_star(start, goal):
    start = tuple(start)
    goal = tuple(goal)

    def search(path, g, bound):
        nonlocal expanded

        current = path[-1]
        h = misplaced_tiles(current, goal)
        f = g + h

        if f > bound:
            return f, None

        expanded += 1

        if current == goal:
            return f, build_path_from_list(path)

        min_bound = float("inf")

        for neighbor in get_neighbors(current):
            if neighbor in path:
                continue

            step_cost = misplaced_tiles(neighbor, goal)
            path.append(neighbor)

            result_bound, result_path = search(
                path,
                g + step_cost,
                bound
            )

            if result_path is not None:
                return result_bound, result_path

            if result_bound < min_bound:
                min_bound = result_bound

            path.pop()

        return min_bound, None

    def build_path_from_list(path):
        return [list(state) for state in path]

    bound = misplaced_tiles(start, goal)
    path = [start]
    expanded = 0

    iteration = 0

    while iteration < MAX_IDA_ITERATIONS and expanded < MAX_EXPANDED_SEARCH:
        iteration += 1
        new_bound, result_path = search(path, 0, bound)

        if result_path is not None:
            return result_path, expanded

        if new_bound == float("inf"):
            return None, expanded

        bound = new_bound

    return None, expanded
def simple_hill_climbing(start, goal):
    start = tuple(start)
    goal = tuple(goal)

    current = start
    current_value = manhattan_zero(current, goal)

    parent = {current: None}
    expanded = 0

    while True:
        expanded += 1

        if current == goal:
            return build_path(parent, current), expanded

        found_better = False

        for neighbor in get_neighbors(current):

            neighbor_value = manhattan_zero(neighbor, goal)

            # Hill Climbing: càng nhỏ càng tốt
            if neighbor_value < current_value:

                parent[neighbor] = current

                current = neighbor
                current_value = neighbor_value

                found_better = True
                break

        if not found_better:
            return None, expanded

def steepest_hill_climbing(start, goal):
    start = tuple(start)
    goal = tuple(goal)

    current = start

    parent = {current: None}
    expanded = 0

    while True:
        expanded += 1

        if current == goal:
            return build_path(parent, current), expanded

        current_value = manhattan_zero(current, goal)

        neighbors = list(get_neighbors(current))

        best_neighbor = None
        best_value = current_value

        for neighbor in neighbors:

            value = manhattan_zero(neighbor, goal)

            if value < best_value:
                best_value = value
                best_neighbor = neighbor

        # Không có trạng thái tốt hơn
        if best_neighbor is None:
            return None, expanded

        parent[best_neighbor] = current
        current = best_neighbor

def stochastic_hill_climbing(start, goal):
    start = tuple(start)
    goal = tuple(goal)

    current = start
    current_value = misplaced_tiles(current, goal)

    parent = {current: None}
    expanded = 0

    while True:
        expanded += 1

        if current == goal:
            return build_path(parent, current), expanded

        better_neighbors = []

        for neighbor in get_neighbors(current):
            neighbor_value = misplaced_tiles(neighbor, goal)

            # Cang nho cang tot
            if neighbor_value < current_value:
                better_neighbors.append(neighbor)

        # Khong con trang thai tot hon -> bi ket cuc bo
        if not better_neighbors:
            return None, expanded

        next_state = random.choice(better_neighbors)
        parent[next_state] = current
        current = next_state
        current_value = misplaced_tiles(current, goal)


def random_restart_hill_climbing(start, goal, max_restart=30):
    start = tuple(start)
    goal = tuple(goal)

    total_expanded = 0
    best_path = None
    best_value = float("inf")

    for i in range(max_restart):
        # Lan dau tien chay dung Start, cac lan sau tao diem bat dau moi
        if i == 0:
            current = start
        else:
            current = tuple(random_state())

        current_value = misplaced_tiles(current, goal)
        parent = {current: None}

        while True:
            total_expanded += 1

            if current == goal:
                return build_path(parent, current), total_expanded

            if current_value < best_value:
                best_value = current_value
                best_path = build_path(parent, current)

            better_neighbors = []

            for neighbor in get_neighbors(current):
                neighbor_value = misplaced_tiles(neighbor, goal)

                if neighbor_value < current_value:
                    better_neighbors.append(neighbor)

            # Bi ket -> restart
            if not better_neighbors:
                break

            next_state = random.choice(better_neighbors)
            parent[next_state] = current
            current = next_state
            current_value = misplaced_tiles(current, goal)

    return None, total_expanded

def local_beam_search(start, goal, k=3, max_steps=100):
    start = tuple(start)
    goal = tuple(goal)

    # Tao k trang thai ban dau: gom Start va k-1 trang thai ngau nhien giai duoc
    current_set = [start]

    while len(current_set) < k:
        state = tuple(random_state())

        if state != start:
            current_set.append(state)

    parent = {state: None for state in current_set}
    expanded = 0

    for _ in range(max_steps):
        neighbor_states = []

        for state in current_set:
            expanded += 1

            if state == goal:
                return build_path(parent, state), expanded

            for neighbor in get_neighbors(state):
                if neighbor not in parent:
                    parent[neighbor] = state
                    neighbor_states.append(neighbor)

        # Khong con lan can de di tiep
        if not neighbor_states:
            return None, expanded

        for neighbor in neighbor_states:
            if neighbor == goal:
                return build_path(parent, neighbor), expanded

        # Chon k trang thai tot nhat theo heuristic h
        neighbor_states.sort(
            key=lambda s: misplaced_tiles(s, goal)
        )
        current_set = neighbor_states[:k]

    return None, expanded


def blind_goal_search(start, goal):
    """
    Tim kiem mu tu Goal ve Start.
    Vi 8-puzzle co buoc di dao nguoc duoc, ta BFS tu goal den start,
    sau do dao nguoc path de hien thi dung chieu Start -> Goal.
    """
    path, expanded = bfs_limited(goal, start, MAX_EXPANDED_BLIND)

    if path is None:
        return None, expanded

    path.reverse()
    return path, expanded


def bidirectional_bfs(start, goal):
    """
    Tim kiem mu Start + Goal.
    Chay BFS hai dau: mot dau tu Start, mot dau tu Goal.
    Khi hai frontier gap nhau thi ghep duong di.
    """
    start = tuple(start)
    goal = tuple(goal)

    if start == goal:
        return [list(start)], 0

    frontier_start = deque([start])
    frontier_goal = deque([goal])

    parent_start = {start: None}
    parent_goal = {goal: None}

    expanded = 0

    def join_path(meet):
        path_start = build_path(parent_start, meet)       # Start -> meet
        path_goal = build_path(parent_goal, meet)         # Goal -> meet
        path_goal.reverse()                               # meet -> Goal
        return path_start + path_goal[1:]

    while frontier_start and frontier_goal and expanded < MAX_EXPANDED_BLIND:
        # Mo rong ben co frontier nho hon de giam so node phai duyet
        if len(frontier_start) <= len(frontier_goal):
            current = frontier_start.popleft()
            expanded += 1

            for neighbor in get_neighbors(current):
                if neighbor not in parent_start:
                    parent_start[neighbor] = current

                    if neighbor in parent_goal:
                        return join_path(neighbor), expanded

                    frontier_start.append(neighbor)
        else:
            current = frontier_goal.popleft()
            expanded += 1

            for neighbor in get_neighbors(current):
                if neighbor not in parent_goal:
                    parent_goal[neighbor] = current

                    if neighbor in parent_start:
                        return join_path(neighbor), expanded

                    frontier_goal.append(neighbor)

    return None, expanded


def simulated_annealing(start, goal, t0=100.0, t_min=0.001, alpha=0.97, max_steps=3000):
    """
    Simulated Annealing cho 8-puzzle.
    - Luon di tu Start -> Goal.
    - Neu neighbor tot hon thi nhan.
    - Neu neighbor xau hon thi van co the nhan theo xac suat exp(-delta / T).
    - T giam dan: T = alpha * T.
    """
    current = tuple(start)
    goal = tuple(goal)

    current_h = misplaced_tiles(current, goal)
    current_path = [current]

    best_state = current
    best_h = current_h
    best_path = current_path[:]

    t = t0
    expanded = 0

    while t > t_min and expanded < max_steps:
        expanded += 1

        if current == goal:
            return [list(state) for state in current_path], expanded

        neighbors = list(get_neighbors(current))
        next_state = random.choice(neighbors)

        next_h = misplaced_tiles(next_state, goal)
        delta = next_h - current_h

        # delta < 0: tot hon nen nhan ngay
        # delta >= 0: xau hon, nhan voi xac suat exp(-delta / T)
        if delta < 0 or random.random() < math.exp(-delta / t):
            current = next_state
            current_h = next_h
            current_path.append(current)

            if current_h < best_h:
                best_state = current
                best_h = current_h
                best_path = current_path[:]

        t = alpha * t

    if best_state == goal:
        return [list(state) for state in best_path], expanded

    return None, expanded

def and_or_graph_search(start, goal, max_depth=35):
    start = tuple(start)
    goal = tuple(goal)
    expanded = 0

    def or_search(state, path, depth):
        nonlocal expanded
        expanded += 1

        if state == goal:
            return [state]

        if state in path or depth >= max_depth:
            return None

        for neighbor in get_neighbors(state):
            plan = and_search([neighbor], path + [state], depth + 1)
            if plan is not None:
                return [state] + plan

        return None

    def and_search(states, path, depth):
        full_plan = []

        for s in states:
            plan = or_search(s, path, depth)
            if plan is None:
                return None

            if not full_plan:
                full_plan = plan
            else:
                full_plan += plan[1:]

        return full_plan

    result = or_search(start, [], 0)

    if result is None:
        return None, expanded

    return [list(state) for state in result], expanded


def backtracking_search(start, goal, max_depth=50):
    start = tuple(start)
    goal = tuple(goal)
    expanded = 0

    def backtrack(state, path, depth):
        nonlocal expanded
        expanded += 1

        if state == goal:
            return path + [state]

        if depth >= max_depth:
            return None

        for neighbor in get_neighbors(state):
            if neighbor not in path:
                result = backtrack(neighbor, path + [state], depth + 1)

                if result is not None:
                    return result

        return None

    result = backtrack(start, [], 0)

    if result is None:
        return None, expanded

    return [list(state) for state in result], expanded


def forward_checking_search(start, goal, max_depth=50):
    start = tuple(start)
    goal = tuple(goal)
    expanded = 0

    def forward_check(state, path):
        neighbors = list(get_neighbors(state))

        valid_neighbors = []
        for neighbor in neighbors:
            if neighbor not in path:
                valid_neighbors.append(neighbor)

        return valid_neighbors

    def backtrack_fc(state, path, depth):
        nonlocal expanded
        expanded += 1

        if state == goal:
            return path + [state]

        if depth >= max_depth:
            return None

        candidates = forward_check(state, path)

        # Uu tien trang thai co heuristic tot hon
        candidates.sort(key=lambda s: misplaced_tiles(s, goal))

        for neighbor in candidates:
            future_candidates = forward_check(neighbor, path + [state])

            # Forward Checking: neu chua toi goal ma khong con nuoc di thi loai som
            if neighbor != goal and not future_candidates:
                continue

            result = backtrack_fc(neighbor, path + [state], depth + 1)

            if result is not None:
                return result

        return None

    result = backtrack_fc(start, [], 0)

    if result is None:
        return None, expanded

    return [list(state) for state in result], expanded

ALGORITHMS = {
    "BFS": bfs,
    "DFS": dfs,
    "IDS": ids,
    "UCS": ucs,
    "Greedy": greedy_search,
    "A*": astar,
    "IDA*": ida_star,
    "Simple HC": simple_hill_climbing,
    "Steepest HC": steepest_hill_climbing,
    "Stochastic HC": stochastic_hill_climbing,
    "Random Restart HC": random_restart_hill_climbing,
    "Local Beam": local_beam_search,
    "Simulated Annealing": simulated_annealing,
    "Blind Start": blind_start_search,
    "Blind Goal": blind_goal_search,
    "Blind Start+Goal": bidirectional_bfs,
    "AND-OR": and_or_graph_search,
    "Backtracking": backtracking_search,
    "Forward Checking": forward_checking_search,
}

# CSP Map Coloring
# Random map: 5 vung, 3 mau
CSP_COLORS = ["Red", "Green", "Blue"]
CSP_COLOR_HEX = {
    "Red": "#ef4444",
    "Green": "#22c55e",
    "Blue": "#3b82f6",
}


def build_csp_neighbors(variables, edges):
    neighbors = {v: [] for v in variables}

    for x, y in edges:
        neighbors[x].append(y)
        neighbors[y].append(x)

    return neighbors


def generate_random_csp_map():
    """
    Dieu kien random:
    - Luon co 5 vung: A, B, C, D, E
    - Luon co 3 mau: Red, Green, Blue
    - Graph luon lien thong
    - So canh random tu 5 den 7
    - Dam bao co nghiem voi 3 mau
    """
    variables = ["A", "B", "C", "D", "E"]
    max_try = 200

    for _ in range(max_try):
        edges = set()

        # Tao cay lien thong truoc
        for i in range(1, len(variables)):
            a = variables[i]
            b = random.choice(variables[:i])
            edges.add(tuple(sorted((a, b))))

        # Them canh random de map khac nhau moi lan
        all_possible = []
        for i in range(len(variables)):
            for j in range(i + 1, len(variables)):
                edge = tuple(sorted((variables[i], variables[j])))
                if edge not in edges:
                    all_possible.append(edge)

        random.shuffle(all_possible)
        target_edges = random.randint(5, 7)

        while len(edges) < target_edges and all_possible:
            edges.add(all_possible.pop())

        edges = sorted(list(edges))
        assignment, steps = csp_backtracking_alg(variables, CSP_COLORS, edges)

        # Chi nhan map co nghiem
        if len(assignment) == len(variables):
            return variables, CSP_COLORS[:], edges

    # Fallback neu random xui
    return variables, CSP_COLORS[:], [
        ("A", "B"), ("A", "C"), ("B", "C"),
        ("B", "D"), ("C", "E"), ("D", "E")
    ]


def csp_is_valid_alg(var, color, assignment, neighbors):
    for neighbor in neighbors[var]:
        if assignment.get(neighbor) == color:
            return False
    return True


def csp_conflicts_alg(var, color, assignment, neighbors):
    count = 0

    for neighbor in neighbors[var]:
        if assignment.get(neighbor) == color:
            count += 1

    return count


def csp_backtracking_alg(variables, colors, edges):
    neighbors = build_csp_neighbors(variables, edges)
    assignment = {}
    steps = []
    expanded = 0

    def backtrack(index):
        nonlocal expanded
        expanded += 1

        if index == len(variables):
            steps.append("DONE: " + str(assignment))
            return True

        var = variables[index]

        for color in colors:
            steps.append(f"Try {var} = {color}")

            if csp_is_valid_alg(var, color, assignment, neighbors):
                assignment[var] = color
                steps.append(f"Assign {var} = {color}")

                if backtrack(index + 1):
                    return True

                steps.append(f"Backtrack {var}")
                del assignment[var]
            else:
                steps.append(f"Reject {var} = {color}")

        return False

    backtrack(0)
    steps.insert(0, f"Expanded nodes: {expanded}")
    return assignment, steps


def csp_forward_checking_alg(variables, colors, edges):
    neighbors = build_csp_neighbors(variables, edges)
    domains = {v: colors[:] for v in variables}
    assignment = {}
    steps = []
    expanded = 0

    def backtrack(index, domains):
        nonlocal expanded
        expanded += 1

        if index == len(variables):
            steps.append("DONE: " + str(assignment))
            return True

        var = variables[index]

        for color in domains[var]:
            steps.append(f"Try {var} = {color}")

            if not csp_is_valid_alg(var, color, assignment, neighbors):
                steps.append(f"Reject {var} = {color}")
                continue

            assignment[var] = color
            new_domains = {v: domains[v][:] for v in domains}
            ok = True

            for neighbor in neighbors[var]:
                if neighbor not in assignment and color in new_domains[neighbor]:
                    new_domains[neighbor].remove(color)
                    steps.append(f"Remove {color} from Domain({neighbor})")

                    if not new_domains[neighbor]:
                        steps.append(f"Fail: Domain({neighbor}) empty")
                        ok = False
                        break

            if ok and backtrack(index + 1, new_domains):
                return True

            steps.append(f"Backtrack {var}")
            del assignment[var]

        return False

    backtrack(0, domains)
    steps.insert(0, f"Expanded nodes: {expanded}")
    return assignment, steps


def csp_ac3_alg(variables, colors, edges):
    neighbors = build_csp_neighbors(variables, edges)
    domains = {v: colors[:] for v in variables}

    # Gan ngau nhien 1 vung truoc de AC-3 co tac dung ro hon
    fixed_var = random.choice(variables)
    fixed_color = random.choice(colors)
    domains[fixed_var] = [fixed_color]

    queue = deque(edges + [(y, x) for x, y in edges])
    steps = [f"Initial: {fixed_var} = {fixed_color}"]

    def revise(xi, xj):
        revised = False

        for x in domains[xi][:]:
            # Constraint: xi != xj
            if not any(x != y for y in domains[xj]):
                domains[xi].remove(x)
                steps.append(f"Remove {x} from Domain({xi}) because of {xj}")
                revised = True

        return revised

    while queue:
        xi, xj = queue.popleft()
        steps.append(f"Check arc ({xi}, {xj})")

        if revise(xi, xj):
            if not domains[xi]:
                steps.append(f"Fail: Domain({xi}) empty")
                return {}, steps, domains

            for xk in neighbors[xi]:
                if xk != xj:
                    queue.append((xk, xi))

    assignment = {}

    for var in variables:
        if len(domains[var]) == 1:
            assignment[var] = domains[var][0]

    steps.append("Domains after AC-3: " + str(domains))
    return assignment, steps, domains


def csp_min_conflicts_alg(variables, colors, edges, max_steps=100):
    neighbors = build_csp_neighbors(variables, edges)
    assignment = {v: random.choice(colors) for v in variables}
    steps = ["Initial: " + str(assignment)]

    def conflicted_vars():
        result = []

        for var in variables:
            if csp_conflicts_alg(var, assignment[var], assignment, neighbors) > 0:
                result.append(var)

        return result

    for step in range(max_steps):
        conflict_vars = conflicted_vars()

        if not conflict_vars:
            steps.append("DONE: " + str(assignment))
            return assignment, steps

        var = random.choice(conflict_vars)

        best_color = min(
            colors,
            key=lambda color: csp_conflicts_alg(var, color, assignment, neighbors)
        )

        assignment[var] = best_color
        steps.append(f"Step {step + 1}: set {var} = {best_color}")

    steps.append("Stopped: max steps reached")
    return assignment, steps


class CSPDemoWindow:
    def __init__(self, root, colors):
        self.root = tk.Toplevel(root)
        self.root.title("CSP Map Coloring - Random 5 Regions")
        self.root.geometry("820x600")
        self.root.resizable(False, False)
        self.COLORS = colors

        self.variables = []
        self.colors = CSP_COLORS[:]
        self.edges = []
        self.assignment = {}

        self.node_pos = {
            "A": (250, 80),
            "B": (110, 230),
            "C": (390, 230),
            "D": (170, 410),
            "E": (330, 410),
        }

        self.setup_ui()
        self.generate_map()

    def setup_ui(self):
        self.root.configure(bg=self.COLORS["bg"])

        left = tk.Frame(self.root, bg=self.COLORS["panel"], width=540, height=575)
        left.pack(side="left", fill="both", padx=12, pady=12)
        left.pack_propagate(False)

        right = tk.Frame(self.root, bg=self.COLORS["panel"], width=250, height=575)
        right.pack(side="right", fill="both", padx=(0, 12), pady=12)
        right.pack_propagate(False)

        title = tk.Label(
            left,
            text="CSP Random Map Coloring",
            font=("Segoe UI", 18, "bold"),
            bg=self.COLORS["panel"],
            fg=self.COLORS["text"],
        )
        title.pack(anchor="w", padx=16, pady=(14, 2))

        note = tk.Label(
            left,
            text="5 regions • 3 colors • connected random graph",
            font=("Segoe UI", 10),
            bg=self.COLORS["panel"],
            fg=self.COLORS["muted"],
        )
        note.pack(anchor="w", padx=16, pady=(0, 8))

        self.canvas = tk.Canvas(
            left,
            width=500,
            height=460,
            bg=self.COLORS["panel_2"],
            highlightthickness=1,
            highlightbackground=self.COLORS["border"],
        )
        self.canvas.pack(padx=16, pady=(0, 16))

        button_frame = tk.Frame(right, bg=self.COLORS["panel"])
        button_frame.pack(fill="x", padx=14, pady=(16, 10))

        self.make_button(button_frame, "Generate Map", self.generate_map).pack(fill="x", pady=(0, 12), ipady=7)
        self.make_button(button_frame, "Backtracking", self.run_backtracking).pack(fill="x", pady=5, ipady=6)
        self.make_button(button_frame, "Forward Checking", self.run_forward_checking).pack(fill="x", pady=5, ipady=6)
        self.make_button(button_frame, "AC-3", self.run_ac3).pack(fill="x", pady=5, ipady=6)
        self.make_button(button_frame, "Min-Conflict", self.run_min_conflicts).pack(fill="x", pady=5, ipady=6)
        self.make_button(button_frame, "Reset Color", self.reset).pack(fill="x", pady=(14, 5), ipady=6)

        self.output = tk.Text(
            right,
            height=20,
            bg=self.COLORS["panel_2"],
            fg=self.COLORS["text"],
            insertbackground=self.COLORS["text"],
            font=("Consolas", 10),
            relief="flat",
            wrap="word",
        )
        self.output.pack(fill="both", expand=True, padx=14, pady=(6, 14))

    def make_button(self, parent, text, command):
        return tk.Button(
            parent,
            text=text,
            font=("Segoe UI", 10, "bold"),
            bg=self.COLORS["card"],
            fg="white",
            activebackground=self.COLORS["accent"],
            activeforeground="#020617",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=command,
        )

    def color_to_hex(self, color):
        if color in CSP_COLOR_HEX:
            return CSP_COLOR_HEX[color]

        return self.COLORS["cell"]

    def draw_graph(self):
        self.canvas.delete("all")

        # Ve canh
        for x, y in self.edges:
            x1, y1 = self.node_pos[x]
            x2, y2 = self.node_pos[y]
            self.canvas.create_line(x1, y1, x2, y2, fill=self.COLORS["border"], width=4)

        # Ve node
        for node in self.variables:
            x, y = self.node_pos[node]
            fill = self.color_to_hex(self.assignment.get(node))
            self.canvas.create_oval(
                x - 36, y - 36,
                x + 36, y + 36,
                fill=fill,
                outline=self.COLORS["accent"],
                width=2,
            )
            self.canvas.create_text(
                x,
                y,
                text=node,
                fill="white",
                font=("Segoe UI", 18, "bold"),
            )

        edge_text = ", ".join([f"{a}-{b}" for a, b in self.edges])
        self.canvas.create_text(
            250,
            25,
            text=f"Edges: {edge_text}",
            fill=self.COLORS["muted"],
            font=("Segoe UI", 9),
        )

    def generate_map(self):
        self.variables, self.colors, self.edges = generate_random_csp_map()
        self.assignment = {}
        self.draw_graph()

        self.output.delete("1.0", "end")
        self.output.insert("end", "Random Map Generated\n")
        self.output.insert("end", "====================\n\n")
        self.output.insert("end", "Condition:\n")
        self.output.insert("end", "- 5 regions: A, B, C, D, E\n")
        self.output.insert("end", "- 3 colors: Red, Green, Blue\n")
        self.output.insert("end", "- Connected graph\n")
        self.output.insert("end", "- Random 5 to 7 edges\n")
        self.output.insert("end", "- Solvable with 3 colors\n\n")
        self.output.insert("end", "Edges:\n")
        for a, b in self.edges:
            self.output.insert("end", f"{a} - {b}\n")

    def show_steps(self, title, assignment, steps):
        self.assignment = assignment.copy()
        self.draw_graph()

        self.output.delete("1.0", "end")
        self.output.insert("end", title + "\n")
        self.output.insert("end", "=" * len(title) + "\n\n")

        for step in steps:
            self.output.insert("end", step + "\n")

        self.output.insert("end", "\nResult:\n")
        for var in self.variables:
            self.output.insert("end", f"{var} = {assignment.get(var, '?')}\n")

    def run_backtracking(self):
        assignment, steps = csp_backtracking_alg(self.variables, self.colors, self.edges)
        self.show_steps("Backtracking", assignment, steps)

    def run_forward_checking(self):
        assignment, steps = csp_forward_checking_alg(self.variables, self.colors, self.edges)
        self.show_steps("Forward Checking", assignment, steps)

    def run_ac3(self):
        assignment, steps, domains = csp_ac3_alg(self.variables, self.colors, self.edges)

        self.assignment = assignment.copy()
        self.draw_graph()

        self.output.delete("1.0", "end")
        self.output.insert("end", "AC-3\n")
        self.output.insert("end", "====\n\n")

        for step in steps:
            self.output.insert("end", step + "\n")

        self.output.insert("end", "\nDomains:\n")
        for var in self.variables:
            self.output.insert("end", f"Domain({var}) = {domains[var]}\n")

    def run_min_conflicts(self):
        assignment, steps = csp_min_conflicts_alg(self.variables, self.colors, self.edges)
        self.show_steps("Min-Conflict", assignment, steps)

    def reset(self):
        self.assignment = {}
        self.draw_graph()
        self.output.delete("1.0", "end")
        self.output.insert("end", "Color reset.\n")

# GUI
class PuzzleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("8 Puzzle Search")
        self.root.geometry("1220x740")
        self.root.minsize(1120, 700)
        self.root.resizable(False, False)
        self.root.configure(bg="#0f172a")

        # Dark sharp theme
        self.COLORS = {
            "bg": "#0f172a",
            "panel": "#111827",
            "panel_2": "#0b1220",
            "card": "#1f2937",
            "cell": "#0f172a",
            "cell_empty": "#111827",
            "border": "#334155",
            "text": "#e5e7eb",
            "muted": "#94a3b8",
            "accent": "#38bdf8",
            "accent_2": "#2563eb",
            "warning": "#f59e0b",
            "success": "#22c55e",
            "danger": "#ef4444",
        }

        self.start, self.goal = generate_puzzle()
        self.selected_algorithm = tk.StringVar(value="BFS")
        self.animation_job = None
        self.paused = False
        self.current_path = []
        self.current_index = 0

        self.start_cells = []
        self.goal_cells = []
        self.status_badge = None

        self.setup_ui()
        self.draw_main_grids()

    # ---------- UI ----------
    def setup_ui(self):
        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=0)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_columnconfigure(3, weight=0)
        self.root.grid_rowconfigure(0, weight=1)

        self.left_panel(self.root)
        self.control_panel(self.root)
        self.states_panel(self.root)
        self.stats_panel(self.root)

    def panel(self, parent):
        return tk.Frame(
            parent,
            bg=self.COLORS["panel"],
            highlightthickness=1,
            highlightbackground=self.COLORS["border"],
            highlightcolor=self.COLORS["accent"],
        )

    def title(self, parent, text, size=20):
        return tk.Label(
            parent,
            text=text,
            font=("Segoe UI", size, "bold"),
            bg=parent["bg"],
            fg=self.COLORS["text"],
        )

    def subtitle(self, parent, text):
        return tk.Label(
            parent,
            text=text,
            font=("Segoe UI", 10),
            bg=parent["bg"],
            fg=self.COLORS["muted"],
        )

    def left_panel(self, parent):
        left = self.panel(parent)
        left.grid(row=0, column=0, sticky="ns", padx=(14, 8), pady=12)
        left.config(width=285, height=716)
        left.grid_propagate(False)

        header = tk.Frame(left, bg=self.COLORS["panel"])
        header.pack(fill="x", padx=24, pady=(18, 6))
        self.title(header, "8 Puzzle", 21).pack(anchor="w")
        self.subtitle(header, "Start and target configuration").pack(anchor="w", pady=(2, 0))

        self.title(left, "Start", 15).pack(anchor="w", padx=24, pady=(10, 6))
        start_frame = tk.Frame(left, bg=self.COLORS["panel"])
        start_frame.pack(padx=24, pady=(0, 8))
        self.start_cells = self.create_grid(start_frame, big=True)

        self.title(left, "Goal", 15).pack(anchor="w", padx=24, pady=(10, 6))
        goal_frame = tk.Frame(left, bg=self.COLORS["panel"])
        goal_frame.pack(padx=24, pady=(0, 12))
        self.goal_cells = self.create_grid(goal_frame, big=True)

    def control_panel(self, parent):
        control = self.panel(parent)
        control.grid(row=0, column=1, sticky="ns", padx=8, pady=12)
        control.config(width=285, height=716)
        control.grid_propagate(False)

        self.title(control, "Algorithm", 19).pack(anchor="w", padx=18, pady=(16, 2))
        self.subtitle(control, "Choose search strategy").pack(anchor="w", padx=18, pady=(0, 10))

        algo_area = tk.Frame(control, bg=self.COLORS["panel"])
        algo_area.pack(fill="x", padx=16, pady=(0, 12))

        self.algo_canvas = tk.Canvas(
            algo_area,
            width=220,
            height=315,
            bg=self.COLORS["panel"],
            highlightthickness=0,
        )
        self.algo_canvas.pack(side="left", fill="both", expand=True)

        algo_scrollbar = tk.Scrollbar(
            algo_area,
            orient="vertical",
            command=self.algo_canvas.yview,
            bg=self.COLORS["panel"],
            troughcolor=self.COLORS["panel_2"],
            activebackground=self.COLORS["accent"],
            relief="flat",
        )
        algo_scrollbar.pack(side="right", fill="y")
        self.algo_canvas.configure(yscrollcommand=algo_scrollbar.set)

        self.algo_container = tk.Frame(self.algo_canvas, bg=self.COLORS["panel"])
        self.algo_canvas_window = self.algo_canvas.create_window(
            (0, 0), window=self.algo_container, anchor="nw"
        )

        self.algo_container.bind(
            "<Configure>",
            lambda e: self.algo_canvas.configure(scrollregion=self.algo_canvas.bbox("all")),
        )
        self.algo_canvas.bind(
            "<Configure>",
            lambda e: self.algo_canvas.itemconfigure(self.algo_canvas_window, width=e.width),
        )
        self.algo_canvas.bind(
            "<Enter>",
            lambda e: self.root.bind_all("<MouseWheel>", self.scroll_algorithm_mouse),
        )
        self.algo_canvas.bind("<Leave>", lambda e: self.root.unbind_all("<MouseWheel>"))

        for name in ALGORITHMS:
            rb = tk.Radiobutton(
                self.algo_container,
                text=name,
                value=name,
                variable=self.selected_algorithm,
                font=("Segoe UI", 10, "bold"),
                bg=self.COLORS["card"],
                fg=self.COLORS["text"],
                activebackground=self.COLORS["accent_2"],
                activeforeground="white",
                selectcolor=self.COLORS["accent_2"],
                indicatoron=False,
                bd=0,
                relief="flat",
                cursor="hand2",
                anchor="w",
                padx=14,
                pady=7,
            )
            rb.pack(fill="x", padx=6, pady=3)

        buttons = tk.Frame(control, bg=self.COLORS["panel"])
        buttons.pack(fill="x", padx=18, pady=(6, 0))

        self.make_button(buttons, "Solve", self.solve, self.COLORS["accent_2"]).pack(fill="x", pady=(0, 6), ipady=6)
        self.make_button(buttons, "New Puzzle", self.new_puzzle, self.COLORS["card"]).pack(fill="x", pady=4, ipady=5)
        self.make_button(buttons, "CSP Coloring", self.open_csp_demo, self.COLORS["accent_2"]).pack(fill="x", pady=4, ipady=5)
        self.make_button(buttons, "Pause", self.pause_animation, self.COLORS["warning"]).pack(fill="x", pady=4, ipady=5)
        self.make_button(buttons, "Resume", self.resume_animation, self.COLORS["success"]).pack(fill="x", pady=4, ipady=5)


    def make_button(self, parent, text, command, color):
        return tk.Button(
            parent,
            text=text,
            font=("Segoe UI", 12, "bold"),
            bg=color,
            fg="white",
            activebackground=self.COLORS["accent"],
            activeforeground="#020617",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=command,
        )

    def stats_panel(self, parent):
        stats = self.panel(parent)
        stats.grid(row=0, column=3, sticky="ns", padx=(8, 14), pady=12)
        stats.config(width=180, height=716)
        stats.grid_propagate(False)

        self.title(stats, "Status", 18).pack(anchor="w", padx=16, pady=(16, 4))
        self.subtitle(stats, "Run information").pack(anchor="w", padx=16, pady=(0, 12))

        box = tk.Frame(
            stats,
            bg=self.COLORS["panel_2"],
            highlightthickness=1,
            highlightbackground=self.COLORS["border"],
        )
        box.pack(fill="x", padx=14, pady=(0, 12))

        self.status_badge = tk.Label(
            box,
            text="READY",
            font=("Segoe UI", 10, "bold"),
            bg=self.COLORS["accent"],
            fg="#082f49",
            padx=10,
            pady=4,
        )
        self.status_badge.pack(anchor="w", padx=10, pady=(12, 8))

        self.info_label = tk.Label(
            box,
            text="Steps: 0\nNodes: 0",
            font=("Consolas", 12, "bold"),
            bg=self.COLORS["panel_2"],
            fg=self.COLORS["text"],
            justify="left",
        )
        self.info_label.pack(anchor="w", padx=10, pady=(0, 12))

    def states_panel(self, parent):
        states = self.panel(parent)
        states.grid(row=0, column=2, sticky="nsew", padx=8, pady=12)
        states.config(width=470, height=716)
        states.grid_propagate(False)
        states.grid_columnconfigure(0, weight=1)
        states.grid_rowconfigure(1, weight=1)

        header = tk.Frame(states, bg=self.COLORS["panel"])
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 10))
        self.title(header, "States", 21).pack(side="left")
        self.path_label = tk.Label(
            header,
            text="No path yet",
            font=("Segoe UI", 10, "bold"),
            bg=self.COLORS["panel"],
            fg=self.COLORS["muted"],
        )
        self.path_label.pack(side="right")

        canvas_area = tk.Frame(states, bg=self.COLORS["panel_2"], highlightthickness=1, highlightbackground=self.COLORS["border"])
        canvas_area.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        canvas_area.grid_columnconfigure(0, weight=1)
        canvas_area.grid_rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            canvas_area,
            bg=self.COLORS["panel_2"],
            highlightthickness=0,
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        scrollbar = tk.Scrollbar(
            canvas_area,
            orient="vertical",
            command=self.canvas.yview,
            bg=self.COLORS["panel"],
            troughcolor=self.COLORS["panel_2"],
            activebackground=self.COLORS["accent"],
            relief="flat",
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.states_container = tk.Frame(self.canvas, bg=self.COLORS["panel_2"])
        self.states_container.grid_columnconfigure(0, weight=1)
        self.states_container.grid_columnconfigure(1, weight=1)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.states_container, anchor="nw")

        self.states_container.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfigure(self.canvas_window, width=e.width),
        )
        self.canvas.bind("<Enter>", lambda e: self.root.bind_all("<MouseWheel>", self.scroll_mouse))
        self.canvas.bind("<Leave>", lambda e: self.root.unbind_all("<MouseWheel>"))

    # ---------- Grid ----------
    def create_grid(self, parent, big=False):
        cells = []
        # Big grid is compact enough to keep Start/Goal visible.
        # Small grid is enlarged for easier reading inside State cards.
        font_size = 20 if big else 15
        width = 3 if big else 3
        height = 1 if big else 1
        pad = 2 if big else 2

        for i in range(9):
            cell = tk.Label(
                parent,
                width=width,
                height=height,
                font=("Segoe UI", font_size, "bold"),
                bg=self.COLORS["cell"],
                fg=self.COLORS["text"],
                bd=0,
                highlightthickness=1,
                highlightbackground=self.COLORS["border"],
                highlightcolor=self.COLORS["accent"],
            )
            cell.grid(row=i // 3, column=i % 3, padx=pad, pady=pad)
            cells.append(cell)

        return cells

    def draw_grid(self, cells, state):
        for cell, value in zip(cells, state):
            if value == 0:
                cell.config(text="", bg=self.COLORS["cell_empty"], fg=self.COLORS["muted"])
            else:
                cell.config(text=str(value), bg=self.COLORS["cell"], fg=self.COLORS["text"])

    def draw_main_grids(self):
        self.draw_grid(self.start_cells, self.start)
        self.draw_grid(self.goal_cells, self.goal)

    def draw_state_card(self, state):
        # Show states in 2 columns to reduce wasted space and make each state larger.
        idx = self.current_index
        row = idx // 2
        col = idx % 2

        card = tk.Frame(
            self.states_container,
            bg=self.COLORS["card"],
            highlightthickness=1,
            highlightbackground=self.COLORS["border"],
        )
        card.grid(row=row, column=col, padx=7, pady=7, sticky="n")

        label = tk.Label(
            card,
            text=f"State {idx + 1}",
            font=("Segoe UI", 9, "bold"),
            bg=self.COLORS["card"],
            fg=self.COLORS["accent"],
        )
        label.pack(anchor="w", padx=10, pady=(8, 4))

        grid_frame = tk.Frame(card, bg=self.COLORS["card"])
        grid_frame.pack(padx=10, pady=(0, 10))
        cells = self.create_grid(grid_frame, big=False)
        self.draw_grid(cells, state)

    # ---------- Actions ----------
    def clear_states(self):
        self.paused = False

        if self.animation_job:
            self.root.after_cancel(self.animation_job)
            self.animation_job = None

        for widget in self.states_container.winfo_children():
            widget.destroy()

        self.canvas.yview_moveto(0)
        self.current_index = 0
        self.path_label.config(text="No path yet")
        self.status_badge.config(text="READY", bg=self.COLORS["accent"], fg="#082f49")

    def solve(self):
        self.clear_states()

        algo_name = self.selected_algorithm.get()
        search = ALGORITHMS[algo_name]
        self.status_badge.config(text="RUNNING", bg=self.COLORS["warning"], fg="#111827")
        self.root.update_idletasks()

        result, nodes = search(self.start, self.goal)

        if result is None:
            self.info_label.config(text=f"Steps: Not found\nNodes: {nodes}")
            self.path_label.config(text=f"{algo_name}: not found")
            self.status_badge.config(text="FAILED", bg=self.COLORS["danger"], fg="white")
            return

        self.current_path = result
        self.current_index = 0
        self.paused = False

        self.info_label.config(text=f"Steps: {len(result) - 1}\nNodes: {nodes}")
        self.path_label.config(text=f"{algo_name} • {len(result) - 1} steps")
        self.status_badge.config(text="SHOWING", bg=self.COLORS["success"], fg="#052e16")

        self.show_states()

    def show_states(self):
        if self.paused:
            return

        if self.current_index >= len(self.current_path):
            self.status_badge.config(text="DONE", bg=self.COLORS["accent"], fg="#082f49")
            return

        self.draw_state_card(self.current_path[self.current_index])
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

        self.current_index += 1
        self.animation_job = self.root.after(220, self.show_states)

    def new_puzzle(self):
        self.clear_states()
        self.start, self.goal = generate_puzzle()
        self.draw_main_grids()
        self.info_label.config(text="Steps: 0\nNodes: 0")

    def open_csp_demo(self):
        CSPDemoWindow(self.root, self.COLORS)

    def scroll_algorithm_mouse(self, event):
        self.algo_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def scroll_mouse(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def pause_animation(self):
        self.paused = True
        self.status_badge.config(text="PAUSED", bg=self.COLORS["warning"], fg="#111827")

        if self.animation_job:
            self.root.after_cancel(self.animation_job)
            self.animation_job = None

    def resume_animation(self):
        if not self.paused:
            return

        self.paused = False
        self.status_badge.config(text="SHOWING", bg=self.COLORS["success"], fg="#052e16")
        self.show_states()


if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleApp(root)
    root.mainloop()
