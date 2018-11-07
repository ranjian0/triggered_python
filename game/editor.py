
class LevelEditor:

    def __init__(self):
        self._level = None
        self.data = dict()

    def load(self, level):
        self.toolbar = EditorToolbar(self.data)
        self.viewport = EditorViewport(self.data)
        self.properties = EditorToolprops()

        self._level = level
        if level.data:
            # -- load leveldata
            for key, val in level.data._asdict().items():
                self.data[key] = val
        else:
            # -- initialize data with default values
            keys = LevelData._fields
            defaults = ([[]], (-10000, -10000), [], [], [], [])
            for k,v in zip(keys, defaults):
                self.data[k] = v

    def save(self):
        # -- remove temp data from self.data
        tmp_items = [key for key,v in self.data.items() if key.startswith('_')]
        tmp_data = [v for key,v in self.data.items() if key.startswith('_')]
        for it in tmp_items:
            del self.data[it]

        # -- update level data and reload level
        self._level.data = LevelData(**self.data)
        self._level.save()
        self._level.reload()

        # -- restore temp data from self.data
        for key,val in zip(tmp_items, tmp_data):
            self.data[key] = val

        # --  update viewport
        self.viewport.reload()

    def draw(self):
        with reset_matrix():
            self.viewport.draw()
            self.toolbar.draw()

    def update(self, dt):
        self.toolbar.update(dt)
        self.viewport.update(dt)

        # -- update tools for viewport transform
        for tool in self.toolbar.tools:
            tool.set_viewport_transform(self.viewport.get_transform())

    def event(self, *args, **kwargs):
        self.toolbar.event(*args, **kwargs)
        self.viewport.event(*args, **kwargs)



class EditorToolbar:
    WIDTH = 60

    def __init__(self, data):
        # -- toolbar
        self.toolbar_settings = {
            "size" : (self.WIDTH, window.height),
            "color" : (207, 188, 188, 255)
        }
        self.toolbar = pg.image.SolidColorImagePattern(
            self.toolbar_settings.get("color"))
        self.toolbar_image = self.toolbar.create_image(
            *self.toolbar_settings.get("size"))

        # -- tools
        self.tools = [
            AddTileTool(),
            AddAgentTool(),
            AddWaypointTool(),
            ObjectivesTool()
        ]

        self.tool_start_loc = (0, window.height)
        self.tool_settings = {
            "size" : (50, 50),
            "border" : (5, 5),
            "anchor" : (25, 25)
        }
        self.init_tools()
        # -- set data that tools operate on
        for tool in self.tools:
            tool.set_data(data)

    def init_tools(self):
        locx, locy = self.tool_start_loc
        # -- rely on orderd dict
        sz, brd, anch = [val for key, val in self.tool_settings.items()]

        for idx, tool in enumerate(self.tools):
            locx = brd[0] + anch[0]
            locy -= brd[1] + (sz[1] if idx > 0 else 0) + (anch[1] if idx == 0 else 0)
            tool.position = (locx, locy)
            tool.size = self.tool_settings.get("size")

    def get_rect(self):
        center = (self.WIDTH/2, window.height/2)
        size = (self.WIDTH, window.height)
        return [center, size]

    def draw(self):
        self.toolbar_image.blit(0, 0)
        for tool in self.tools:
            tool.draw()

    def update(self, dt):
        for tool in self.tools:
            tool.update(dt)

            if tool.activated:
                # -- set all tools as inactive
                set_flag('is_active', False, self.tools)
                set_flag('activated', False, self.tools)

                # -- activate current tool
                tool.is_active = True

    def event(self, *args, **kwargs):
        for tool in self.tools:
            tool.event(*args, **kwargs)

        # -- handle resize
        _type = args[0]
        if _type == EventType.RESIZE:
            _,_,h = args
            self.tool_start_loc = (0, h)
            self.init_tools()

            self.toolbar_settings['size'] = (self.WIDTH, h)
            self.toolbar_image = self.toolbar.create_image(
                *self.toolbar_settings.get("size"))

        elif _type == EventType.MOUSE_DOWN:
            x, y, btn, mod = args[1:]

            # -- deactivate all tools if click over empty toolbar area
            if btn == mouse.LEFT and mouse_over_rect((x, y), *self.get_rect()):
                # -- check if mouse was clicked over toolbar but not over a tool,
                if not any([mouse_over_rect((x, y), tool.position, tool.size) for tool in self.tools]):
                    # -- set all tools as inactive
                    set_flag('is_active', False, self.tools)
                    set_flag('activated', False, self.tools)

