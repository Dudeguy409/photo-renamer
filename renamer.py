import argparse
import os

photo_idx = 1
orig_names_to_mod_names = {}
delete_count = 0
renamed_count = 0

def recursive_add_mapping(curr_path, curr_name):
    for f in os.listdir(curr_path):
        new_path = curr_path+"/"+f
        if os.path.isfile(new_path):
            if new_path.endswith(".jpg") or new_path.endswith(".JPG") :
                global photo_idx
                global orig_names_to_mod_names
                filename = f.split(".")[0]
                new_name = curr_name + "_" + str(photo_idx)
                photo_idx += 1
                orig_names_to_mod_names[filename]= new_name
        else:
            recursive_add_mapping(new_path, curr_name+"_"+f)

def clean_up_raw_folder(raw_path):
    for f in os.listdir(raw_path):
        filename = f.split(".")[0]
        fileext = f.split(".")[1]
        mapping = orig_names_to_mod_names.get(filename)
        if mapping and mapping != "":
            #os.rename(raw_path + "/" + f, raw_path + "/" + mapping + "." + fileext)
            global renamed_count
            renamed_count += 1
            print("\033[1;37;40mrenamed " + raw_path + "/" + f + "  to  " + raw_path + "/" + mapping + "." + fileext)
        else:
            #os.remove(raw_path + "/" + f)
            global delete_count
            delete_count += 1
            print("\033[1;31;40mdeleted " + raw_path + "/" + f)

parser = argparse.ArgumentParser(description='Given the absolute path of a base directory containing images sorted into "raw" and "jpg" folders, renames the raw photos after the structure of subdirectories in jpg, deleting RAW files whose jpgs were deleted.')
parser.add_argument('directory', metavar='Dir', type=str, nargs=1,
                    help='absolute path of base photo directory.  Must contain raw and jpg subdirectories')

args = parser.parse_args()

base_dir = args.directory[0]
dir_names = base_dir.split("/")
base_dir_name = dir_names[-1]
if base_dir_name == '':
    base_dir_name = dir_names[-2]
recursive_add_mapping(base_dir+"/jpg", base_dir_name)
clean_up_raw_folder(base_dir+"/raw")
print("\033[1;36;40m" + str(renamed_count) + " files renamed and " + str(delete_count) + " deleted.")
