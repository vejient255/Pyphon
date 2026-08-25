import os
import sys

# Patch app to print loop info
import core.app
original_procesar = core.app.MobileApp._procesar_eventos

def patched_procesar(self):
    events = getattr(self, "eventos_count", 0)
    if events == 0:
        print("FIRST FRAME")
    self.eventos_count = events + 1
    
    import sdl2
    evts = sdl2.ext.get_events()
    for event in evts:
        print(f"EVENT: {event.type}")
        if event.type == sdl2.SDL_QUIT:
            print("QUIT EVENT RECEIVED!")
            self.running = False
            
    # call rest of it maybe or just do it ourselves:
    for event in evts:
        pass # we just wanted to log

core.app.MobileApp._procesar_eventos = patched_procesar

import main
main.run_test()
