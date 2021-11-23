import re
from types import CodeType
from typing import Union
import unicodedata
import pathlib
import os
from datetime import datetime
from multiprocessing import Pool

from helpers import replace_mul

from bs4 import BeautifulSoup
import requests as req
import pandas as pd
from tqdm import tqdm

BASE_LINK = "https://sb.atlantaned.space/library/"
LIBRARY_PATH = "./library/"
NORMAL = "normal"
DELETED = "deleted"

class InvalidSessionException(Exception): pass
class UnknownBookFormatException(Exception): pass
class BookUnavailableException(Exception): pass

class StatbusBook():
    id: int
    title: str
    raw_text: str
    text: str
    author: str
    ckey: str
    deleted: bool
    time_published: datetime
    round_published: int

    def __init__(self, soup: BeautifulSoup, id: int = 0) -> None:

        self.id = id or try_extract_id(soup)
        self.raw_text = extract_text_from_statbus(soup)
        self.text = preprocess_statbus_text(self.raw_text)
        self.deleted = check_deleted(soup)

        # Title is in the card's header, h3 to be specific
        h3_text = soup.find("h3", {"class": lambda x: "card-header" in x}).get_text().split("\n")
        #   Title (0)                    Author (1)                                         ckey (3) 
        # ['<some cool name>', '      By <in game name>', '                | ', '          <ckey>', '        ', '', '']
        self.title = h3_text[0]
        self.author = h3_text[1].replace("By", "").strip()
        self.ckey = h3_text[3].strip()

        footer = soup.find("div", {"class": "card-footer"})
        # The datetime, in ISO format, is located in the card footer in a tag called time, set as a property datetime
        try:
            self.time_published = datetime.fromisoformat(footer.find("time")["datetime"])
        except:
            self.time_published = datetime.fromtimestamp(0)
        # The round ID is located as text in an anchor in the footer
        try:
            self.round_published = int(footer.find("a").get_text())
        except:
            self.round_published = 0

    @classmethod
    def from_html(cls, html: str):
        if "Authorize remote access" in html: raise InvalidSessionException("Not authenticated")
        bs = BeautifulSoup(html, "html.parser")
        return cls(bs)

    @classmethod
    def from_id(cls, session_id: str, id: int):
        """
        Gets a book from StatBus. Requires a PHPSESSID cookie.
        """
        r = req.get(BASE_LINK + str(id), cookies={"PHPSESSID": session_id})
        return cls.from_html(r.text.strip())
    
    def __repr__(self) -> str:
        return f"StatbusBook, ID: {self.id}, Title: {self.title}"

    def __str__(self) -> str:
        return self.text

def extract_text_from_statbus(html: Union[str, BeautifulSoup]) -> str:
    """
    Parses StatBus' page and removes clutter, leaving only the book text
    """
    bs = html
    if not type(bs) == BeautifulSoup:
        bs = BeautifulSoup(html, "html.parser")
    body = bs.find("div", {"class": "card-body"})
    if not body:
        if ("Slim Application Error" in bs.get_text()): raise BookUnavailableException("Page returned an error")
        raise UnknownBookFormatException("Book could not be loaded correctly. Check your PHPSESSID cookie and if the book is available to read.")
    return body.get_text(separator= " ")

def check_deleted(html: Union[str, BeautifulSoup]) -> bool:
    """
    Checks if the book has been deleted based on raw html input
    """
    bs = html
    if not type(bs) == BeautifulSoup:
        bs = BeautifulSoup(html, "html.parser")
    bs = bs.find("div", {"class": "alert alert-danger"})
    return (bool(bs) and "This book has been deleted" in bs.get_text())

def try_extract_id(html: Union[str, BeautifulSoup]) -> int:
    """
    Tries to extract the ID from StatBus html. Returns the ID or 0
    """
    bs = html
    if not type(bs) == BeautifulSoup:
        bs = BeautifulSoup(html, "html.parser")
    try:
        # The only trace of an ID is in the form containing the button "Delete Book", so we'll try to find it
        form = bs.find("form", {"method": "POST"})
        # The aforementioned form posts to /library/<ID>/delete
        return int(form["action"].split("/")[2])
    except:
        return 0

