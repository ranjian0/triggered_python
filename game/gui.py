import sys
import pyglet as pg
from pyglet.window import mouse
from pyglet.text import layout, caret, document

from .level     import LevelManager
from .signal    import emit_signal, create_signal
from .core      import (
    EventType,
    get_window,
    reset_matrix,
    mouse_over_rect)

class MainMenu:

    def __init__(self):
        window = get_window()

        self.title = pg.text.Label("TRIGGERED",
            bold=True, color=(255, 255, 0, 255),
            font_size=48, x=window.width/2, y=window.height*.9,
            anchor_x='center', anchor_y='center')

        self.quit = TextButton("QUIT", bold=True, font_size=32,
                                anchor_x='center', anchor_y='center')
        self.quit.x = self.quit.content_width
        self.quit.y = self.quit.content_height
        self.quit.hover_color = (255, 255, 0, 255)
        self.quit.on_click(sys.exit)

        self.level_options = []
        self.level_batch = pg.graphics.Batch()
        for idx, level in enumerate(LevelManager.instance.levels):
            btn = TextButton(level.name, bold=True, font_size=28,
                                anchor_x='center', anchor_y='center',
                                batch=self.level_batch)
            btn.x = window.width/4
            btn.y = (window.height*.8)-((idx+1)*btn.content_height)
            btn.hover_color = (200, 0, 0, 255)
            btn.on_click(self.select_level, level.name)

            self.level_options.append(btn)

        create_signal("start_game")

    def select_level(self, name):
        LevelManager.instance.set(name)
        emit_signal("start_game")

    def draw(self):
        with reset_matrix():
            self.title.draw()
            self.quit.draw()
            self.level_batch.draw()

    def event(self, _type, *args, **kwargs):
        window = get_window()

        if _type == EventType.RESIZE:
            w, h = args

            self.title.x = w/2
            self.title.y = h*.9

            self.quit.x = self.quit.content_width
            self.quit.y = self.quit.content_height

            for idx, txt in enumerate(self.level_options):
                txt.x = window.width/4
                txt.y = (window.height*.8)-((idx+1)*txt.content_height)

        self.quit.event(_type, *args, **kwargs)
        for option in self.level_options:
            option.event(_type, *args, **kwargs)


    def update(self, dt):
        pass

class PauseMenu:

    def __init__(self):
        window = get_window()

        self.title = pg.text.Label("PAUSED",
            bold=True, color=(255, 255, 0, 255),
            font_size=48, x=window.width/2, y=window.height*.9,
            anchor_x='center', anchor_y='center')
        actions = {"Resume":self.resume, "Restart":self.restart, "Mainmenu":self.mainmenu}
        self.options = []
        self.options_batch = pg.graphics.Batch()
        for idx, (act, callback) in enumerate(actions.items()):
            btn = TextButton(act, bold=True, font_size=32,
                anchor_x='center', anchor_y='center',
                batch=self.options_batch)
            btn.x = window.width/2
            btn.y = (window.height*.7) - (idx * btn.content_height)

            btn.hover_color = (255, 0, 0, 255)
            btn.on_click(callback)
            self.options.append(btn)

    def resume(self):
        game.state = GameState.RUNNING

    def restart(self):
        LevelManager.instance.load()
        game.state = GameState.RUNNING

    def mainmenu(self):
        game.state = GameState.MAINMENU

    def reload(self, *args):
        window = get_window()

        self.title.x = window.width/2
        self.title.y = window.height*.9

        for idx, opt in enumerate(self.options):
            opt.x = window.width/2
            opt.y = (window.height*.7) - (idx * opt.content_height)

    def draw(self):
        with reset_matrix():
            self.title.draw()
            self.options_batch.draw()

    def event(self, _type, *args, **kwargs):
        if _type == EventType.RESIZE:
            w, h = args
            self.reload()

        for opt in self.options:
            opt.event(_type, *args, **kwargs)

    def update(self, dt):
        pass

class InfoPanel:
    MINIMAP_AGENT_SIZE = 25

    def __init__(self, level_name, objs, _map, agents):
        self.level_name = level_name
        self.objectives = objs
        self.map = _map
        self.agents = agents

        self.reload()

        # -- minimap images
        player_img = Resources.instance.sprite("minimap_player")
        image_set_size(player_img, *(self.MINIMAP_AGENT_SIZE,)*2)
        image_set_anchor_center(player_img)
        self.minimap_player = pg.sprite.Sprite(player_img)

        enemy_img = Resources.instance.sprite("minimap_enemy")
        image_set_size(enemy_img, *(self.MINIMAP_AGENT_SIZE,)*2)
        image_set_anchor_center(enemy_img)

        num_enemies = len([a for a in self.agents if isinstance(a, Enemy)])
        self.minimap_enemies = [pg.sprite.Sprite(enemy_img) for _ in range(num_enemies)]

    def reload(self):
        self.panel = self.create_panel()
        self.title = self.create_title()
        self.objs = self.create_objectives()
        self.minimap = self.create_minimap()

    def draw(self):
        with reset_matrix():
            self.panel.blit(0, 0)
            self.title.draw()
            self.objs.draw()
            self.minimap.draw()
            self.draw_minimap_agents()

    def update(self, dt):
        # -- update position of agents on minimap
        w, h = self.minimap.width, self.minimap.height
        offx, offy = self.minimap.x - w, self.minimap.y - h
        sx, sy = [mini/_map for mini, _map in zip((w,h), self.map.size())]

        e_idx = 0
        for agent in self.agents:
            px, py = agent.pos
            _x = offx + (px*sx)
            _y = offy + (py*sy)

            if isinstance(agent, Player):
                self.minimap_player.update(x=_x, y=_y)
            elif isinstance(agent, Enemy):
                self.minimap_enemies[e_idx].update(x=_x, y=_y)
                e_idx += 1

    def event(self, _type, *args, **kwargs):
        if _type == EventType.RESIZE:
            self.reload()

    def create_panel(self):
        w, h = window.get_size()
        img = pg.image.SolidColorImagePattern((100, 100, 100, 200))
        panel_background = img.create_image(w, h)
        return panel_background

    def create_title(self):
        w, h = window.get_size()
        level_name = pg.text.Label(self.level_name.title(), color=(255, 0, 0, 200),
            font_size=24, x=w/2, y=h*.95, anchor_x='center', anchor_y='center', bold=True)
        return level_name

    def create_objectives(self):
        txt_objs = "".join(["- "+obj+'\n' for obj in self.objectives])
        text = f"""Objectives:\n {txt_objs}"""
        w, h = window.get_size()

        return pg.text.Label(text, color=(255, 255, 255, 200), width=w/3,
            font_size=16, x=15, y=h*.9, anchor_y='top', multiline=True, italic=True)

    def create_minimap(self):
        w, h = window.get_size()

        msx, msy = w*.75, h*.9
        minimap = self.map.make_minimap((msx, msy), (255, 255, 255, 150))
        minimap.image.anchor_x = minimap.image.width
        minimap.image.anchor_y = minimap.image.height
        minimap.x = w
        minimap.y = h*.9
        return minimap

    def draw_minimap_agents(self):
        e_idx = 0
        for agent in self.agents:
            if isinstance(agent, Player):
                self.minimap_player.draw()
            elif isinstance(agent, Enemy):
                self.minimap_enemies[e_idx].draw()
                e_idx += 1


