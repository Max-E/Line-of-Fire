from lof_fs import fs

class renderer:
    
    def __init__ (self, *rest):
        self.fs = fs("lof_data")
        self._init_dpy (*rest)
        self._init_res (*rest)

