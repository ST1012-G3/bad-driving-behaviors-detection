import os
import shutil
import zipfile

set_type = 'val'
img_home_dir = f'E:\\dataset\\bdd100k\\bdd100k\\images\\track\\{set_type}\\'
label_dir = f'E:\\dataset\\bdd100k\\bdd100k\\labels\\box_track_20\\{set_type}\\'
output_dir = f'E:\\dataset\\bdd100k\\coco\\{set_type}\\'


def load_dir(img_home_dir, label_dir):
    label_dirs = []
    for dirname, _, filenames in os.walk(label_dir):
        for filename in filenames:
            label_dirs.append(filename.strip('.json'))

    img_dirs = []
    for dirname, _, filenames in os.walk(img_home_dir):
        img_dirs.append(dirname.split('\\')[-1])

    available_dirs = []
    for dir in label_dirs:
        if dir in img_dirs:
            available_dirs.append(dir)
    available_dirs.sort()

    return available_dirs


def mkdir(path):
    try:
        os.mkdir(path)
    except FileExistsError:
        pass


def convert(img_home_dir, label_dir, output_dir, start=0, end=-1):
    available_dirs = load_dir(img_home_dir, label_dir)
    print(f'[+]{len(available_dirs)} dirs available')

    # Loop over all image folders in available dirs
    for i, dir in enumerate(available_dirs[:end]):
        if i < start:
            continue
        print(f'\n[+]Converting {dir} ({i+1}/{len(available_dirs)})...')
        image_dir = os.path.join(img_home_dir, dir)
        label_path = os.path.join(label_dir, f'{dir}.json')
        output_folder_dir = os.path.join(output_dir, dir)
        temp_label_path = os.path.join(
            output_folder_dir, 'Annotations', f'{dir}.json')

        # Make dirs
        mkdir(output_dir)
        mkdir(output_folder_dir)
        mkdir(os.path.join(output_folder_dir, 'Annotations'))

        # Copy images
        try:
            shutil.copytree(image_dir, os.path.join(
                output_folder_dir, 'Images'))
        except FileExistsError:
            pass

        # Convert bdd to coco
        os.system(f'python -m bdd100k.label.to_coco \
                    -m box_track -i {label_path} -o {temp_label_path}')

        # Trim .json
        with open(temp_label_path, 'r') as temp:
            with open(os.path.join(output_folder_dir, 'Annotations', 'coco_info.json'), 'w') as label_file:
                label_file.write(temp.readline().replace(f'{dir}\\\\', ''))

        # Remove temp label file
        os.remove(temp_label_path)

        # Zip Images and Annotations folders
        zip_file = output_folder_dir + '.zip'
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zip:
            for dirname, _, filenames in os.walk(output_folder_dir):
                filepath = dirname.replace(output_folder_dir, '')
                for filename in filenames:
                    zip.write(os.path.join(dirname, filename),
                              os.path.join(filepath, filename))

        # Remove unzipped folders
        shutil.rmtree(output_folder_dir)


if __name__ == '__main__':
    convert(img_home_dir, label_dir, output_dir)
