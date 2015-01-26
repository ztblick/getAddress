getAddress
Zachary Blickensderfer, JE '16
Last edited: Jan. 26, 2015
=========================================================================
This is a python script I've been working on to help me more efficiently
gather the contact information of clients who might potentially be interested
in contracting a performance by my singing group, the Yale Alley Cats.

It uses pre-existing modules like beautifulsoup and xlwt for HTML scraping
and Excel compatibility, respectively. I hope to be able to get this working
to the point that it can take an excel spreadsheet with a list of URLs and
return a list of email addresses.

As of right now, it has single-site functionality through terminal with
output into an excel file. Depth and time parameters help with the searching.
Working on debugging various cases in the HREF fields (like external and
previously seen links).
