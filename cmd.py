""" bridge for the command goes to simu or live in the config case or if css is vailable """
from . import config
if config.simulate:
    from . import cmdSimu as _cmd
    from .cmdSimu import * 
else:    
    try:
        from . import cmdLive as cmd
        from .cmdLive import * 
    except ModuleNotFoundError:
        print('CSS in Simu')
        from . import cmdSimu as cmd
        from .cmdSimu import * 
