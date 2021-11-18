import bpy, pickle, os


path = bpy.utils.resource_path("USER")
path_cookiesFolder = os.path.join(path, "cookies")
path_cookies_username = os.path.join(path_cookiesFolder, "username")


def remember_username(username):
    cookies_username = open(path_cookies_username, "wb")
    pickle.dump(username, cookies_username)
    cookies_username.close()


def read_remembered_username():
    if os.path.isfile(path_cookies_username):
        with open(path_cookies_username, "rb") as fr:
            data = pickle.load(fr)
        return data
    else:
        return ""


def delete_remembered_username():
    if os.path.isfile(path_cookies_username):
        os.remove(path_cookies_username)


def read_remembered_checkbox():
    if os.path.isfile(path_cookies_username):
        return True
    else:
        return False
