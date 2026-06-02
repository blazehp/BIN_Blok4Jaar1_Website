import requests as req

def get_creds():
    web_url = "https://blok4jaar1.up.railway.app/_creds"
    response = req.get(web_url)
    creds = response.json()
    return creds

def write_creds():
    creds = get_creds()
    with open(".env_new", "w") as file:
        content = f"""
        DB_USER = {creds.user}
        DB_PASSWORD = {creds.password}
        DB_HOST = {creds.host}
        DB_PORT = {creds.port}
        DB_DATABASE = {creds.database}
        DB_POOL_NAME = {creds.pool_name}
        DB_POOL_SIZE = {creds.pool_size}
        """
        file.write(content)
    return