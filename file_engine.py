from collections import OrderedDict
from werkzeug.utils import secure_filename
from class_list import classes
from threading import Thread
from magic import from_file
import os, shutil, class_list, sys, bitmath, subprocess, base64, time, traceback

active = OrderedDict()

root_path = '/var/docuserv'

f_e_log = open(root_path + '/file_engine.log', 'a')

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
    f_e_log.write('[' + time.strftime("%Y-%m-%d %H:%M:%S") + '] Initiated: setup_dirs ')
    try:
        for directory in classes:
            if not os.path.exists(root_path + '/files/' + directory):
                os.makedirs(root_path + '/files/' + directory)
            for subdir in classes[directory]:
                if not os.path.exists(root_path + '/files/' + directory + '/' + subdir[0]):
                    os.makedirs(root_path + '/files/' + directory + '/' + subdir[0])
                    open(root_path + '/files/' + directory + '/' + subdir[0] + '/' + subdir[0] + '.meta', 'a')
                    os.makedirs(root_path + '/files/' + directory + '/' + subdir[0] + '/logs')
    except:
        f_e_log.write('\nFailure: setup_dirs')
        traceback.print_exc(file=f_e_log)
    f_e_log.write('\n')
    f_e_log.flush()
    os.chdir(root_path)

def rm_dirs():
    f_e_log.write('[' + time.strftime("%Y-%m-%d %H:%M:%S") + '] Initiated: rm_dirs ')
    try:
        for directory in classes:
            if os.path.exists(root_path + '/files/' + directory):
                shutil.rmtree(root_path + '/files/' + directory)
    except:
        f_e_log.write('\nFailure: rm_dirs')
        traceback.print_exc(file=f_e_log)
    f_e_log.write('\n')
    f_e_log.flush()
    os.chdir(root_path)

def log_cleanup():
    f_e_log.write('[' + time.strftime("%Y-%m-%d %H:%M:%S") + '] Initiated: log_cleanup ')
    try:
        for directory in classes:
            for subdir in classes[directory]:
                for i in os.listdir(root_path + '/files/' + directory + '/' + subdir[0] + '/logs'):
                    if i != 'logs' and i != '':
                        if not os.path.exists(root_path + '/files/' + directory + '/' + subdir[0] + '/' + i[:-4]):
                            os.remove(root_path + '/files/' + directory + '/' + subdir[0] + '/logs/' + i)
    except:
        f_e_log.write('\nFailure: log_cleanup')
        traceback.print_exc(file=f_e_log)
    f_e_log.write('\n')
    f_e_log.flush()
    os.chdir(root_path)

def check_whitelist(key, classnum):
    if key in classes and classnum in [keys[0] for keys in classes[key]]:
        return True
    return False

def file_list(key, classnum, cur_user):
    f_e_log.write('[' + time.strftime("%Y-%m-%d %H:%M:%S") + '] Initiated: file_list ' + ' '.join([key, classnum, cur_user]))
    file_list = list()
    try:
        if check_whitelist(key, classnum):
            os.chdir('files/'+ key + '/' + classnum)
            metafile = open(classnum + '.meta', 'r')
            for i in metafile:
                splittext = i.split(';')
                file_list.append(Upload(splittext[0].strip(), splittext[1].strip(), splittext[2].strip(), splittext[3].strip(), splittext[4].strip(), splittext[5].strip(), splittext[6].strip() == cur_user).listify())
    except:
        f_e_log.write('\nFailure: file_list')
        traceback.print_exc(file=f_e_log)
    f_e_log.write('\n')
    f_e_log.flush()
    os.chdir(root_path)
    return file_list

def search_all(query, cur_user):
    search_list = list()
    f_e_log.write('[' + time.strftime("%Y-%m-%d %H:%M:%S") + '] Initiated: search_all ' + ' '.join([query, cur_user]) )
    splitquery = query.lower().split()
    try:
        for i in classes:
            for j in classes[i]:
                files = open(root_path + '/files/' + i + '/' + j[0] + '/' + j[0] + '.meta', 'r')
                for line in files:
                    splittext = line.split(';')
                    sort_score = 0
                    for x in splitquery:
                        if x in splittext[0].lower():
                            sort_score += 5
                        if x in splittext[1].lower():
                            sort_score += 1
                        if x in splittext[3].lower():
                            sort_score += 1
                        if x in splittext[4].lower():
                            sort_score += 1
                        if x in (i + ' ' + j[0]).lower():
                            sort_score += 4
                    if sort_score > 0:
                        search_list.append((Upload(splittext[0].strip(), splittext[1].strip(), splittext[2].strip(), splittext[3].strip(), splittext[4].strip(), splittext[5].strip(), splittext[6].strip() == cur_user).listify() + [i + ' ' + j[0]], sort_score))
    except Exception as e:
        f_e_log.write('\nFailure: search_all', e)
        traceback.print_exc(file=f_e_log)
    f_e_log.write('\n')
    f_e_log.flush()
    os.chdir(root_path)
    return [i[0] for i in sorted(search_list, key=lambda item: int(item[1]))]

