from bs4 import BeautifulSoup
import pandas as pd
import sys
import re

"""
Data parser to read html files as read from politicsresources.net into
.csv files.

Including a Constituency class and a parse function.

Usage:

    Constituency class and parse function can be imported for use with
    IPython.

    Run the file with a .htm file as a command line argument to produce
    a .csv file with the expected file name.

    For example:

    $ ls
    data.htm
    $ python3 parser.py data.htm
    $ ls
    data.htm    data.csv
"""
__author__ = "Toby James"
__email__ = "tobyswjames@gmail.com"
__version__ = "0.1.0"
__status__ = "Development"
__maintainer__ = "Toby James"
__license__ = "Beerware"


class Constituency():
    """
    Constituency class. Represents a constituency result at an election.
    Public variables:
        name: constituency name
        candidates: candidates who stood at an election
        parties: candidates' respective parties
        votes: votes cast for each candidate
        percent: percentage of the vote in favour of each candidate
    """
    def __init__(self, name: str):
        """
        Initialise a named constituency with a given name. Creates
        instance variables for candidates, parties, votes and
        percentages.

        @param name (str): Name of the constituency.
        """
        self.name = name
        self.candidates = []
        self.parties = []
        self.votes = []
        self.percent = []
        self.electorate = []

    def to_pandas(self) -> pd.DataFrame:
        """
        Produce a Pandas DataFrame from the Constituency data.

        Returns a Pandas DataFrame of the following shape:

            names   candidates  parties votes   percent
        0   string  string      string  string  string
        .
        .
        .
        """
        # Create list with the name of the constituency repeated as many
        # times as there are candidates
        names = [self.name] * len(self.candidates)
        electorates = [self.electorate] * len(names)

        # Initialise empty Pandas DataFrame of the desired shape
        dataframe = pd.DataFrame(columns=["names",
                                          "candidates",
                                          "parties",
                                          "votes",
                                          "percent",
                                          "electorate"])

        # Populate the DataFrame for return
        dataframe['names'] = names
        dataframe['candidates'] = self.candidates
        dataframe['parties'] = self.parties
        dataframe['votes'] = self.votes
        dataframe['percent'] = self.percent
        dataframe['electorate'] = electorates

        return dataframe


def parse(file_handle: str, write_to_csv=False) -> pd.DataFrame:
    """
    Parse a given file into a Pandas DataFrame for analysis.

    @param file_handle (str): Name of the file to open. Accepted file
                              types are .htm. Will work for .html but
                              any produced .csv files will be named
                              incorrectly.
    @param write_to_csv (bool): If True, produces a .csv file with the
                                same name as the .htm file.
    """
    # Read the given file into a BeautifulSoup instance
    soup = BeautifulSoup(open(file_handle), features='lxml')
    # politicsresources.net contains the interesting data in a <table>
    # tag. There are two on the page, and the data is in the second.
    big_table = soup.find_all('table')[1]

    # Init blank lists for the constituencies in the given dataset.
    constituencies = []
    constituency_names = []
    electorates = []

    # Iterate over the table identifying each constituency
    for tr in big_table.find_all('tr'):

        # Add constituency names to an array
        for constituency_name in tr.find_all('b'):
            constituency_names.append(constituency_name)

        # Collect electorate figures.
        for constituency_info in tr.find_all('p'):
            # Regex to match the electorate figures on the webpage
            exp = re.search('Electorate: [\d,]{1,}', constituency_info.text)
            # Strip useless characters and commas
            new_exp = exp.group(0).replace('Electorate: ', '').replace(',', '')
            electorates.append(new_exp)

    # Count of constituencies iterated over
    con_count = 0
    # Iterate over the tables, each representing a constituency
    for table in big_table.find_all('table'):
        # Create Constituency object for each constituency
        constituency = Constituency(constituency_names[con_count].text)
        # Update electorate value for each constituency
        constituency.electorate = electorates[con_count]
        con_count += 1  # Increment constituency count

        # Count for within each table to determine the type of data
        count = 0
        for row in table.find_all('tr'):
            # Iterate over rows of table
            for item in row.find_all('td'):
                # Iterate over contents of each row
                # Depending on count value, determines the meaning of
                # the row item
                if count % 4 == 0:
                    _item = item.text.replace(',', '').replace('*', '')
                    constituency.candidates.append(_item)
                elif count % 4 == 1:
                    _item = item.text.replace(',', '')
                    constituency.parties.append(_item)
                elif count % 4 == 2:
                    _item = item.text.replace(',', '')
                    constituency.votes.append(_item)
                elif count % 4 == 3:
                    _item = item.text.replace(',', '').replace('%', '')
                    constituency.percent.append(_item)
                count += 1  # Increment

        # Add constituency to constituency list
        constituencies.append(constituency)

    # Create DataFrame for file
    dataframe = pd.DataFrame(columns=["names",
                                      "candidates",
                                      "parties",
                                      "votes",
                                      "percent"])

    for constituency in constituencies:
        # Add constituencies to the DataFrame
        try:
            dataframe = pd.concat([dataframe, constituency.to_pandas()])
        except(ValueError) as e:
            # Means the shape of the data is not as expected. This is
            # the case for university seats - so far skipping them
            # I'm not sure this will necessarily always work but I think
            # it does for the current datasets
            pass

    # Strip commas from constituency names
    dataframe['names'] = dataframe['names'].str.replace(',', '')

    if write_to_csv:
        # Write to .csv file named after original file.
        # If original file is .html rather than .htm the resulting file
        # will be ..csv because I just stripped the last 3 characters :)
        dataframe.to_csv(file_handle[:-4] + ".csv", index=False, header=False)

    return dataframe


if __name__ == "__main__":
    # If run with a command line argument of a file, create a .csv for
    # that file

    # Print the filename for feedback when iterating over multiple files
    print(sys.argv[1])
    parse(sys.argv[1], write_to_csv=True)
