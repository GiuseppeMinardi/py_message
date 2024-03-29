"""
This module provides functions useful to parse conversations extracted from
different instant messages provider such WhatsApp e Telegram
"""
import csv
import json
import mmap
import re
from typing import Optional, Tuple, Iterable

from tqdm import tqdm


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
    Taken from https://blog.nelsonliu.me/2016/07/30/progress-bars-for-python-file
    -reading-with-tqdm/

    Parameters
    ----------
    file_path :

    Returns
    -------
    int
    """
    with open(file_path, "r+") as f_path:
        buf = mmap.mmap(f_path.fileno(), 0)
        lines = 0
        while buf.readline():
            lines += 1
    return lines


def _get_progressbar(file_iterator: Iterable[str],
                     file_path: str,
                     verbosity: bool = False) -> object:
    """
    If set to verbose returns a progressbar
    Parameters
    ----------
    file_iterator :  Iterable[str]
    file_path :  str
    verbosity : bool

    Returns
    -------
    object
        a simple progressbar with tqdm
    """
    if verbosity:
        return tqdm(file_iterator, total=_get_num_lines(file_path))
    return file_iterator


def _process_string(date_name: str,
                    text: str) -> Tuple[str, str, str]:
    """
    return the row to write into a file
    Parameters
    ----------
    date_name : str
    text : str

    Returns
    -------
    Tuple[str, str, str]
        a tuple containing a date, the name of who sent the message
        and the message
    """
    date_time, name = date_name.split(" - ")
    date_time = date_time.strip().replace(", ", "-")
    name = name[:-1].strip()
    return date_time, name, text


def app_parsing(file_to_parse: str,
                file_to_write: str = "chat_whatsapp.csv",
                verbose: bool = True) -> None:
    """
    WhatsApp parser. Takes the path of a conversation extracted from whatsapp
    and creates a csv file easier to read with pandas
    Parameters
    ----------
    file_to_parse : str
        Path to a file to read
    file_to_write : str
        Name of the file to write. Default is ""chat_whatsapp.csv"
    verbose : bool
        If true prints a progressbar parsing the file

    Returns
    -------
    None
    """
    with open(file_to_parse,
              encoding="utf8") as wa_file, open(file_to_write,
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
    Telegram parser. Takes the path of a conversation extracted from Telegram
    in json format and creates a csv file easier to read with pandas

    Parameters
    ----------
    file_to_parse : str
        Path to a file to read
    file_to_write : str
        Name of the file to write. Default is ""chat_whatsapp.csv"
    verbose : bool
        If true prints a progressbar parsing the file

    Returns
    -------
    None
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
