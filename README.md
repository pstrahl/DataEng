# Data Engineering Exercise
In this project we extract, transform, and load constituent data to obtain specific information about constituents and acquisition of constituents.

## Objective

To find the (primary) email address, source code, subscription status, creation date, and updated date for each constituent, as well as the number of constituents 
acquired per calendar date, then save this information in two csv files.

## Files

1. **cons.csv**: stores the general data for each constituent, in particular the constituent id, the source code, the created date, and the modified date. <br>
2. **cons_email.csv**: stores the email data for each constituent, including the constituent id, constituent email id, email address, and a flag determining whether
the email is the primary email address. <br>
3. **chapter.csv**: stores the subscription data for some of the constituents, including the constituent email id, the chapter id, and whether they are still 
subscribed to the chapter. <br>

## Methods

We define a class to construct the relevant tables and create the csv files.

After loading each csv into pandas, we convert all of the dates to np.datetime64[ns]. We extract only those records corresponding to the primary email address in the
second dataframe, and only those records in the third dataframe corresponding to a chapter id of 1. From here, we merge these two dataframes using the constituent email id,
and fill the missing values to indicate that, if an email id fails to appear in the third dataframe, then it is assumed that the constituent associated with that email 
id is still subscribed to chapter 1. Finally, we merge this dataframe with the first dataframe (corresponding to the general data for each constituent) using the constituent
id. To determine the creation date and updated date, we take the minimum and maximum, respectively, of the created date and the modified date from the first original 
dataframe since for over half of the records the modified date is before the created date. After this we select the columns mentioned in the objective.

We use the people table to form the acquisition_facts table as follows. We create a copy of the people table, then extract the month and day from the creation date column,
and save this as a new column to the new people table. From here we group the entries in the creation date column by the new column and count the entries in each group.
Finally, we convert the resulting series to a dataframe, reset the index, and rename the columns to obtain the acquisition_facts table.

## Output

* people.csv has the following schema: <br>
  |**Column**|**Type**|**Description**|
  |--------|------|----------------------------------------|
  |email|string|primary email address of constituent|
  |code|string|constituent's source code|
  |is_unsub|Boolean|whether the primary email address is unsubscribed to chapter 1|
  |created_dt|datetime|the date of the constituent's creation in the database|
  |updated_dt|datetime|the date that the constituent was updated in the database|

* acquisitions.csv has the following schema: <br>
  |**Column**|**Type**|**Description**|
  |--------|------|--------------|
  |acquisition_date|date|the calendar date of acquisition|
  |acquisitions|int|the number of acquisitions made on acquisition_date|






