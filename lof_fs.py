import os

class resource_type:
    
    def __init__ (self, subdir, ext):
        assert type(subdir) == str, "subdir must be a string!"
        assert type(ext) == str, "ext must be a string!"
        self.subdir = subdir
        self.ext = ext


class fs:
    """For accessing the game's resources. Multiple instances can exist at once."""
    
    def __init__ (self, datapath):
        assert type(datapath) == str, "datapath must be a string!"
        self.datapath = datapath
        self.restypes = {}
        self.ext_delim = "."
    
    def add_resource_type ( self, resource_type_name, 
                            resource_type_subdir, resource_type_fileext ):
        assert type(resource_type_name) == str, \
                "resource_type_name must be a string!"
        self.restypes[resource_type_name] = \
                resource_type (resource_type_subdir, resource_type_fileext)
    
    def locate_resource (self, resource_type_name, resource_name):
        """Returns a file name"""
        assert resource_type_name in self.restypes, \
                "Unknown resource type "+repr(resource_type_name)
        assert type(resource_name) == str, "resource_name must be a string!"
        restype = self.restypes[resource_type_name]
        respath = os.path.join (self.datapath, restype.subdir, 
                                resource_name + self.ext_delim +
                                restype.ext)
        return respath

