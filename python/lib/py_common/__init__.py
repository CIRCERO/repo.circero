"""
py_common - Minimal implementation for Kodi addon
Provides logging and utility functions compatible with StashApp scrapers
"""

import xbmc

class Logger:
    """Simple logger compatible with StashApp's py_common.log"""
    
    @staticmethod
    def info(msg):
        xbmc.log("[py_common] INFO: {}".format(str(msg)), xbmc.LOGINFO)
    
    @staticmethod
    def debug(msg):
        xbmc.log("[py_common] DEBUG: {}".format(str(msg)), xbmc.LOGDEBUG)
    
    @staticmethod
    def warning(msg):
        xbmc.log("[py_common] WARNING: {}".format(str(msg)), xbmc.LOGWARNING)
    
    @staticmethod
    def error(msg):
        xbmc.log("[py_common] ERROR: {}".format(str(msg)), xbmc.LOGERROR)

# Create a global logger instance
log = Logger()
