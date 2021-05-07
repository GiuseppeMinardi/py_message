import re
from typing import Dict, List, Any, Tuple

import pandas as pd


def line_splitter(string_to_split: str):
    """

    Parameters
    ----------
    string_to_split :

    Returns
    -------

    """
    time, string_to_split = string_to_split.split('-', 1)
    who_sent, message_content = string_to_split.split(":", 1)
    return time.rstrip(), who_sent.rstrip(), message_content.rstrip()


def load_chat(path: str):
    """

    Parameters
    ----------
    path :

    Returns
    -------

    """
    record_start_pattern = "^[0-9][0-9]/[0-9][0-9]/[0-9][0-9], [0-9][0-9]:[0-9][0-9] - .* :"
    pattern = re.compile(record_start_pattern)
    chat_data_dict: Dict[str, List[Any]] = {'date': [],
                                            'name': [],
                                            'message': []}
    with open(path) as f:
        prev = ""
        for line in f:
            # if the same person sent 2 messages in a minutes the second message
            # misses the date
            if pattern.match(line):
                prev = pattern.findall(line)[0]
                try:
                    date_time, name, message = line_splitter(line)
                except ValueError:
                    print(f"Cannot parse this message:\n\t{line}")
            else:
                print("==================================================")
                print(prev)
                line = prev + line
                print(line)
                date_time, name, message = line_splitter(line)

            chat_data_dict["date"].append(date_time)
            chat_data_dict["name"].append(name)
            chat_data_dict["message"].append(message)

    chat_data_frame = pd.DataFrame(chat_data_dict)
    chat_data_frame['date'] = pd.to_datetime(chat_data_frame['DateTime'],
                                             dayfirst=True,
                                             infer_datetime_format=True)
    return chat_data_frame


def separate_media(chat_data_frame: pd.DataFrame,
                   hotkey: str = "<.*>") -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    This function returns a tuple containing a dataframe with only media and one without media

    Parameters
    ----------
    chat_data_frame : pd.DataFrame
        a pandas DataFrame containing a chat
    hotkey : str
        regex to find the media in a chat

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame]
        a tuple containing two pandas DataFrame with and without media.
    """
    contains_hotkey_series = chat_data_frame["message"].str.contains(hotkey, regex=True)
    media = chat_data_frame[contains_hotkey_series]
    not_media = chat_data_frame[~contains_hotkey_series]

    return media, not_media


chat_dataset = load_chat("./ChatWhatsApp.txt")
