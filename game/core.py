

FPS        = 60
DEBUG      = 1
SIZE       = (800, 600)
CAPTION    = "Triggered"
BACKGROUND = (100, 100, 100)


class EventType(Enum):
    KEY_UP       = 1
    KEY_DOWN     = 2

    MOUSE_UP     = 3
    MOUSE_DOWN   = 4
    MOUSE_DRAG   = 5
    MOUSE_MOTION = 6
    MOUSE_SCROLL = 7

    RESIZE       = 8

    TEXT               = 9
    TEXT_MOTION        = 10
    TEXT_MOTION_SELECT = 11

Resource  = namedtuple("Resource", "name data")
LevelData = namedtuple("LevelData",
            ["map",
             "player",
             "enemies",
             "waypoints",
             "lights",
             "objectives"])


def clamp(x, _min, _max):
    return max(_min, min(_max, x))

def angle(p):
    nx, ny = normalize(p)
    return math.degrees(math.atan2(ny, nx))

def normalize(p):
    mag = math.hypot(*p)
    if mag:
        x = p[0] / mag
        y = p[1] / mag
        return (x, y)
    return p

def set_flag(name, value, items):
    for item  in items:
        setattr(item, name, value)

@contextmanager
def profile(perform=True):
    if perform:
        import cProfile, pstats, io
        s = io.StringIO()
        pr = cProfile.Profile()

        pr.enable()
        yield
        pr.disable()

        ps = pstats.Stats(pr, stream=s)
        ps.sort_stats('cumtime')
        # ps.strip_dirs()
        ps.print_stats()

        all_stats = s.getvalue().split('\n')
        self_stats = "".join([line+'\n' for idx, line in enumerate(all_stats)
            if ('triggered' in  line) or (idx <= 4)])
        print(self_stats)
    else:
        yield

@contextmanager
def reset_matrix():
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, window.width, 0, window.height, -1, 1)

    yield

    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

def distance_sqr(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return dx**2 + dy**2

def add_wall(space, pos, size):
    shape = pm.Poly.create_box(space.static_body, size=size)
    shape.collision_type = COLLISION_MAP.get("WallType")
    shape.body.position = pos
    space.add(shape)

def heuristic(a, b):
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)

def random_color():
    r = random.random()
    g = random.random()
    b = random.random()
    return (r, g, b, 1)

def a_star_search(graph, start, goal):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while not frontier.empty():
        current = frontier.get()

        if current == goal:
            break

        for next in graph.neighbours(current):
            new_cost = cost_so_far[current] + graph.cost(current, next)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(goal, next)
                frontier.put(next, priority)
                came_from[next] = current

    return came_from, cost_so_far

def reconstruct_path(came_from, start, goal):
    current = goal
    path = [current]
    while current != start:
        current = came_from[current]
        path.append(current)
    path.append(start)
    path.reverse()
    return path

def setup_collisions(space):

    # Player-Enemy Collision
    def player_enemy_solve(arbiter, space, data):
        """ Keep the two bodies from intersecting"""
        pshape = arbiter.shapes[0]
        eshape = arbiter.shapes[1]

        normal = pshape.body.position - eshape.body.position
        normal = normal.normalized()
        pshape.body.position = eshape.body.position + (normal * (pshape.radius*2))
        return True

    for etype in Enemy.COL_TYPES:
        handler = space.add_collision_handler(
                COLLISION_MAP.get("PlayerType"), etype)
        handler.begin = player_enemy_solve

    # Enemy-Enemy Collision
    def enemy_enemy_solve(arbiter, space, data):
        """ Keep the two bodies from intersecting"""
        eshape  = arbiter.shapes[0]
        eshape1 = arbiter.shapes[1]

        normal = eshape.body.position - eshape1.body.position
        normal = normal.normalized()

        # -- to prevent, dead stop, move eshape a litte perpendicular to collision normal
        perp = pm.Vec2d(normal.y, -normal.x)
        perp_move = perp * (eshape.radius*2)
        eshape.body.position = eshape1.body.position + (normal * (eshape.radius*2)) + perp_move
        return True

    for etype1, etype2 in it.combinations(Enemy.COL_TYPES, 2):
        handler = space.add_collision_handler(
                etype1, etype2)
        handler.begin = enemy_enemy_solve

def draw_point(pos, color=(1, 0, 0, 1), size=5):
    glColor4f(*color)
    glPointSize(size)

    glBegin(GL_POINTS)
    glVertex2f(*pos)
    glEnd()
    # -- reset color
    glColor4f(1,1,1,1)

def draw_line(start, end, color=(1, 1, 0, 1), width=2):
    glColor4f(*color)
    glLineWidth(width)

    glBegin(GL_LINES)
    glVertex2f(*start)
    glVertex2f(*end)
    glEnd()
    # -- reset color
    glColor4f(1,1,1,1)

def draw_path(points, color=(1, 0, 1, 1), width=5):
    glColor4f(*color)
    glLineWidth(width)

    glBegin(GL_LINE_STRIP)
    for point in points:
        glVertex2f(*point)
    glEnd()
    # -- reset color
    glColor4f(1,1,1,1)

def image_set_size(img, w, h):
    img.width = w
    img.height = h

def image_set_anchor_center(img):
    img.anchor_x = img.width/2
    img.anchor_y = img.height/2

def mouse_over_rect(mouse, center, size):
    mx, my = mouse
    tx, ty = center
    dx, dy = abs(tx - mx), abs(ty - my)

    tsx, tsy = size
    if dx < tsx/2 and dy < tsy/2:
        return True
    return False

def get_current_level():
    return LevelManager.instance.current
