# hertz-feed
This is the Hertz feed script I use.

Since I have not kept up with the changes made from cm-steem's initial reference script release I didn't want to clone and issue a pull request so as not to disrupt the flow of his changes. 

This version differs mainly with additions for:
- added logging to file
- removed unused imports
- inline initializing of the wallet so this program stands alone (eliminates need for external program)
- uses Python-BitShares lib ability to automatically select an API connection from a list
- no longer requires an external timer or systemd to publish feeds, just set FREQ to interval desired