def preprocess_statbus_text(s: str) -> str:
    """
    Preprocess string for analisys
    """
    s = unicodedata.normalize("NFKD", s)
    # Remove all extra new lines
    s = re.sub("\n{2,}", "", s)
    # Replace all kinds of special characters
    s = replace_mul(
        s, 
        ('„', '"'),
        ('”', '"'),
        ("’", "'"),
        ("\n", ". "),
        (" . ", ". ")
    )

    # Remove empty sentences
    s = re.sub("(\\. \\.)( \\.)*", " ", s)
    # Replace multiple spaces with only one
    s = re.sub(" {2,}", " ", s)

    return s.strip(".").strip()

def generate_library(session_id = None, overwrite_existing_books = False, workers = 4):
    """
    Generates a local library by scraping StatBus (thanks Ned)
    """
    if not session_id: session_id = input("Please input your PHPSESSID: ")

    last_downloaded_id = 1
    if not overwrite_existing_books:
        library = pathlib.Path(LIBRARY_PATH)
        try:
            # Ensure lists have at least one item
            last_downloaded_id = max(
                max([int(x.replace(".txt", "")) for x in (os.listdir(library.joinpath(NORMAL)) or ["1"])]),
                max([int(x.replace(".txt", "")) for x in (os.listdir(library.joinpath(DELETED)) or ["1"])])
            )
        except FileNotFoundError:
            pass # Lazyness, why have an if when you can have an exception

    r = req.get(BASE_LINK, cookies={"PHPSESSID": session_id})
    bs = BeautifulSoup(r.text.strip(), "html.parser")
    # Get the table of all books
    table = bs.find("table")
    if not table: raise Exception("Could not find table, most likely an authentication error. Check your PHPSESSID cookie")
    # Find the first anchor, which should be the link to the first book
    anchor = table.find("a")
    if not anchor: raise Exception("Could not find an anchor tag in the book list, something must be wrong.")
    # /library/<number>
    last_id = int(anchor["href"].split("/")[-1])

    generate_library_range(session_id, (last_downloaded_id, last_id + 1), workers=workers)

def generate_library_range(session_id, id_range: tuple[int, int], workers = 4):
    """
    Generates a local library from a range, [start, end)
    """
    pool = Pool(processes=workers)

    library = pathlib.Path(LIBRARY_PATH)
    normal_path = library.joinpath(NORMAL)
    deleted_path = library.joinpath(DELETED)

    if not library.exists(): os.mkdir(library)
    if not normal_path.exists(): os.mkdir(normal_path)
    if not deleted_path.exists(): os.mkdir(deleted_path)

    df_path = library.joinpath("book_metadata.csv")
    if os.path.exists(df_path):
        df = pd.read_csv(df_path)
    else: df = pd.DataFrame()

    metadata = []
    print(f"Downloading library books from {id_range[0]} to {id_range[1]}")
    try:
        responses = [pool.apply_async(StatbusBook.from_id, args=(session_id, x,)) for x in range(*id_range)]
        for res in tqdm(responses):
            book = None
            while True:
                try:
                    book: StatbusBook = res.get()
                    break
                except InvalidSessionException:
                    session_id = input("Cookie invalid. Please insert a new PHPSESSID cookie: ")
                except BookUnavailableException:
                    #print("Warning: book {} is not available".format(book_id))
                    break
            if not book: continue
            
            if book.deleted:
                book_path = deleted_path.joinpath(str(book.id) + ".txt")
            else:
                book_path = normal_path.joinpath(str(book.id) + ".txt")
            with open(book_path, "w", encoding="utf-8") as f:
                f.write(book.text)
                f.flush()
                f.close()
            metadata.append((book.id, book.title, book.author, book.ckey, book.deleted, book.time_published, book.round_published))
    finally: # TODO: make sure this works fine
        df = df.append(pd.DataFrame(metadata, columns=["ID", "Title", "Author", "CKEY", "Deleted", "Time Published", "Round Published"]))
        df.to_csv(library.joinpath("book_metadata.csv"), index=0)
