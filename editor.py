import os
import pickle
import pyglet as pg

from utils import *
from resources import Resources, LevelData

class Editor:

    def __init__(self):
        self.levels = Resources.instance.levels()
        self.current = sorted(self.levels)[0]
        self.data = dict()

        self.load()

    def load(self):
        # -- load current leveldata
        for key, val in self.levels[self.current]._asdict().items():
            self.data[key] = val

        self.topbar = EditorTopbar(self.levels)
        self.toolbar = EditorToolbar(self.data)
        self.viewport = EditorViewport(self.data)

        # -- hook events
        self.topbar.new_btn.on_click(self.new)
        self.topbar.save_btn.on_click(self.save)

    def new(self):
        # -- create new level file
        new_level = Resources.instance.level(f"level_{len(self.levels)+1}")
        self.levels = Resources.instance.levels()

        # -- set as current level
        self.current = list(self.levels)[-1]
        for key, val in self.levels[self.current]._asdict().items():
            self.data[key] = val

        self.topbar.add_tab(self.current)


    def save(self):
        # -- remove temp data from self.data
        tmp_items = [key for key,v in self.data.items() if key.startswith('_')]
        tmp_data = [v for key,v in self.data.items() if key.startswith('_')]
        for it in tmp_items:
            del self.data[it]

        # -- save data
        ldata = LevelData(**self.data)
        f = open(self.current, 'wb')
        pickle.dump(ldata, f)

        # -- restore temp data from self.data
        for key,val in zip(tmp_items, tmp_data):
            self.data[key] = val

        # # --  update viewport
        self.viewport.reload(self.data)
        print("Saved -- > ", self.current)

    def draw(self):
        with reset_matrix(window.width, window.height):
            self.viewport.draw()
            self.toolbar.draw()
            self.topbar.draw()

    def update(self, dt):
        self.topbar.update(dt)
        self.toolbar.update(dt)
        self.viewport.update(dt)

        # -- check selected tab in topbar
        if self.topbar.tab_switched:
            self.current = sorted(self.levels, key=self.topbar.tab_sort_func)[self.topbar.active_level]
            self.data.clear()

            # -- change level
            for key, val in self.levels[self.current]._asdict().items():
                self.data[key] = val

            self.topbar.tab_switched = False

        # -- update tools for viewport transform
        for tool in self.toolbar.tools:
            tool.set_viewport_transform(self.viewport.get_transform())

    def event(self, *args, **kwargs):
        self.topbar.event(*args, **kwargs)
        self.toolbar.event(*args, **kwargs)
        self.viewport.event(*args, **kwargs)