class EditorViewport:
    LINE_WIDTH = 2
    OFFSET = (EditorToolbar.WIDTH+LINE_WIDTH, LINE_WIDTH)

    GRID_SIZE = 20000
    GRID_SPACING = 100

    def __init__(self, data):
        self.data = data

        # -- panning options
        self._is_panning = False
        self._pan_offset = (0, 0)

        # -- zoom ptions
        self._zoom = (1, 1)
        self._zoom_sensitivity = 0.1

        # -- map options
        self.wall_img   = Resources.instance.sprite("wall")
        image_set_size(self.wall_img, self.GRID_SPACING, self.GRID_SPACING)

        self.floor_img   = Resources.instance.sprite("floor")
        image_set_size(self.floor_img, self.GRID_SPACING, self.GRID_SPACING)

        # -- player options
        self.player_img = Resources.instance.sprite("hitman1_stand")
        image_set_size(self.player_img, self.GRID_SPACING*.75, self.GRID_SPACING*.75)
        image_set_anchor_center(self.player_img)

        # -- enemy options
        self.enemy_img = Resources.instance.sprite("robot1_stand")
        image_set_size(self.enemy_img, self.GRID_SPACING*.75, self.GRID_SPACING*.75)
        image_set_anchor_center(self.enemy_img)

        self.enemy_target = Resources.instance.sprite("enemy_target")
        image_set_size(self.enemy_target, *(EditorViewport.GRID_SPACING,)*2)
        image_set_anchor_center(self.enemy_target)

    def reload(self):
        self = EditorViewport(self.data)

    def get_rect(self):
        width = window.width - EditorToolbar.WIDTH
        size = (width, window.height)
        center = (width/2 + EditorToolbar.WIDTH, window.height/2)
        return [center, size]

    def get_transform(self):
        return (self._pan_offset, self._zoom)

    @contextmanager
    def _editor_do_pan(self):
        glPushMatrix()
        glTranslatef(*self._pan_offset, 0)
        yield
        glPopMatrix()

    @contextmanager
    def _editor_do_zoom(self):
        glPushMatrix()
        glScalef(*self._zoom, 1)
        yield
        glPopMatrix()

    def _editor_draw_grid(self):
        glLineWidth(self.LINE_WIDTH)
        glBegin(GL_LINES)
        for y in range(0, self.GRID_SIZE, self.GRID_SPACING):
            glColor4f(1, 1, 1, 1)

            # -- vertical lines
            if y == 0:
                glColor4f(0, 0, 1, 1)
            glVertex2f(y, 0)
            glVertex2f(y, self.GRID_SIZE)

            # -- horizontal lines
            if y == 0:
                glColor4f(1, 0, 0, 1)
            glVertex2f(0, y)
            glVertex2f(self.GRID_SIZE, y)

        glEnd()

    def _editor_draw_map(self):
        for y, row in enumerate(self.data['map']):
            for x, data in enumerate(row):
                offx, offy = x * self.GRID_SPACING, y * self.GRID_SPACING
                if data == "#":
                    self.wall_img.blit(offx, offy, 0)
                elif data == ' ':
                    self.floor_img.blit(offx, offy, 0)

    def _editor_draw_player(self):
        self.player_img.blit(*self.data['player'], 0)

    def _editor_draw_enemies(self):
        for pos in self.data['enemies']:
            self.enemy_img.blit(*pos, 0)

        enemy_id = self.data.get('_active_enemy')
        if enemy_id:
            self.enemy_target.blit(*self.data['enemies'][enemy_id-1], 0)

    def _editor_draw_waypoints(self):
        waypoints = self.data.get('waypoints')
        if waypoints:
            # -- check if we have active enemy
            enemy_id = self.data.get('_active_enemy')
            if enemy_id:
                # -- select waypoints for active enemy
                points = waypoints[enemy_id-1]

                # -- draw waypoints
                draw_path(points, color=(0,0,1,1))
                for point in points:
                    draw_point(point, color=(1,1,1,1))

    def draw(self):
        glPushMatrix()
        glTranslatef(*self.OFFSET, 1)
        with self._editor_do_pan():
            with self._editor_do_zoom():
                self._editor_draw_grid()
                self._editor_draw_map()
                self._editor_draw_player()
                self._editor_draw_enemies()
                self._editor_draw_waypoints()
        glPopMatrix()

    def update(self, dt):
        pass

    def event(self, *args, **kwargs):
        _type = args[0]

        if _type == EventType.MOUSE_DRAG:
            x, y, dx, dy, but, mod = args[1:]
            if not mouse_over_rect((x, y), *self.get_rect()): return

            if but == mouse.MIDDLE:
                self._is_panning = True
                px, py = self._pan_offset
                px = 0 if (px+dx) > 0 else px+dx
                py = 0 if (py+dy) > 0 else py+dy
                self._pan_offset = (px, py)
        else:
            self._is_panning = False

        if _type == EventType.MOUSE_SCROLL:
            x, y, sx, sy = args[1:]
            if not mouse_over_rect((x, y), *self.get_rect()): return

            _sum = lambda x,y,val: (x+val, y+val)
            if sy < 0:
                self._zoom = _sum(*self._zoom, -self._zoom_sensitivity)
            else:
                self._zoom = _sum(*self._zoom,  self._zoom_sensitivity)

            # -- clamp zoom to (0.2, 10.0) and round to  d.p
            self._zoom = tuple(map(lambda x: clamp(x, 0.2, 10.0), self._zoom))
            self._zoom = tuple(map(lambda x: round(x, 1), self._zoom))


