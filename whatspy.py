import re
import mmap
import csv
from tqdm import tqdm
from typing import Dict, Tuple, List

def _check_integrity(record):
    pattern = r"^[0-9]{2}/[0-9]{2}/[0-9]{2}, [0-9]{2}:[0-9]{2} \- .*?:"
    match = re.match(pattern, record)
    if match is None:
        return None
    return re.match(pattern, record).group(0)

def _get_text(record):
    pattern = r"^[0-9]{2}/[0-9]{2}/[0-9]{2}, [0-9]{2}:[0-9]{2} \- .*?:"
    _, text = re.split(pattern, record)
    return text.strip()


def _get_num_lines(file_path):
    """
    Taken from https://blog.nelsonliu.me/2016/07/30/progress-bars-for-python-file-reading-with-tqdm/
    """
    fp = open(file_path, "r+")
    buf = mmap.mmap(fp.fileno(), 0)
    lines = 0
    while buf.readline():
        lines += 1
    return lines

def _get_progressbar(file_iterator, file_path, verbosity: bool = False):
    if verbosity:
        return tqdm(file_iterator, total=_get_num_lines(file_path))
    return file_iterator

def _process_string(date_name, text):
    date_time, name = date_name.split(" - ")
    date_time = date_time.strip().replace(", ", "-")
    name = name[:-1].strip()
    return date_time, name, text

def wapp_parsing(file_to_parse: str,
                 file_to_read: str = "chat_whatsapp.csv",
                 verbose: bool = True) -> None:

    with open(file_to_parse) as wa_file, open(file_to_read, "w") as wa_csv:
        writer =  csv.writer(wa_csv, delimiter='\t')
        writer.writerow(["datetime", "from", "text"])
        prev = str()
        #for line in wa_file:
        for line in _get_progressbar(wa_file, file_to_parse, verbose):
            date_name = _check_integrity(line)
            if date_name is not None:
                prev = date_name
                text = _get_text(line)
                writer.writerow(_process_string(prev, text))
            else:
                writer.writerow(_process_string(prev, line))

if __name__ == "__main__":
    wapp_parsing("ChatWhatsApp.txt")