def process_file(conversion_image, istext, path):
    ps_image = conversion_image
    recLimit = 0
    os.makedirs(path + conversion_image + '-images')
    if istext:
        ps_image = conversion_image + '.ps'
        a = 1
        while (a != 0):
            a = os.system('enscript --word-wrap --no-header ' + path + conversion_image + ' -o ' + path + ps_image + ' >> ' + path + 'logs/' + conversion_image + '.log 2>&1')
    a = 1
    while (a != 0 and recLimit < 3):
        a = os.system('convert -density 300 ' + path + ps_image + ' ' +  path + conversion_image + '-images/out.png' + ' >> ' + path + 'logs/' + conversion_image + '.log 2>&1')
        recLimit += 1
    if ps_image != conversion_image:
        os.system('rm ' + path + ps_image)


def add_file(classname, file_to_save, file_name, upload_type, downloadable, quarter, year, cur_user):
    f_e_log.write('[' + time.strftime("%Y-%m-%d %H:%M:%S") + '] Initiated: add_file ' + ' '.join([classname, file_name, upload_type, downloadable, quarter, year, cur_user]))
    try:
        key, classnum = classname.split()
        path = root_path + '/files/' + key + '/' + classnum
        name, ext = ext_ract(file_name)
        encoded_file = base64.urlsafe_b64encode((name + str(time.time())).encode()).decode() + '.' + ext
        file_to_save.save(path + '/' + encoded_file)
        metafile = open(path + '/' + classnum + '.meta', 'a')
        metafile.write(file_name + ';' + upload_type + ';' + downloadable + ';' + quarter + ';' + year + ';' + path + '/' + encoded_file + ';' + cur_user + '\n')
        file_infer = from_file(path + '/' + encoded_file)
        process_t = Thread(target=process_file, args=(encoded_file, 'text' in file_infer, path + '/', ))
        process_t.start()
    except:
        f_e_log.write('\nFailure: add_file')
        traceback.print_exc(file=f_e_log)
    f_e_log.write('\n')
    f_e_log.flush()
    os.chdir(root_path)

def delete_file(classname, hashpath, cur_user):
    f_e_log.write('[' + time.strftime("%Y-%m-%d %H:%M:%S") + '] Initiated: delete_file ' + ' '.join([classname, hashpath, cur_user]))
    try:
        key, classnum = classname.split()
        f = open(root_path + '/files/'+ key + '/' + classnum + '/' + classnum + '.meta', 'r+')
        d = f.readlines()
        f.seek(0)
        for i in d:
            if hashpath not in i:
                f.write(i)
            elif cur_user in i:
                os.remove(hashpath)
                if os.path.exists(hashpath + '.ps'):
                    os.remove(hashpath + '.ps')
                shutil.rmtree(hashpath + '-images')
        f.truncate()
        f.close()
    except:
        f_e_log.write('\nFailure: delete_file')
        traceback.print_exc(file=f_e_log)
    f_e_log.write('\n')
    f_e_log.flush()
    os.chdir(root_path)

def update_active():
    f_e_log.write('[' + time.strftime("%Y-%m-%d %H:%M:%S") + '] Initiated: update_active ')
    global active
    try:
        for directory in classes:
            empty = True
            for subdirectory in classes[directory]:
                if (len(os.listdir(root_path + '/files/' + directory + '/' + subdirectory[0])) > 2):
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
    except:
        f_e_log.write('\nFailure: update_active')
        traceback.print_exc(file=f_e_log)

    for i in active:
        active[i] = sorted(active[i], key=lambda item: int(item[0]))
    active = OrderedDict(sorted(active.items()))
    f_e_log.write('\n')
    f_e_log.flush()
    os.chdir(root_path)

def get_images(path):
    f_e_log.write('[' + time.strftime("%Y-%m-%d %H:%M:%S") + '] Initiated: get_images ' + path)
    returner = ''
    try:
        images = os.listdir(path)
        if (len(images) > 1):
            for i in range(len(images)):
                images[i] = 'out-' + str(i) + '.png'
        returner =  [base64.b64encode(open(path + '/' + j, 'rb').read()).decode() for j in images]
    except:
        f_e_log.write('\nFailure: get_images')
        traceback.print_exc(file=f_e_log)
    f_e_log.write('\n')
    f_e_log.flush()
    os.chdir(root_path)
    return returner
