import glob
import os
import hashlib
import pathlib
import json

ROOT = pathlib.Path(r'G:\Backup\Minecraft\5 Folders')
ROOT_DEPTH = len(ROOT.parts)
BLOCKSIZE = 65536


def main():
    folders = [pathlib.Path(folder) for folder in glob.glob(os.path.join(ROOT, '**'), recursive=True) if os.path.isdir(folder)]
    folders.remove(ROOT)

    hashed_folders = dict()
    while len(folders) > 0:
        for folder in folders:
            # Check if folder contains a unhashed folder
            contains_unhashed_folders = False
            for child in folder.iterdir():
                if child.is_dir() and str(child) not in hashed_folders:
                    contains_unhashed_folders = True
                    break

            if not contains_unhashed_folders:
                # Hash the folder contents
                child_file_hashes = list()
                for child in folder.iterdir():
                    if child.is_file():
                        file_hash = hashlib.md5()
                        with open(str(child), mode='rb') as f:
                            buffer = f.read(BLOCKSIZE)
                            while len(buffer) > 0:
                                file_hash.update(buffer)
                                buffer = f.read(BLOCKSIZE)
                        child_file_hashes.append(file_hash.hexdigest())
                    else:
                        child_file_hashes.append(hashed_folders[str(child)])


                # Sort list of hashes for consistancy
                child_file_hashes.sort()

                # Hash hashes
                hash_of_hashes = hashlib.md5()
                for computed_hash in child_file_hashes:
                    hash_of_hashes.update(computed_hash.encode('utf_8'))

                # Add hash of folder to hashed_folders
                hashed_folders[str(folder)] = hash_of_hashes.hexdigest()
                # Remove newly hashed folders from folders
                folders.remove(folder)

    rev_multidict = {}
    for key, value in hashed_folders.items():
        rev_multidict.setdefault(value, list()).append(key)

    # Remove listings that have a single match
    new_data = dict()
    for key in rev_multidict.keys():
        if len(rev_multidict[key]) > 1:
            new_data[key] = rev_multidict[key]

    json.dump(new_data, open('output.json', mode='w'), indent=4)


if __name__ == '__main__':
    main()
