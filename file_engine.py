from collections import OrderedDict
from werkzeug.utils import secure_filename
from class_list import classes
from threading import Thread
from magic import from_file
import os, shutil, class_list, sys, bitmath, subprocess, base64, time, traceback

active = OrderedDict()

root_path = os.getcwd()

class Upload:
    def __init__(self, file_name, upload_type, downloadable, quarter, year, hashpath, author):
        self.file_name, self.file_ext = ext_ract(file_name)
        self.upload_type = upload_type
        self.size = bitmath.Byte(bytes=os.path.getsize(hashpath)).best_prefix().format("{value:.2f} {unit}")
        self.downloadable = downloadable
        self.quarter = quarter
        self.year = year
        self.hashpath = hashpath
        self.author = author
    def listify(self):
        return [self.file_name, self.file_ext,  self.quarter, self.year, self.downloadable, self.size, self.upload_type, self.hashpath, self.author]

def ext_ract(file_name):
    ext = ''
    i = len(file_name) - 1
    while file_name[i] != '.' and i > 0:
        ext = file_name[i] + ext
        i -= 1
    if i == 0:
        return (file_name, '')
    return (file_name[:i], ext)

def setup_dirs():
    try:
        os.chdir(root_path + '/files')
        for directory in classes:
            if not os.path.exists(directory):
                os.makedirs(directory)
            os.chdir(directory)
            for subdir in classes[directory]:
                if not os.path.exists(subdir[0]):
                    os.makedirs(subdir[0])
                os.chdir(subdir[0])
                open(subdir[0] + '.meta', 'a')
                os.chdir(root_path + '/files/' + directory)
            os.chdir(root_path + '/files')
    except:
        print('Failure: setup_dirs')
        traceback.print_exc()
    os.chdir(root_path)

def rm_dirs():
    try:
        os.chdir('files')
        for directory in classes:
            if os.path.exists(directory):
                shutil.rmtree(directory)
    except:
        print('Failure: cd ' + root_path)
        traceback.print_exc()
    os.chdir(root_path)

def check_whitelist(key, classnum):
    if key in classes and classnum in [keys[0] for keys in classes[key]]:
        return True
    return False

def file_list(key, classnum, cur_user):
    file_list = list()
    try:
        if check_whitelist(key, classnum):
            os.chdir('files/'+ key + '/' + classnum)
            metafile = open(classnum + '.meta', 'r')
            for i in metafile:
                splittext = i.split(';')
                file_list.append(Upload(splittext[0].strip(), splittext[1].strip(), splittext[2].strip(), splittext[3].strip(), splittext[4].strip(), splittext[5].strip(), splittext[6].strip() == cur_user).listify())
    except:
        print('Failure: file_list')
        traceback.print_exc()
    os.chdir(root_path)
    return file_list

def search_all(query, cur_user):
    search_list = list()
    splitquery = query.lower().split()
    try:
        for i in classes:
            for j in classes[i]:
                files = open(root_path + '/files/' + i + '/' + j[0] + '/' + j[0] + '.meta', 'r')
                for line in files:
                    splittext = line.split(';')
                    all_params = True
                    for x in splitquery:
                        if not (x in splittext[0].lower() or x in splittext[1].lower() or x in splittext[3].lower() or x in splittext[4].lower() or x in (i + ' ' + j[0]).lower()):
                            all_params = False
                    if all_params:
                        search_list.append(Upload(splittext[0].strip(), splittext[1].strip(), splittext[2].strip(), splittext[3].strip(), splittext[4].strip(), splittext[5].strip(), splittext[6].strip() == cur_user).listify() + [i + ' ' + j[0]])
    except Exception as e:
        print('Failure: search_all', e)
        traceback.print_exc()
    os.chdir(root_path)
    return search_list

def process_file(conversion_image, istext, path):
    ps_image = conversion_image
    os.makedirs(path + conversion_image + '-images')
    if istext:
        ps_image = conversion_image + '.ps'
        os.system('enscript --word-wrap --no-header ' + path + conversion_image + ' -o ' + path + ps_image)
    os.system('convert -density 300 ' + path + ps_image + ' ' +  path + conversion_image + '-images/out.png')
    if ps_image != conversion_image:
        os.system('rm ' + path + ps_image)


def add_file(classname, file_to_save, file_name, upload_type, downloadable, quarter, year, cur_user):
    try:
        key, classnum = classname.split()
        path = root_path + '/files/' + key + '/' + classnum
        os.chdir(path)
        name, ext = ext_ract(file_name)
        encoded_file = base64.urlsafe_b64encode((name + str(time.time())).encode()).decode() + '.' + ext
        file_to_save.save(encoded_file)
        metafile = open(classnum + '.meta', 'a')
        metafile.write(file_name + ';' + upload_type + ';' + downloadable + ';' + quarter + ';' + year + ';' + path + '/' + encoded_file + ';' + cur_user + '\n')
        file_infer = from_file(encoded_file)
        process_t = Thread(target=process_file, args=(encoded_file, 'text' in file_infer, path + '/', ))
        process_t.start()
    except:
        print('Failure: add_file')
        traceback.print_exc()
    os.chdir(root_path)

def delete_file(classname, hashpath, cur_user):
    try:
        key, classnum = classname.split()
        os.chdir(root_path + '/files/'+ key + '/' + classnum)
        f = open(classnum + '.meta', 'r+')
        d = f.readlines()
        f.seek(0)
        for i in d:
            if hashpath not in i:
                f.write(i)
            elif cur_user in i:
                os.remove(hashpath)
                os.remove(hashpath + '.ps')
                shutil.rmtree(hashpath + '-images')
        f.truncate()
        f.close()
    except:
        print('Failure: delete_file')
        traceback.print_exc()
    os.chdir(root_path)

def update_active():
    global active
    try:
        os.chdir(root_path + '/files')
        for directory in classes:
            os.chdir(directory)
            empty = True
            for subdirectory in classes[directory]:
                if (len(os.listdir(subdirectory[0])) > 1):
                    empty = False
                    if directory not in active:
                        active[directory] = list()
                    if subdirectory not in active[directory]:
                        active[directory].append(subdirectory)
                elif directory in active and subdirectory in active[directory]:
                    print(subdirectory)
                    active[directory].remove(subdirectory)
            if empty and directory in active:
                del active[directory]
            os.chdir(root_path + '/files')
    except:
        print('Failure: update_active')
        traceback.print_exc()

    for i in active:
        active[i] = sorted(active[i], key=lambda item: int(item[0]))
    active = OrderedDict(sorted(active.items()))
    os.chdir(root_path)

def get_images(path):
    try:
        images = os.listdir(path)
        if (len(images) > 1):
            for i in range(len(images)):
                images[i] = 'out-' + str(i) + '.png'
        return [base64.b64encode(open(path + '/' + j, 'rb').read()).decode() for j in images]
    except:
        print('Failure: get_images')
        traceback.print_exc()
