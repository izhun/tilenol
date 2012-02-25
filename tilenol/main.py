from functools import partial
import sys
import subprocess
import os.path

from zorro.di import DependencyInjector, di, has_dependencies, dependency

from .xcb import Connection, Proto, Core, Keysyms
from .keyregistry import KeyRegistry
from .events import EventDispatcher
from .window import Window
from .commands import CommandDispatcher, EnvCommands
from .config import Config


env_defaults = {
    'XDG_CONFIG_HOME': os.path.expanduser('~/.config'),
    }


@has_dependencies
class Tilenol(object):

    xcore = dependency(Core, 'xcore')
    dispatcher = dependency(EventDispatcher, 'event-dispatcher')
    config = dependency(Config, 'config')
    commander = dependency(CommandDispatcher, 'commander')

    def __init__(self, options):
        pass
        # extract options needed

    def register_hotkeys(self, keys):
        for key, cmd in self.config.keys():
            keys.add_key(key, self.commander.callback(*cmd))
        keys.register_keys(self.root_window)

    def run(self):

        proto = Proto()
        proto.load_xml('xproto')
        self.conn = conn = Connection(proto)
        conn.connection()
        self.root_window = Window(conn.init_data['roots'][0]['root'])

        inj = DependencyInjector()
        inj['xcore'] = Core(conn)
        inj['keysyms'] = keysyms = Keysyms()
        keysyms.load_default()
        keys = KeyRegistry()
        inj['key-registry'] = inj.inject(keys)
        inj['event-dispatcher'] = inj.inject(EventDispatcher())
        inj['config'] = inj.inject(Config())
        inj['commander'] = cmd = inj.inject(CommandDispatcher())
        cmd['env'] = EnvCommands()
        inj.inject(self)

        self.xcore.init_keymap()
        self.register_hotkeys(keys)
        self.setup_events()

        self.loop()

    def setup_events(self):
        EM = self.xcore.EventMask
        self.xcore.raw.ChangeWindowAttributes(
            window=self.root_window,
            params={
                self.xcore.CW.EventMask: EM.StructureNotify
                                      | EM.SubstructureNotify
                                      | EM.SubstructureRedirect
            })
        attr = self.xcore.raw.GetWindowAttributes(window=self.root_window)
        if not (attr['your_event_mask'] & EM.SubstructureRedirect):
            print("Probably another window manager is running", file=sys.stderr)
            return

    def loop(self):
        for i in self.conn.get_events():
            self.dispatcher.dispatch(i)