class TextInput:

    def __init__(self, text, x, y, width):
        self.batch = pg.graphics.Batch()

        self.document = pyglet.text.document.UnformattedDocument(text)
        self.document.set_style(0, len(self.document.text), dict(color=(0, 0, 0, 255)))
        font = self.document.get_font()
        height = font.ascent - font.descent

        self.layout = pyglet.text.layout.IncrementalTextLayout(
            self.document, width, height, multiline=False, batch=self.batch)
        self.caret = pyglet.text.caret.Caret(self.layout)

        self.layout.x = x
        self.layout.y = y

        # Rectangular outline
        pad = 2
        self.add_background(x - pad, y - pad,
                            x + width + pad, y + height + pad)

        self.text_cursor = window.get_system_mouse_cursor('text')
        self.set_focus()

    def hit_test(self, x, y):
        return (0 < x - self.layout.x < self.layout.width and
                0 < y - self.layout.y < self.layout.height)

    def add_background(self, x1, y1, x2, y2):
        vert_list = self.batch.add(4, pyglet.gl.GL_QUADS, None,
                                     ('v2i', [x1, y1, x2, y1, x2, y2, x1, y2]),
                                     ('c4B', [200, 200, 220, 255] * 4))

    def draw(self):
        self.batch.draw()

    def event(self, _type, *args, **kwargs):
        type_map = {
            EventType.MOUSE_MOTION : self._on_mouse_motion,
            EventType.MOUSE_DOWN : self._on_mouse_press,
            EventType.MOUSE_DRAG : self._on_mouse_drag,
            EventType.TEXT : self._on_text,
            EventType.TEXT_MOTION : self._on_text_motion,
            EventType.TEXT_MOTION_SELECT : self._on_text_motion_select
        }
        if _type in type_map.keys():
            type_map[_type](*args, **kwargs)

    def _on_mouse_motion(self, x, y, dx, dy):
        window = get_window()
        if self.hit_test(x, y):
            window.set_mouse_cursor(self.text_cursor)
        else:
            window.set_mouse_cursor(None)

    def _on_mouse_press(self, x, y, button, modifiers):
        if self.hit_test(x, y):
            self.set_focus()
            self.caret.on_mouse_press(x, y, button, modifiers)
        else:
            self.set_focus(False)

    def _on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.hit_test(x, y):
            self.caret.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def _on_text(self, text):
        self.caret.on_text(text)

    def _on_text_motion(self, motion):
        self.caret.on_text_motion(motion)

    def _on_text_motion_select(self, motion):
        self.caret.on_text_motion_select(motion)

    def set_focus(self, focus=True):
        if focus:
            self.caret.visible = True
        else:
            self.caret.visible = False
            self.caret.mark = self.caret.position = 0

class Button(object):

    def __init__(self):
        self._callback = None
        self._callback_args = ()

    def on_click(self, action, *args):
        if callable(action):
            self._callback = action
            self._callback_args = args

    def hover(self, x, y):
        return NotImplementedError()

    def event(self, _type, *args, **kwargs):
        if _type == EventType.MOUSE_MOTION:
            x, y, *_ = args
            self.hover(x,y)

        elif _type == EventType.MOUSE_DOWN:
            x, y, btn, mod = args

            if btn == mouse.LEFT:
                if self.hover(x,y):
                    self._callback(*self._callback_args)

class TextButton(pg.text.Label, Button):

    def __init__(self, *args, **kwargs):
        pg.text.Label.__init__(self, *args, **kwargs)
        Button.__init__(self)

        self._start_color = self.color
        self._hover_color = (200, 0, 0, 255)

    def _set_hcolor(self, val):
        self._hover_color = val
    hover_color = property(fset=_set_hcolor)

    def get_size(self):
        return self.content_width, self.content_height

    def hover(self, x, y):
        center = self.x, self.y
        if mouse_over_rect((x,y), center, self.get_size()):
            self.color = self._hover_color
            return True

        self.color = self._start_color
        return False

class ImageButton(Button):

    def __init__(self, image):
        Button.__init__(self)

    def hover(self, x, y):
        return False
