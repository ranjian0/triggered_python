
class Signal(object):
    # -- list of all signals
    DB = []
    # -- deffered signals i.e signals connected to before creation
    DEFFERED = []

    def __init__(self, name, instance=True):
        self.name = name
        self.slots = []

        if not instance:
            if name not in [s.name for s in Signal.DB]:
                Signal.DB.append(self)
                self._connect_deffered(name)


    def _connect_deffered(self, name):
        if name in map(op.itemgetter(0), Signal.DEFFERED):
            sname, target, meth = [sig for sig in Signal.DEFFERED
                                    if sig[0] == name][-1]
            self.connect(getattr(target, meth))

    def connect(self, slot):
        "slot: is a function / method"
        assert callable(slot)
        self.slots.append(slot)

    def disconnect(self, slot):
        self.slots.remove(slot)

    def __call__(self, *args, **kwargs):
        "Fire the signal to connected slots"
        for slot in self.slots:
            slot(*args, **kwargs)

    def __del__(self):
        self.slots.clear()
        if self in Signal.DB:
            Signal.DB.remove(self)

def create_signal(name):
    """ create a signal"""
    if name not in [s.name for s in Signal.DB]:
        return Signal(name, False)

def connect(signal_name, target, method):
    """ connect the method contained in target to a signal with signal_name"""
    for signal in Signal.DB:
        if signal.name == signal_name:
            signal.connect(getattr(target, method))
            break
    else:
        Signal.DEFFERED.append((signal_name, target, method))

def disconnect(signal_name, target, method):
    """ disconnect the method contained in target to a signal with signal_name"""
    for signal in Signal.DB:
        if signal.name == signal_name:
            signal.disconnect(getattr(target, method))
            break

def emit_signal(signal_name, *args, **kwargs):
    """ emit the signal called signal_name """
    for signal in Signal.DB:
        if signal.name == signal_name:
            signal(*args, **kwargs)

