import os
import re
from datetime import datetime
from time import strftime, localtime
from tkinter import filedialog

folder = ""


def main():
    getFolder()
    filenames = os.listdir(folder)
    renameFiles(filenames)


def getFolder():
    global folder
    folder = filedialog.askdirectory()


def renameFiles(filenames):
    for filename in filenames:
        try:
            formatedName = formatFilename(filename)
            if formatedName is None:
                continue
            nameEpoch = formatNameToEpoch(formatedName)
            metaName = filenameFromMetaDate(filename)
            metaEpoch = formatNameToEpoch(metaName)
            renameFile(filename, (formatedName, nameEpoch), (metaName, metaEpoch))
        except RuntimeWarning as e:
            print(e)


def formatNameToEpoch(filename):
    assert re.match(r"\d{8}_\d{6}\d*\..+$", filename)
    time = None
    try:
        time = datetime.strptime(filename.split(".")[0][:15], "%Y%m%d_%H%M%S").timestamp()
    except ValueError:
        time = datetime.strptime(filename.split(".")[0][:8], "%Y%m%d").timestamp()
    return int(time)


def formatFilename(filename):
    if re.match(r"\d{8}_\d{4}\d*\..+$", filename):  # accepted filenames
        return filename
    elif re.match(r"\d{8}_WA\d+\..+", filename):
        regex = re.search(r"(\d{8})_WA\d+(\..+)$", filename)
        return f"{regex.group(1)}_000000{regex.group(2)}"
    elif re.match(r".*?\d{8}.\d{4}\d+.*?(\..+)$", filename):  # searches for date and time
        regex = re.search(r"(\d{8}).(\d{4}\d+).*?(\..+)$", filename)
        return f"{regex.group(1)}_{regex.group(2)}{regex.group(3)}"
    elif re.match(r".*?\d{8}.WA\d+.*?\..+$", filename):  # searches for date and WA index
        return filenameFromMetaDate(filename)
    elif re.match(r"signal-\d{4}-\d{2}-\d{2}-\d+.*?\..+$", filename):  # signal files
        newfilename = filename.replace("-", "")
        regex = re.search(r"signal(\d{8})(\d+)(\..+)$", newfilename)
        return f"{regex.group(1)}_{regex.group(2)}{regex.group(3)}"
    elif re.match(r"WhatsApp \w+ \d{4}-\d{2}-\d{2} at \d{2}\.\d{2}\.\d{2}.*?\..+$", filename):  # whatsapp files
        newfilename = filename.replace("-", "")
        regex = re.search(r"WhatsApp \w+ (\d{8}) at (\d{2})\.(\d{2})\.(\d{2}).*?(\..+)$", newfilename)
        return f"{regex.group(1)}_{regex.group(2)}{regex.group(3)}{regex.group(4)}{regex.group(5)}"
    elif re.match(r"snapchat.*?\..+$", filename.lower()):
        return filenameFromMetaDate(filename)
    elif re.match(r"^\d+\.", filename.split(".")[0]):
        unixstamp = filename.split(".")[0]
        unixstamp = int(unixstamp) / (pow(10, len(unixstamp) - 10) if len(unixstamp) > 10 else 1)
        newfilename = datetime.fromtimestamp(unixstamp).strftime('%Y%m%d_%H%M%S')
        return re.sub(r"\d+", newfilename, filename)
    else:
        print(f"\033[91mNo rule found for:\033[0m {filename}")


def renameFile(filename, nameData, metaData):  # also treats edge cases
    if not re.match(r"\d{8}.*\.[a-zA-Z0-9_]+$", nameData[0]):
        print(f"\033[91m{nameData[0]} is not a valid filename!")
        return
    if not re.match(r"\d{8}.*\.[a-zA-Z0-9_]+$", metaData[0]):
        print(f"\033[91m{nameData[0]} is not a valid filename!")
        return

    new = nameData if nameData[1] <= metaData[1] else metaData
    currentMeta = os.stat(os.path.join(folder, filename))
    if filename == new[0] and currentMeta.st_mtime == new[1] and currentMeta.st_atime == new[1]:
        return
    try:
        os.rename(os.path.join(folder, filename), os.path.join(folder, new[0]))
        os.utime(os.path.join(folder, new[0]), (new[1], new[1]))
    except FileExistsError:
        dataExtension = re.search(r".*(\..+)$", new[0]).group(1)
        new = (f"{datetime.fromtimestamp(new[1] + 1).strftime('%Y%m%d_%H%M%S')}.{dataExtension}", new[1] + 1)
        renameFile(filename, new, new)


def filenameFromMetaDate(filename):
    assert re.match(r".*\..+$", filename)
    dataExtension = re.search(r"^[^.]+?(\..+)$", filename).group(1)
    metadata = os.stat(os.path.join(folder, filename))
    creation_time = None
    try:
        creation_time = metadata.st_birthtime
    except AttributeError:
        creation_time = metadata.st_ctime
    return strftime('%Y%m%d_%H%M%S', localtime(creation_time)) + dataExtension


if __name__ == '__main__':
    main()
