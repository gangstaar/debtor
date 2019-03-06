import os
from werkzeug.security import generate_password_hash, check_password_hash

user_data_path = './userdata/'
password_hash_file_name = 'password'
if not os.path.exists(user_data_path):
    os.mkdir(user_data_path)


def check_user_exists(user_name):
    if os.path.exists(user_data_path+user_name+'/'):
        return True
    else:
        return False


def check_user_without_password(user_name):
    if check_user_exists(user_name) and not os.path.exists(user_data_path+user_name+'/'+password_hash_file_name):
        return True
    else:
        return False


def check_user_password(name, password):
    if not check_user_exists(name):
        return False

    if check_user_without_password(name):
        return False

    file_name = user_data_path + name + '/password'
    f = open(file_name, 'r')
    lin = f.readline().rstrip().split(' = ')

    if len(lin) < 2:
        return False

    lin = lin[1]
    if check_password_hash(lin, password):
        return True
    else:
        return False


def register_new_user(user_name, password):
    #  type: (str, str) -> bool

    if check_user_exists(user_name) and not check_user_without_password(user_name):
        return False

    user_directory = user_data_path + user_name + '/'
    if not check_user_exists(user_name):
        os.mkdir(user_directory)

    if not os.path.exists(user_directory):
        return False

    f = open(user_data_path+user_name+'/'+password_hash_file_name, 'w')
    password_hash = generate_password_hash(password)
    f.write('PASSWORD_HASH = ' + password_hash)
    f.close()

    return True


def get_user_path(user_name):
    return './userdata/' + user_name + '/'