class EditorTopbar:
    HEIGHT = 40

    def __init__(self, levels):
        self.levels = levels
        self.active_level = 0

        # -- topbar background
        self.topbar_settings = {
            "size" : (window.width, self.HEIGHT),
            "color" : (207, 188, 188, 255)
        }
        self.topbar = pg.image.SolidColorImagePattern(
            self.topbar_settings.get("color"))
        self.topbar_image = self.topbar.create_image(
            *self.topbar_settings.get("size"))

        # -- action buttons
        # -- images are 22x22, Toolbar width = 60
        hw = EditorToolbar.WIDTH / 2
        self.new_btn  = ImageButton("new",  (hw/2, window.height - self.HEIGHT/2))
        self.save_btn = ImageButton("save", (hw*1.5, window.height - self.HEIGHT/2))

        # -- tab buttons
        self.max_tabs = 4
        self.tabs_batch = pg.graphics.Batch()
        self.inactive_color = (50, 50, 50, 200)
        self.tab_sort_func = lambda n: int(os.path.basename(n).split('.')[0].split('_')[-1])
        self.tabs = [
            TextButton(os.path.basename(level), bold=False, font_size=14, color=self.inactive_color,
                        anchor_x='center', anchor_y='center', batch=self.tabs_batch)
            for idx, level in enumerate(sorted(self.levels, key=self.tab_sort_func)
            )]

        self.tabs[self.active_level].bold = True
        self.init_tabs()
        for tab in self.tabs:
            tab.on_click(self.switch_level, tab.text)

        # - tab switching flags
        self.tab_switched = False

    def switch_level(self, level_txt):
        self.tab_switched = True
        for idx, level in enumerate(sorted(self.levels, key=self.tab_sort_func)):
            if os.path.basename(level) == level_txt:
                self.active_level = idx
                break

        # -- set clicked tab to bold
        for idx, tab in enumerate(self.tabs):
            if idx == self.active_level:
                tab.bold = True
            else:
                tab.bold = False

    def add_tab(self, level):
        # -- update list of levels from resources
        self.levels = Resources.instance.levels()
        # -- add a new tab and set as active
        ntab =  TextButton(os.path.basename(level), bold=False, font_size=14, color=self.inactive_color,
            anchor_x='center', anchor_y='center', batch=self.tabs_batch)
        ntab.on_click(self.switch_level, ntab.text)
        self.tabs.append(ntab)

        self.active_level = len(self.tabs)-1
        self.switch_level(ntab.text)
        self.init_tabs()

    def init_tabs(self):
        margin = 15
        start_x = EditorToolbar.WIDTH

        for idx, tab in enumerate(self.tabs):
            w, h = tab.get_size()

            tab.x = start_x + (w/2) + (idx*w) + ((idx+1) * margin)
            tab.y = window.height - self.HEIGHT/2

        # -- recalculate max_tabs based on tabs and window width
        bar_width = window.width - EditorToolbar.WIDTH
        tab_averge_width = sum([t.get_size()[0] + margin for t in self.tabs]) / len(self.tabs)
        self.max_tabs  = int(bar_width / tab_averge_width)

    def draw(self):
        # -- draw background
        self.topbar_image.blit(EditorToolbar.WIDTH+2, window.height-self.HEIGHT)
        draw_line((0, window.height-self.HEIGHT), (window.width, window.height-self.HEIGHT), color=(.1, .1, .1, .8), width=5)

        # -- draw action buttons
        self.new_btn.draw()
        self.save_btn.draw()

        # -- draw tab buttons
        if len(self.tabs) <= self.max_tabs:
            self.tabs_batch.draw()
        else:
            for i in range(self.max_tabs):
                self.tabs[i].draw()


    def update(self, dt):
        pass

    def event(self, *args, **kwargs):
        # -- handle resize
        _type = args[0]
        if _type == EventType.RESIZE:
            _,w,h = args
            self.init_tabs()
            hw = EditorToolbar.WIDTH / 2
            self.new_btn.update(hw/2, h - self.HEIGHT/2)
            self.save_btn.update(hw*1.5, h - self.HEIGHT/2)

            self.topbar_settings['size'] = (w, self.HEIGHT)
            self.topbar_image = self.topbar.create_image(
                *self.topbar_settings.get("size"))

        self.new_btn.event(*args, **kwargs)
        self.save_btn.event(*args, **kwargs)
        for tab in self.tabs:
            tab.event(*args, **kwargs)

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

        self.tool_start_loc = (0, window.height - EditorTopbar.HEIGHT)
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
        center = (self.WIDTH/2, (window.height-EditorTopbar.HEIGHT)/2)
        size = (self.WIDTH, window.height-EditorTopbar.HEIGHT)
        return [center, size]

    def draw(self):
        self.toolbar_image.blit(0, -EditorTopbar.HEIGHT)
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
            self.tool_start_loc = (0, h- EditorTopbar.HEIGHT)
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

    def reload(self, data):
        self.data = data
        self = EditorViewport(data)

    def get_rect(self):
        width = window.width - EditorToolbar.WIDTH
        height = window.height - EditorTopbar.HEIGHT
        size = (width, height)
        center = (width/2 + EditorToolbar.WIDTH, height/2)
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
        draw_point(self.get_rect()[0])

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


