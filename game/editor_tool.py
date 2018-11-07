
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

