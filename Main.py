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
        evaluateRegexName(filename)


def evaluateRegexName(filename):
    if re.match(r"\d{8}_\d{4}\d*\..+", filename) or re.match(r"\d{8}_WA\d+\..+", filename):  # accepted filenames
        renameFile(filename, filename, metaCheck=True)  # check for new metaData
    elif re.match(r".*?\d{8}.\d{4}\d+.*(\..+)$", filename):  # searches for date and time
        regex = re.search(r"(\d{8}).(\d{4}\d+).*(\..+)$", filename)
        newfilename = f"{regex.group(1)}_{regex.group(2)}{regex.group(3)}"
        renameFile(filename, newfilename)
    elif re.match(r".*?\d{8}.WA\d+.*\..+$", filename):  # searches for date and WA index
        newfilename = filenameFromMetaDate(filename)
        renameFile(filename, newfilename)
    elif re.match(r"signal-\d{4}-\d{2}-\d{2}-\d+.*\..+$", filename):  # signal files
        newfilename = filename.replace("-", "")
        regex = re.search(r"signal(\d{8})(\d+)(\..+)$", newfilename)
        newfilename = f"{regex.group(1)}_{regex.group(2)}{regex.group(3)}"
        renameFile(filename, newfilename)
    elif re.match(r"WhatsApp \w+ \d{4}-\d{2}-\d{2} at \d{2}\.\d{2}\.\d{2}.*\..+$", filename):  # whatsapp files
        newfilename = filename.replace("-", "")
        regex = re.search(r"WhatsApp \w+ (\d{8}) at (\d{2})\.(\d{2})\.(\d{2}).*(\..+)$", newfilename)
        newfilename = f"{regex.group(1)}_{regex.group(2)}{regex.group(3)}{regex.group(4)}{regex.group(5)}"
        renameFile(filename, newfilename)
    elif re.match(r"snapchat.*\..+$", filename.lower()):
        newfilename = filenameFromMetaDate(filename)
        renameFile(filename, newfilename)
    elif re.match(r"^\d+$", filename.split(".")[0]):
        unixstamp = filename.split(".")[0]
        unixstamp = int(unixstamp) / (pow(10, len(unixstamp) - 10) if len(unixstamp) > 10 else 1)
        newfilename = datetime.fromtimestamp(unixstamp).strftime('%Y%m%d_%H%M%S')
        renameFile(filename, re.sub(r"\d+", newfilename, filename))
    else:
        print(f"\033[91mNo rule found for:\033[0m {filename}")


def renameFile(old, new, metaCheck=True):  # also treats edge cases
    if not re.match(r"\d{8}.*\.[a-zA-Z0-9_]+$", new):
        print(f"\033[91m{new} is not a valid filename!")
        return
    new = checkMetaDateFilename(old, new) if metaCheck else new
    if old == new:
        return
    try:
        os.rename(os.path.join(folder, old), os.path.join(folder, new))
    except FileExistsError:
        time = int(re.search(r"(\d+)\..*?$", new).group(
            1))  # gets the lastDigit of the new filename in front of the file extension
        dataExtension = re.search(r".*(\..+)$", new).group(1)
        new = re.sub(r"\d+(\..*?)$", f"{str(time + 1)}{dataExtension}", new)
        renameFile(old, new, False)


def filenameFromMetaDate(filename):
    assert re.match(r".*\..+$", filename)
    dataExtension = re.search(r".*(\..+)$", filename).group(1)
    metadata = os.stat(os.path.join(folder, filename))
    minTime = min(metadata.st_ctime, metadata.st_mtime, metadata.st_atime)
    return strftime('%Y%m%d_%H%M%S', localtime(minTime)) + dataExtension


def checkMetaDateFilename(file, otherFilename):  # function computes the filename from metadata, compares it to the
    # alternative filename otherFilename and returns the more suitable one.
    metaDateFilename = filenameFromMetaDate(file)
    return metaDateFilename if metaDateFilename < otherFilename else otherFilename


if __name__ == '__main__':
    main()