class EditorTool:

    tools = []
    def __new__(cls):
        instance = object.__new__(cls)
        EditorTool.tools.append(instance)
        return instance

    def __init__(self, options):
        # -- options
        # -- e.g {'Add Player' : player_image, 'Add_Enemy' : enemy_image}
        self.options = options
        self.level_data = None

        self.position = (0, 0)
        self.size = (0, 0)

        # -- set image anchors to center:
        for _,img in self.options.items():
            image_set_anchor_center(img)

        self.default = list(options)[0]

        self.tool_background = Resources.instance.sprite("tool_background")
        image_set_anchor_center(self.tool_background)

        self.tool_indicator = Resources.instance.sprite("tool_indicator")
        image_set_anchor_center(self.tool_indicator)

        self.tool_active = Resources.instance.sprite("tool_select")
        image_set_anchor_center(self.tool_active)

        # -- flags to show optional tools
        self.mouse_down_duration = 0
        self.mouse_hold_duration = .5
        self.start_show_event = False
        self.show_options = False

        # -- flags for active state of the tool
        self.is_active = False
        self.activated = False

        # -- flag to track viewport transform
        self._viewport_pan = (0, 0)
        self._viewport_zoom = (1, 1)

    def set_data(self, val):
        self.level_data = val

    def set_viewport_transform(self, val):
        self._viewport_pan = val[0]
        self._viewport_zoom = val[1]

    def mouse_pos_to_viewport(self, x, y):
        # -- convert mouse position to viewport position
        # -- subtract editor offset
        ox, oy = EditorViewport.OFFSET
        px, py = x-ox, y-oy

        # -- transform viewport pan
        panx, pany = self._viewport_pan
        px, py = px-panx, py-pany

        # -- transform viewport scale
        zx, zy = self._viewport_zoom
        px, py = px*(1/zx), py*(1/zy)
        return px, py

    def mouse_pos_to_map(self, x, y):
        # -- convert mouse position to map array indices
        vx, vy = self.mouse_pos_to_viewport(x, y)
        gs = EditorViewport.GRID_SPACING
        return int(vx) // gs, int(vy) // gs

    def draw(self):
        # -- draw tool background
        self.tool_background.blit(*self.position)

        # -- draw default tool
        img = self.options[self.default]
        img.blit(*self.position)

        # -- draw tool indicator
        if len(self.options.items()) > 1:
            # -- draw small arror to indicate more than one option
            if not self.show_options:
                self.tool_indicator.blit(*self.position)

        # -- draw tool active
        if self.is_active:
            self.tool_active.blit(*self.position)

        # -- draw all tool option when mouse held down
        # -- this will be drawn a little off side
        if self.show_options and len(self.options.items()) > 1:
            offx = 50
            for idx, (name, image) in enumerate(self.options.items()):
                idx += 1
                px, py = self.position
                loc = (px + (idx*offx), py)
                self.tool_background.blit(*loc)
                image.blit(*loc)

    def update(self, dt):
        if self.start_show_event:
            self.mouse_down_duration += dt

            if self.mouse_down_duration >= self.mouse_hold_duration:
                self.show_options = True
                self.start_show_event = False
                self.mouse_down_duration = 0

    def event(self, _type, *args, **kwargs):

        if _type == EventType.MOUSE_DOWN:
            x, y, btn, mod = args
            if btn == mouse.LEFT and mouse_over_rect((x, y), self.position, self.size):
                self.start_show_event = True

        if _type == EventType.MOUSE_UP:
            x, y, btn, mod = args
            if btn == mouse.LEFT:
                if self.start_show_event or self.show_options:
                    self.activated = True

                if self.start_show_event:
                    self.start_show_event = False

                if self.show_options:
                    # -- check if mouse was released over a tool option
                    # --  set that tool as active
                    offx = 50
                    for idx, (name, image) in enumerate(self.options.items()):
                        idx += 1
                        px, py = self.position
                        loc = (px + (idx*offx), py)
                        if mouse_over_rect((x,y), loc, self.size):
                            self.default = list(self.options)[idx-1]

                    self.show_options = False

