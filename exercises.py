from __future__ import print_function

import pandas as pd
import numpy as np


def get_column_info(df):
    """
    Get the number of unique values and missing values per column.

    Args:
        df (Dataframe): This is the dataframe whose columns we will probe.
    Returns:
        None
    """
    for col in df.columns:
        print("column :{}, dtype:{}, size:{}, unique values:{}, missing values: {}"
              .format(col, df[col].dtype, df[col].size, df[col].unique().size,
                      df[df[col].isna()].index.size
                      )
              )


class People:
    """This class produces the people table.

    The class is initialized with 3 dataframes consisting of general information
    about the constituents (const), email information about the constituents (primary_emails),
    and subscription information about the constituents (const_sub).

    The people csv file will contain the constituent's primary email address,
    the constituent's source code from the first dataframe, whether they have
    a subscription to Chapter 1, the creation date of the constituent in the
    database, and the updated date of the constituent in the database.
    """

    def __init__(self):
        """
        Create the initial dataframes from the csv files.

        Returns:
             None
        """
        self.const = pd.read_csv(r"cons.csv")
        self.primary_emails = pd.read_csv(r"cons_email.csv")
        self.const_sub = pd.read_csv(r"chapter.csv")
        self.people = None
        self.acquisition_facts = None

    def get_const(self):
        """
        Get only the relevant columns from the const table and convert to datetime64[ns].

        Returns:
            None
        """
        self.const = self.const.loc[:, ["cons_id", "source", "create_dt", "modified_dt"]].copy()
        date_cols = ["create_dt", "modified_dt"]
        # Strip the day of the week and convert to datetime64[ns]
        for col in date_cols:
            self.const[col] = pd.to_datetime(self.const[col].apply(lambda x: x[5:]))

    def get_primary_emails(self):
        """
        Get only the relevant columns and rows from the primary_emails table and convert to datetime64[ns].

        Returns:
            None
        """
        self.primary_emails = self.primary_emails.loc[:,
                                    ["cons_email_id", "cons_id", "is_primary",
                                    "email", "create_dt", "modified_dt"]
                                    ].copy()
        self.primary_emails = self.primary_emails[self.primary_emails["is_primary"] == 1].copy()
        date_cols = ["create_dt", "modified_dt"]
        # Strip the day of the week and convert to datetime64[ns]
        for col in date_cols:
            self.primary_emails[col] = \
                pd.to_datetime(self.primary_emails[col].apply(lambda x: x[5:]))

    def get_const_sub(self):
        """
        Get only the relevant columns and rows from the const_sub table and convert to datetime64[ns].

        Returns:
            None
        """
        self.const_sub = \
            self.const_sub.loc[:, ["cons_email_id", "chapter_id", "isunsub", "unsub_dt", "modified_dt"]].copy()
        self.const_sub = \
            self.const_sub[self.const_sub["chapter_id"] == 1].copy()
        date_cols = ["unsub_dt", "modified_dt"]
        for col in date_cols:
            self.const_sub[col] = \
                pd.to_datetime(self.const_sub[col].apply(lambda x: x[5:]))

    def get_people(self):
        """
        Merge the dataframes using the cons_id and cons_email_id in the tables.

        The people table has the following fields: email (the primary email address),
        code (the source code of the constituent), is_unsub (whether the constituent is
        unsubscribed to chapter 1), created_dt (the creation date of the constituent's
        account), and updated_dt (the date the constituent's account was updated).

        Since some of the create_dts are chronologically after the modified_dts in the
        const table, we take the min as the created_dt and the max as the updated_dt.
        Returns:
            None
        """
        self.people = self.primary_emails.merge(self.const_sub, "left",
                                                on="cons_email_id",
                                                suffixes=["_pr", "_csub"],
                                                indicator=True
                                                ).copy()
        # Fill the missing values of chapter_id with 1 and unsubscribed with 0
        # using assumption that if a constituent does not appear in const_sub
        # then they are still subscribed to chapter 1.
        self.people = self.people.fillna(value={"chapter_id": 1, "isunsub": 0})
        self.people = self.const.merge(self.people, "right",
                                        on="cons_id",
                                        suffixes=["_con", "_pr"],
                                        indicator="_merge2"
                                        ).copy()
        # For some of the records, the created date comes after the modified date in the
        # const table. I took this to mean that there is an error, so I took the minimum
        # of the two dates for the created_dt and the larger for the updated_dt.
        self.people["created_dt"] = \
            self.people.loc[:, ["create_dt_con", "modified_dt"]].apply(np.min, axis=1)
        self.people["updated_dt"] = \
            self.people.loc[:, ["create_dt_con", "modified_dt"]].apply(np.max, axis=1)
        self.people = self.people.loc[:, ["email", "source", "isunsub", "created_dt", "updated_dt"]].copy()
        self.people.rename(mapper={"email": "email", "source": "code",
                                   "isunsub": "is_unsub", "created_dt": "created_dt",
                                    "updated_dt": "updated_dt"}, axis=1, inplace=True
                           )

    def get_acquisition_facts(self):
        """
        Obtain the number of constituents acquired per calendar day in a dataframe.

        The columns are acquisition date, which is the month-day of the calendar year, and
        acquisitions, which is the number of constituents acquired on that day.
        """
        extended_people = self.people.copy()
        # Get the month and day of the date of creation
        acq_dates = extended_people["created_dt"].apply(lambda d: d.strftime("%m-%d"))
        extended_people["acquisition_date"] = acq_dates
        acquisition_series = extended_people.groupby("acquisition_date")["created_dt"].count()
        self.acquisition_facts = pd.DataFrame(acquisition_series)
        self.acquisition_facts.reset_index(inplace=True)
        self.acquisition_facts.rename(mapper={"acquisition_date": "acquisition_date",
                                              "created_dt": "acquisitions"}, axis=1, inplace=True
                                      )
if __name__ == "__main__":
    exercise = People()
    print("Constituents: \n {}".format(exercise.const.head()))
    get_column_info(exercise.const)
    exercise.get_const()
    # Verify type conversion performed as expected
    get_column_info(exercise.const)
    print("Constituents: \n {}".format(exercise.const.head()))
    print("Primary_emails: \n {}".format(exercise.primary_emails.head()))
    get_column_info(exercise.primary_emails)
    exercise.get_primary_emails()
    # Verify type conversion performed as expected
    get_column_info(exercise.primary_emails)
    print("Primary emails: \n {}".format(exercise.primary_emails.head()))
    print("Constituents Subscription Info: \n {}".format(exercise.const_sub.head()))
    get_column_info(exercise.const_sub)
    exercise.get_const_sub()
    # Verify type conversion performed as expected
    get_column_info(exercise.const_sub)
    print("Constituents Subscription Info: \n {}".format(exercise.const_sub.head()))
    exercise.get_people()
    print("People: \n {}".format(exercise.people.head()))
    exercise.people.to_csv(r"people.csv",
                           header=["email", "code", "is_unsub", "created_dt", "updated_dt"],
                           na_rep='NULL')
    exercise.get_acquisition_facts()
    print("Acquisition facts: \n {}".format(exercise.acquisition_facts.head()))
    exercise.acquisition_facts.to_csv(r"acquisition_facts.csv",
                                      header=["acquisition_date", "acquisitions"]
                                      )





