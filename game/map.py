
class Map:

    def __init__(self, data,
                    wall_img  = None,
                    node_size = 100,
                    physics   = None):

        self.data       = data
        self.node_size  = node_size
        self.wall_img   = Resources.instance.sprite("wall")
        image_set_size(self.wall_img, node_size, node_size)

        self.floor_img   = Resources.instance.sprite("floor")
        image_set_size(self.floor_img, node_size, node_size)

        self.sprites    = []
        self.batch      = pg.graphics.Batch()
        self.make_map(physics)

        self.pathfinder = PathFinder(self.data, node_size)

        create_signal("on_player_move")
        connect("on_player_move", self, "clamp_player")

    def make_map(self, physics):
        bg = pg.graphics.OrderedGroup(0)
        fg = pg.graphics.OrderedGroup(1)
        nsx, nsy = (self.node_size,)*2

        for y, row in enumerate(self.data):
            for x, data in enumerate(row):
                offx, offy = x * nsx, y * nsy

                # -- create floor tiles
                if data == " ":
                    sp = pg.sprite.Sprite(self.floor_img, x=offx, y=offy, batch=self.batch, group=bg)
                    self.sprites.append(sp)

                # -- create walls
                if data == "#":
                    sp = pg.sprite.Sprite(self.wall_img, x=offx, y=offy, batch=self.batch, group=fg)
                    self.sprites.append(sp)
                    add_wall(physics.space, (offx + nsx/2, offy + nsy/2), (nsx, nsy))

    def clamp_player(self, player_pos):
        # -- calculate player offset
        px, py = player_pos
        w, h = window.get_size()
        player_off =  -px + w/2, -py + h/2

        # -- keep player within map bounds
        offx, offy = self.clamped_offset(*player_off)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(offx, offy, 0)

    def clamped_offset(self, offx, offy):
        # -- clamp offset so that viewport doesnt go beyond map bounds
        # -- if map is smaller than window, no need for offset
        winw, winh = window.get_size()
        msx, msy = self.size()

        clamp_X = msx - winw
        clamp_Y = msy - winh

        offx = 0 if offx > 0 else offx
        if clamp_X > 0:
            offx = -clamp_X if offx < -clamp_X else offx

        offy = 0 if offy > 0 else offy
        if clamp_Y > 0:
            offy = -clamp_Y if offy < -clamp_Y else offy

        return offx, offy

    def make_minimap(self, size, wall_color=(255, 255, 0, 200),
        background_color=(0, 0, 0, 0)):
        sx, sy = [s/ms for s, ms in zip(size, self.size())]
        nsx, nsy = (self.node_size,)*2

        background_image = pg.image.SolidColorImagePattern(background_color)
        background_image = background_image.create_image(*self.size())
        background = background_image.get_texture()

        wall_image = pg.image.SolidColorImagePattern(wall_color)
        wall_image = wall_image.create_image(nsx, nsy)
        wall = wall_image.get_texture()

        for y, row in enumerate(self.data):
            for x, data in enumerate(row):
                offx, offy = x * nsx, y * nsy

                if data == "#":
                    background.blit_into(wall_image, offx, offy, 0)

        sp = pg.sprite.Sprite(background)
        sc = min(sx, sy)
        sp.scale_x = sc
        sp.scale_y = sc
        return sp

    def draw(self):
        self.batch.draw()

    def size(self):
        ns = self.node_size
        return (ns * len(self.data[0])), (ns * len(self.data))

class PathFinder:

    def __init__(self, map_data, node_size):
        self.data = map_data
        self.node_size = (node_size,)*2

    def walkable(self):
        # -- find all walkable nodes
        add = lambda p1, p2 : (p1[0]+p2[0], p1[1]+p2[1])
        mul = lambda p1, p2 : (p1[0]*p2[0], p1[1]*p2[1])

        hns = (self.node_size[0]/2, self.node_size[1]/2)
        walkable = [add(hns, mul((x, y), self.node_size)) for y, data in enumerate(self.data)
            for x, d in enumerate(data) if d != '#']
        return walkable

    def calculate_path(self, p1, p2):
        cf, cost = a_star_search(self, p1, p2)
        return reconstruct_path(cf, p1, p2)

    def calc_patrol_path(self, points):
        result = []
        circular_points = points + [points[0]]
        for i in range(len(circular_points)-2):
            f, s = circular_points[i:i+2]
            path = self.calculate_path(f, s)[1:]
            result.extend(path)
        return result

    def neighbours(self, p):
        add = lambda p1, p2 : (p1[0]+p2[0], p1[1]+p2[1])
        mul = lambda p1, p2 : (p1[0]*p2[0], p1[1]*p2[1])

        # -- find neighbours that are walkable
        directions      = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        neigh_positions = [add(p, mul(d, self.node_size)) for d in directions]
        return [n for n in neigh_positions if n in self.walkable()]

    def closest_point(self, p):
        data = [(distance_sqr(p, point), point) for point in self.walkable()]
        return min(data, key=lambda d:d[0])[1]

    def cost(self, *ignored):
        return 1

class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]