class AddTileTool(EditorTool):
    def __init__(self):
        opts = {
            "Wall" : Resources.instance.sprite("tool_wall"),
            "Floor" : Resources.instance.sprite("tool_floor")
        }
        super(AddTileTool, self).__init__(opts)

    def _map_add_tile(self, idx, idy, data):
        _map = self.level_data.get('map')

        # -- modifiy map list to accomodate new wall
        items_to_add = (idx+1) - len(_map[0])
        rows_to_add = (idy+1) - len(_map)
        len_rows = len(_map[0])

        # -- add new rows
        if rows_to_add:
            for i in range(rows_to_add):
                _map.append(['' for _ in range(len_rows)])

        # -- add new items
        if items_to_add:
            for row in _map:
                    for _ in range(items_to_add):
                        row.append('')

        # -- set wall at target index
        _map[idy][idx] = data

    def _map_add_wall_at(self, idx, idy):
        _map = self.level_data.get('map')
        if _map:
            # -- ensure list contains data
            if idy < len(_map) and idx < len(_map[0]):
                _map[idy][idx] = '#'
            else:
                self._map_add_tile(idx, idy, '#')

    def _map_remove_wall_at(self, idx, idy):
        _map = self.level_data.get('map')
        if _map:
            # -- ensure list contains data
            if idy < len(_map) and idx < len(_map[0]):
                _map[idy][idx] = ''

    def _map_add_floor_at(self, idx, idy):
        _map = self.level_data.get('map')
        if _map:
            # -- ensure list contains data
            if idy < len(_map) and idx < len(_map[0]):
                _map[idy][idx] = ' '
            else:
                self._map_add_tile(idx, idy, ' ')

    def _map_remove_floor_at(self, idx, idy):
        _map = self.level_data.get('map')
        if _map:
            # -- ensure list contains data
            if idy < len(_map) and idx < len(_map[0]):
                _map[idy][idx] = ''

    def event(self, _type, *args, **kwargs):
        super(AddTileTool, self).event(_type, *args, **kwargs)
        if not self.is_active: return

        if _type == EventType.MOUSE_DRAG or _type == EventType.MOUSE_DOWN:
            x,y,*_,but,mod = args
            # -- ensure mouse if over viewport
            if x < EditorToolbar.WIDTH: return

            if but == mouse.LEFT:
                # -- if we are showing tool options for other tools, return
                for tool in EditorTool.tools:
                    if tool.show_options:
                        return

                map_id = self.mouse_pos_to_map(x, y)
                if self.default == 'Wall':
                    if mod & key.MOD_CTRL:
                        self._map_remove_wall_at(*map_id)
                    else:
                        self._map_add_wall_at(*map_id)
                elif self.default == 'Floor':
                    if mod & key.MOD_CTRL:
                        self._map_remove_floor_at(*map_id)
                    else:
                        self._map_add_floor_at(*map_id)

class AddAgentTool(EditorTool):
    def __init__(self):
        opts = {
            "Player" : Resources.instance.sprite("tool_player"),
            "Enemy" : Resources.instance.sprite("tool_enemy"),
            # "NPC" : Resources.instance.sprite("tool_npc")
        }
        super(AddAgentTool, self).__init__(opts)

    def event(self, _type, *args, **kwargs):
        super(AddAgentTool, self).event(_type, *args, **kwargs)
        if not self.is_active: return

        if _type == EventType.MOUSE_DOWN:
            x, y, but, mod = args
            # -- ensure mouse if over viewport
            if x < EditorToolbar.WIDTH: return

            if but == mouse.LEFT:
                px, py = self.mouse_pos_to_viewport(x, y)

                if self.default == 'Player':
                    self.level_data['player'] = (px, py)
                elif self.default == 'Enemy':
                    if mod & key.MOD_CTRL:
                        enemies = self.level_data['enemies']
                        waypoints = self.level_data['waypoints']
                        for idx, en in enumerate(enemies):
                            if mouse_over_rect((px,py), en, (EditorViewport.GRID_SPACING*.75,)*2):
                                self.level_data['enemies'].remove(en)
                                self.level_data['waypoints'].remove(waypoints[idx])
                    else:
                        self.level_data['enemies'].append((px, py))
                        self.level_data['waypoints'].append([])

class AddWaypointTool(EditorTool):
    def __init__(self):
        opts = {
            "Waypoint" : Resources.instance.sprite("tool_waypoint"),
        }
        super(AddWaypointTool, self).__init__(opts)

    def event(self, _type, *args, **kwargs):
        super(AddWaypointTool, self).event(_type, *args, **kwargs)
        if not self.is_active: return

        if _type == EventType.MOUSE_DOWN:
            x, y, but, mod = args
            px, py = self.mouse_pos_to_viewport(x, y)

            # -- ensure mouse if over viewport
            if x < EditorToolbar.WIDTH: return

            # -- create waypoint
            if but == mouse.LEFT:
                # -- check if an enemy is selected
                enemy_id = self.level_data.get('_active_enemy')
                if enemy_id:
                    # -- ensure waypoint list exist
                    waypoints = self.level_data.get('waypoints')
                    if not waypoints:
                        self.level_data['waypoints'] = []
                        waypoints = self.level_data['waypoints']

                    # -- check if waypoints exist for all enemies
                    missing = len(self.level_data['enemies']) > len(waypoints)
                    if missing:
                        for _ in range(len(self.level_data['enemies']) - len(waypoints)):
                            waypoints.append([])


                    if mod & key.MOD_CTRL:
                        # -- remove waypoint at mouse location
                        selected = None
                        for point in waypoints[enemy_id-1]:
                            if mouse_over_rect((px, py), point, (10, 10)):
                                selected = point
                                break
                        if selected:
                            waypoints[enemy_id-1].remove(selected)
                    else:
                        # -- add mouse location to the selected enemy waypoints
                        waypoints[enemy_id-1].append((px, py))

            # -- select enemy
            elif but == mouse.RIGHT:
                if mod & key.MOD_CTRL:
                    if self.level_data.get('_active_enemy'):
                        del self.level_data['_active_enemy']
                else:
                    enemies = self.level_data['enemies']
                    for idx, en in enumerate(enemies):
                        if mouse_over_rect((px,py), en, (EditorViewport.GRID_SPACING*.75,)*2):
                            self.level_data['_active_enemy'] = idx+1

