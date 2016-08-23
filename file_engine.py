from collections import OrderedDict
from werkzeug.utils import secure_filename
from class_list import classes
from threading import Thread
from magic import from_file
import os, shutil, class_list, sys, bitmath, subprocess, base64, time

active = OrderedDict()

root_path = os.getcwd()

class Upload:
    def __init__(self, file_name, upload_type, downloadable, quarter, year, hashpath):
        self.file_name, self.file_ext = ext_ract(file_name)
        self.upload_type = upload_type
        self.size = bitmath.Byte(bytes=os.path.getsize(hashpath)).best_prefix().format("{value:.2f} {unit}")
        self.downloadable = downloadable
        self.quarter = quarter
        self.year = year
        self.hashpath = hashpath
    def listify(self):
        # return {"File name" : self.file_name,
        #         "Extension" : self.file_ext,
        #         "Upload type" : self.upload_type,
        #         "Size" : self.size,
        #         "Downloadable" : self.downloadable,
        #         "Quarter" : self.quarter,
        #         "Year" : self.year}
        return [self.file_name, self.file_ext,  self.quarter, self.year, self.downloadable, self.size, self.upload_type, self.hashpath]

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
        os.chdir('files')
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
        print('Failure: cd ' + root_path)
    os.chdir(root_path)

def rm_dirs():
    try:
        os.chdir('files')
        for directory in classes:
            if os.path.exists(directory):
                shutil.rmtree(directory)
    except:
        print('Failure: cd ' + root_path)
    os.chdir(root_path)

def check_whitelist(key, classnum):
    if key in classes and classnum in [keys[0] for keys in classes[key]]:
        return True
    return False

def file_list(key, classnum):
    file_list = list()
    try:
        if check_whitelist(key, classnum):
            os.chdir('files/'+ key + '/' + classnum)
            metafile = open(classnum + '.meta', 'r')
            for i in metafile:
                splittext = i.split(';')
                file_list.append(Upload(splittext[0].strip(), splittext[1].strip(), splittext[2].strip(), splittext[3].strip(), splittext[4].strip(), splittext[5].strip()).listify())
    except Exception as e:
        print('Failure: cd ' + root_path, e)
    os.chdir(root_path)
    return file_list

def process_file(conversion_image, istext, path):
    ps_image = conversion_image
    os.makedirs(path + conversion_image + '-images')
    if istext:
        ps_image = conversion_image + '.ps'
        os.system('enscript --word-wrap --no-header ' + path + conversion_image + ' -o ' + path + ps_image)
    os.system('convert -density 300 ' + path + ps_image + ' ' +  path + conversion_image + '-images/out.png')
    if ps_image != conversion_image:
        os.system('rm ' + path + ps_image)


def add_file(classname, file_to_save, file_name, upload_type, downloadable, quarter, year):
    try:
        key, classnum = classname.split()
        os.chdir('files/'+ key + '/' + classnum)
        name, ext = ext_ract(file_name)
        encoded_file = base64.urlsafe_b64encode((name + str(time.time())).encode()).decode() + '.' + ext
        file_to_save.save(encoded_file)
        path = os.getcwd() + '/'
        metafile = open(classnum + '.meta', 'a')
        metafile.write(file_name + ';' + upload_type + ';' + downloadable + ';' + quarter + ';' + year + ';' + path + encoded_file + '\n')
        file_infer = from_file(encoded_file)
        process_t = Thread(target=process_file, args=(encoded_file, 'text' in file_infer, path, ))
        process_t.start()
    except Exception as e:
        print(sys.exc_info()[0], e)
    os.chdir(root_path)

def update_active():
    global active
    try:
        os.chdir(root_path + '/files')
        for directory in classes:
            os.chdir(directory)
            for subdirectory in classes[directory]:
                if len(os.listdir(subdirectory[0])) > 1:
                    if directory not in active:
                        active[directory] = list()
                    if subdirectory not in active[directory]:
                        active[directory].append(subdirectory)
            os.chdir(root_path + '/files')
    except Exception as e:
        print('Failure: cd ' + root_path, e)

    for i in active:
        active[i] = sorted(active[i], key=lambda item: int(item[0]))
    active = OrderedDict(sorted(active.items()))
    os.chdir(root_path)

def get_images(path):
    images = os.listdir(path)
    if (len(images) > 1):
        for i in range(len(images)):
            images[i] = 'out-' + str(i) + '.png'
    return [base64.b64encode(open(path + '/' + j, 'rb').read()).decode() for j in images]
