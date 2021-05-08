import csv
import json
import mmap
import re

from tqdm import tqdm
from typing import Optional, Tuple, Iterable


def _check_integrity(record: str) -> Optional[str]:
    """

    Parameters
    ----------
    record :

    Returns
    -------

    """
    pattern = r"^[0-9]{2}/[0-9]{2}/[0-9]{2}, [0-9]{2}:[0-9]{2} \- .*?:"
    match = re.match(pattern, record)
    if match is None:
        return None
    return re.match(pattern, record).group(0)


def _get_text(record: str) -> str:
    """

    Parameters
    ----------
    record :

    Returns
    -------

    """
    pattern = r"^[0-9]{2}/[0-9]{2}/[0-9]{2}, [0-9]{2}:[0-9]{2} \- .*?:"
    _, text = re.split(pattern, record)
    return text.strip()


def _get_num_lines(file_path: str) -> int:
    """
    Taken from https://blog.nelsonliu.me/2016/07/30/progress-bars-for-python-file-reading-with-tqdm/

    Parameters
    ----------
    file_path :

    Returns
    -------
    int
    """
    with open(file_path, "r+") as fp:
        buf = mmap.mmap(fp.fileno(), 0)
        lines = 0
        while buf.readline():
            lines += 1
    return lines


def _get_progressbar(file_iterator: Iterable[str],
                     file_path: str,
                     verbosity: bool = False) -> object:
    if verbosity:
        return tqdm(file_iterator, total=_get_num_lines(file_path))
    return file_iterator


def _process_string(date_name: str,
                    text: str) -> Tuple[str, str, str]:
    """

    Parameters
    ----------
    date_name :
    text :

    Returns
    -------

    """
    date_time, name = date_name.split(" - ")
    date_time = date_time.strip().replace(", ", "-")
    name = name[:-1].strip()
    return date_time, name, text


def wapp_parsing(file_to_parse: str,
                 file_to_read: str = "chat_whatsapp.csv",
                 verbose: bool = True) -> None:
    """

    Parameters
    ----------
    file_to_parse :
    file_to_read :
    verbose :
    """
    with open(file_to_parse,
              encoding="utf8") as wa_file, open(file_to_read,
                                                "w",
                                                encoding="utf8") as wa_csv:
        writer = csv.writer(wa_csv, delimiter='\t')
        writer.writerow(["datetime", "from", "text"])
        prev = str()
        # for line in wa_file:
        for line in _get_progressbar(wa_file, file_to_parse, verbose):
            date_name = _check_integrity(line)
            if date_name is not None:
                prev = date_name
                text = _get_text(line)
                writer.writerow(_process_string(prev, text))
            else:
                writer.writerow(_process_string(prev, line))


def telegram_parsing(file_to_parse: str,
                     file_to_write: str = "chat_telegram.csv",
                     verbose: bool = True) -> None:
    """

    Parameters
    ----------
    file_to_parse :
    file_to_write :
    verbose :
    """
    with open(file_to_parse,
              encoding="utf8") as json_file, open(file_to_write,
                                                  "w",
                                                  encoding="utf8") as csv_file:

        writer = csv.writer(csv_file, delimiter="\t")
        writer.writerow(["datetime", "from", "text"])
        messages = json.load(json_file)["messages"]
        for message in _get_progressbar(messages, file_to_parse, verbose):
            # converting date in format YYYY/MM/DD-hh:mm
            date_time = message["date"].replace("-", "/").replace("T", "-")[:-3]
            who_sent_msg = message["from"]
            text = message["text"]

            # empty text means that we sent some sort of files
            if text is None:
                text = "<" + message["media_type"] + ">"
                # if there is a media file and the text is not none then
                writer.writerow([date_time, who_sent_msg, text])
            # I cont them as two messages, one with a text and one with a file
            elif "media_type" in message:
                text = "<" + message["media_type"] + ">"
                writer.writerow([date_time, who_sent_msg, text])
            else:
                writer.writerow([date_time, who_sent_msg, text])