class ObjectivesTool(EditorTool):
    def __init__(self):
        opts = {
            "Objectives" : Resources.instance.sprite("tool_objectives"),
        }
        super(ObjectivesTool, self).__init__(opts)

        self.num_inputs = 1
        self.active_field = None
        self.input_fields = []

        self._add_fields()

    def _add_fields(self):
        pad = (5, 5)
        px, py = [ox+px for ox,px in zip(EditorViewport.OFFSET, pad)]

        w, h, fs = 400, 35, 18
        hoff = py + (len(self.input_fields) * h)
        for idx in range(self.num_inputs - len(self.input_fields)):
            self.input_fields.append(
                TextInput("Enter Objective", px, hoff+(idx*h), w) #(w, h), {'color':(0, 0, 0, 255), 'font_size':fs})
            )

    def _remove_fields(self):
        if len(self.input_fields) >  self.num_inputs:
            del self.input_fields[self.num_inputs:]

    def event(self, _type, *args, **kwargs):
        super(ObjectivesTool, self).event(_type, *args, **kwargs)
        if self.is_active:
            for field in self.input_fields:
                field.event(_type, *args, **kwargs)

            if _type == EventType.KEY_DOWN:
                symbol, mod = args
                if symbol == key.RETURN:
                    if mod & key.MOD_CTRL:
                        self.num_inputs = max(1, self.num_inputs-1)
                        self._remove_fields()
                    else:
                        self.num_inputs += 1
                        self._add_fields()

                    self.input_fields[self.num_inputs-1].set_focus()

    def draw(self):
        super(ObjectivesTool, self).draw()
        if self.is_active:
            for field in self.input_fields:
                field.draw()


'''
============================================================
---   MAIN
============================================================
'''

# -- create window
window = pg.window.Window(800, 600, resizable=True)
window.set_minimum_size(800, 600)
window.set_caption("Triggered LevelEditor")

res    = Resources()
editor = Editor()


glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
glEnable(GL_BLEND)

@window.event
def on_draw():
    window.clear()
    glClearColor(.39, .39, .39, 1)

    editor.draw()

@window.event
def on_resize(w, h):
    editor.event(EventType.RESIZE, w, h)

@window.event
def on_key_press(symbol, modifiers):
    editor.event(EventType.KEY_DOWN, symbol, modifiers)

@window.event
def on_key_release(symbol, modifiers):
    editor.event(EventType.KEY_UP, symbol, modifiers)

@window.event
def on_mouse_press(x, y, button, modifiers):
    editor.event(EventType.MOUSE_DOWN, x, y, button, modifiers)

@window.event
def on_mouse_release(x, y, button, modifiers):
    editor.event(EventType.MOUSE_UP, x, y, button, modifiers)

@window.event
def on_mouse_motion(x, y, dx, dy):
    editor.event(EventType.MOUSE_MOTION, x, y, dx, dy)

@window.event
def on_mouse_drag(x, y, dx, dy, button, modifiers):
    editor.event(EventType.MOUSE_DRAG, x, y, dx, dy, button, modifiers)

@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    editor.event(EventType.MOUSE_SCROLL, x, y, scroll_x, scroll_y)

@window.event
def on_text(text):
    editor.event(EventType.TEXT, text)

@window.event
def on_text_motion(motion):
    editor.event(EventType.TEXT_MOTION, motion)

@window.event
def on_text_motion_select(motion):
    editor.event(EventType.TEXT_MOTION_SELECT, motion)

def on_update(dt):
    editor.update(dt)

if __name__ == '__main__':
    pg.clock.schedule_interval(on_update, 1/60)
    pg.app.run()