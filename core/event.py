EVENT_METHS = [
    "on_draw",
    "on_key_press",
    "on_key_release",
    "on_mouse_drag",
    "on_mouse_motion",
    "on_mouse_press",
    "on_mouse_release",
    "on_mouse_scroll",
    "on_resize",
    "on_text",
    "on_text_motion",
    "on_text_motion_select",
]


def _pass_func(self, *args):
    pass


methods = {meth_name : _pass_func for meth_name in EVENT_METHS}
EventHandler = type("EventHandler", (object,), methods)
