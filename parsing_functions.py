import string
from typing import Dict, Tuple, List

import pandas as pd


def wapp_parsing(file_path: str, verbose: bool = False) -> Dict[str, List[str]]:
    """
    This function parses the log file avoiding non-text lines, and avoiding
    problems from messages sent by the same person in one minute

    Parameters
    ----------
    verbose :  bool
        verbose output
    file_path : str
        path to the chat

    Returns
    -------
    Dict[str, List[str]]
        return a dictionary to be converted into a pandas DataFrame
    """
    data = {"DateTime": [], "name": [], "msg": []}

    def line_splitter(unseparated_record: str) -> None:
        """
        This function splits each line of the log

        Parameters
        ----------
        unseparated_record : str
            a record from the chat
        """
        if unseparated_record.find(":") == 12:
            splitted = unseparated_record.split(' - ')
            data["DateTime"].append(splitted[0])

            splitted = splitted[1].split(":")
            data["name"].append(splitted[0])
            print(splitted)
            data["msg"].append(splitted[1][0:-1].lower())

    if verbose:
        print("Loading... Parsing the file.")

    with open(file_path) as f:
        prev = ""
        for line in f:
            # if the same person sent 2 messages in a minutes the second message
            # misses the date
            if len(line) != 0:
                if (line[0] in string.digits) and (line[1] in string.digits):
                    prev = line[0: line.find(":", 14, -1) + 1]
                    line_splitter(line)
                else:
                    line = prev + line
                    line_splitter(line)

    if verbose:
        print("File Parsed!")
    return data


# ===============================================================================

def data_manipulation(data: pd.DataFrame) -> pd.DataFrame:
    """
    This function manipulates the dataframe and extracts info

    Parameters
    ----------
    data :  pd.DataFrame
        a pandas DataFrame to be cleaned

    Returns
    -------
    pd.DataFrame
        a cleaned DataFrame
    """
    data['DateTime'] = pd.to_datetime(data['DateTime'],
                                      dayfirst=True,
                                      infer_datetime_format=True)
    data['msgLen'] = data.msg.apply(lambda x: len(x.split()))
    data.set_index("DateTime", inplace=True)
    return data


# ===============================================================================

def aggregateMonthName(data: pd.DataFrame) -> pd.DataFrame:
    """
    This function returns a dataframe grouped by the month and the name of who sent the messages
    with the number of text sent by the user during each month

    Parameters
    ----------
    data : pd.DataFrame
       a pandas DataFrame containing a chat

    Returns
    -------
    pd.DataFrame
        a pandas DataFrame grouped by month
    """
    final_df = pd.DataFrame()

    for name, DF in data.groupby(data["name"]):
        temp = DF.resample("M").mean()
        temp["name"] = name
        final_df = pd.concat([final_df, temp])

    return final_df


# ===============================================================================

def separate_media(data: pd.DataFrame,
                   hotkey: str = "<.*>") -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    This function returns a tuple containing a dataframe with only media and one without media

    Parameters
    ----------
    data : pd.DataFrame
        a pandas DataFrame containing a chat
    hotkey : str
        regex to find the media in a chat

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame]
        a tuple containing two pandas DataFrame with and without media.
    """

    media = data[data["msg"].str.contains(hotkey, regex=True)]
    not_media = data[data["msg"].str.contains(hotkey, regex=True)]

    return media, not_media
