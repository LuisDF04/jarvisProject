import os
import importlib.util
import inspect

class Plugin():
    def __init__(self):
        self.plugins = {}

    def load_plugins(self):
        plugin_dir = os.path.join(os.path.dirname(__file__), "plugins_library")
        # Ensure the directory exists to prevent FileNotFoundError
        os.makedirs(plugin_dir, exist_ok=True) 
        
        for filename in os.listdir(plugin_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = filename[:-3]
                file_path = os.path.join(plugin_dir, filename)
                
                # Load the module dynamically
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Register functions found in the plugin
                for name, func in inspect.getmembers(module, inspect.isfunction):
                    # Ensure we only load functions explicitly defined in the plugin file
                    if func.__module__ == module_name:
                        self.plugins[name] = func
                        print(f"[INFO] Plugin loaded: {name}")
                        
        return self.plugins