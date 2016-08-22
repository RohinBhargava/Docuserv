from collections import OrderedDict
from werkzeug.utils import secure_filename
from class_list import classes
import os, shutil, class_list, sys, bitmath, subprocess

active = OrderedDict()

root_path = os.getcwd()

class Upload:
    def __init__(self, file_name, upload_type, downloadable, quarter, year):
        self.file_name, self.file_ext = os.path.splitext(file_name)
        self.upload_type = upload_type
        self.size = bitmath.Byte(bytes=os.path.getsize(secure_filename(file_name))).best_prefix().format("{value:.2f} {unit}")
        self.downloadable = downloadable
        self.quarter = quarter
        self.year = year
    def listify(self):
        # return {"File name" : self.file_name,
        #         "Extension" : self.file_ext,
        #         "Upload type" : self.upload_type,
        #         "Size" : self.size,
        #         "Downloadable" : self.downloadable,
        #         "Quarter" : self.quarter,
        #         "Year" : self.year}
        return [self.file_name, self.file_ext,  self.quarter, self.year, self.downloadable, self.size, self.upload_type]

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
                file_list.append(Upload(splittext[0].strip(), splittext[1].strip(), splittext[2].strip(), splittext[3].strip(), splittext[4].strip()).listify())
    except Exception as e:
        print('Failure: cd ' + root_path, e)
    os.chdir(root_path)
    return file_list

def add_file(classname, file_to_save, file_name, upload_type, downloadable, quarter, year):
    key, classnum = classname.split()
    try:
        os.chdir('files/'+ key + '/' + classnum)
        file_to_save.save(secure_filename(file_name))
        metafile = open(classnum + '.meta', 'a')
        metafile.write(file_name + ';' + upload_type + ';' + downloadable + ';' + quarter + ';' + year + '\n')
        file_infer = str(subprocess.check_output(['file', '-b', secure_filename(file_name)]))
        conversion_image = secure_filename(file_name)
        ps_image = conversion_image
        if 'text' in file_infer:
            ps_image = secure_filename(file_name) + '.ps'
            subprocess.call(['enscript', '--word-wrap', '--no-header', conversion_image, '-o', ps_image])
        subprocess.call(['convert', '-density', '300', ps_image,  conversion_image + '.png'])
        if ps_image != conversion_image:
            subprocess.call(['rm', ps_image])
    except:
        print(sys.exc_info()[0])
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
