import argparse
import os
import pathlib


timestamps_to_names = {}
raw_names_found = {}
renamed_jpg_count = 0
unmatched_raw_count = 0
unmatched_jpg_count = 0
raw_total_count = 0
overlapping_jpg_timestamp = 0
overlapping_raw_timestamp = 0
directories_created = 0


def add_raw_timestamp_name_mappings(raw_path):
    global raw_total_count
    global timestamps_to_names
    global raw_names_found
    for f in os.listdir(raw_path):
        curr_file_path = raw_path + "/" + f
        if os.path.isfile(curr_file_path):
                raw_total_count += 1
                filename = f.split(".")[0]
                timestamp = os.path.getmtime(curr_file_path)
                print("\033[1;37;40m file to timestamp: " + filename + " : " + str(timestamp))
                mapping = timestamps_to_names.get(timestamp)
                if mapping:
                    print("\033[1;37;40m found mapping: " + str(mapping))
                    timestamps_to_names[timestamp] = mapping + [filename]
                    print("\033[1;37;40m finished updating mapping: " + str(timestamps_to_names.get(timestamp)))
                else:
                    timestamps_to_names[timestamp]= [filename]
                    raw_names_found[filename] = False
        else:
            print("\033[1;37;40mfound a directory in the raw folder: " + curr_file_path)
    global overlapping_raw_timestamp
    global directories_created
    for timestamp, names in timestamps_to_names.items():
        if len(names) > 1:
            print("\033[1;37;40mfound overlapping raw timestamps: " + str(names) + " : " + str(timestamp))
            new_dir = raw_path+"/"+str(timestamp)+"/"
            directories_created += 1
            if args.force:
                os.makedirs(new_dir)
            print("\033[1;37;40mmade timestamp dir: " + str(timestamp))
            for name in names :
                old_loc = raw_path+"/"+name+".RW2"
                new_loc = raw_path+"/"+str(timestamp)+"/"+name+".RW2"
                if args.force:
                    os.rename(old_loc, new_loc)
                overlapping_raw_timestamp += 1
                raw_names_found[name] = True
                print("\033[1;37;40m renamed  " + old_loc + " to " + new_loc)

def recursive_rename_jpgs(curr_path, raw_path):
    global overlapping_jpg_timestamp
    for f in os.listdir(curr_path):
        old_path = curr_path + "/" + f
        if os.path.isfile(old_path):
            if old_path.endswith(".jpg") or old_path.endswith(".JPG") :
                file_ext = f.split(".")[1]
                timestamp = os.path.getmtime(old_path)
                global timestamps_to_names
                mapping = timestamps_to_names.get(timestamp)
                if mapping :
                    if len(mapping) > 1:
                        new_path = raw_path + "/" + str(timestamp) + "/" + f
                        if args.force:
                            os.rename(old_path, new_path)
                        overlapping_jpg_timestamp += 1
                        print("\033[1;37;40m moved to jpg with overlapping raw " + old_path + " to " + new_path)
                    else:
                        global raw_names_found
                        if raw_names_found.get(mapping[0]) != False :
                            overlapping_jpg_timestamp += 1
                            print("\033[1;37;40mfound double dipped file:  " + old_path + " and " + mapping[0])
                        else:
                            new_path = curr_path + "/" + str(mapping[0]) + "." +file_ext
                            if args.force:
                                os.rename(old_path, new_path)
                            global renamed_jpg_count
                            renamed_jpg_count += 1
                            raw_names_found[mapping[0]] = True
                            print("\033[1;37;40mrenamed " + old_path + " to " + new_path)
                else:
                    global unmatched_jpg_count
                    unmatched_jpg_count += 1
                    print("\033[1;37;40munable to find a match for " + old_path)
        else:
            recursive_rename_jpgs(old_path, raw_path)

def print_unmatched_raws():
    global raw_names_found
    global unmatched_raw_count
    for name, found in raw_names_found.items():
        if not found:
            unmatched_raw_count += 1
            print("\033[1;37;40munmatched raw file: " + name)

parser = argparse.ArgumentParser(description='Given the absolute path of a base directory containing images sorted into "raw" and "unprocessed" folders where raw photos are renamed and unprocessed photos arent, renames the unprocessed photos after the raw photos based on matching timestamps.')
parser.add_argument('directory', metavar='Dir', type=str, nargs=1,
                    help='absolute path of base photo directory.  Must contain raw and unprocessed subdirectories')
parser.add_argument("-f", "--force", help="enables changes to be written.  Defaults to false for preview mode. Cannot be undone",
                    action="store_true")

args = parser.parse_args()

if args.force:
    print("Force flag detected. Changes will be made.")
else:
    print("The force flag was not set using '-f', so no changes will be made.  Preview mode.")

base_dir = args.directory[0]
dir_names = base_dir.split("/")
base_dir_name = dir_names[-1]
if base_dir_name == '':
    base_dir_name = dir_names[-2]
unprocessed_dir = base_dir + "/unprocessed"
raw_dir = base_dir + "/raw"
add_raw_timestamp_name_mappings(raw_dir)
recursive_rename_jpgs(unprocessed_dir, raw_dir)
print_unmatched_raws()

print("\033[1;36;40m" + str(renamed_jpg_count) + " jpg files renamed\n" + str(unmatched_raw_count) + " raw files unmatched\n" + str(unmatched_jpg_count) + " jpg files unmatched\n" + str(raw_total_count) + " total raw files\n" + str(overlapping_jpg_timestamp) + " overlapping jpgs\n" + str(overlapping_raw_timestamp) + "overlapping raws\n"+ str(directories_created) + "directories created\n")

if args.force:
    print("Force flag detected. Changes were made.")
else:
    print("The force flag was not set using '-f', so no changes were made.  Preview mode.")
