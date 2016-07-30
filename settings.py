from config import Config

default_settings = {
    'host': 'localhost',
    'port': 8080,
    'mongo_host': 'localhost',
    'mongo_port': 27017,
    'mongo_name': 'scc',}

configFile = file('settings.cfg')
cfg = Config(configFile)

app_settings = default_settings
app_settings.update(cfg)
