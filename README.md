# sanitise

Recently I needed some data in my personal Jamf Pro Cloud instance. I used "jamf-migrator" (https://github.com/jamf/JamfMigrator) for almost everything, making sure to go in to the 'computer' pane of preferences and tick "migrate computer as managed" and add an account name and password.

Copying records from anywhere will introduce a security hole so I wrote these tools to sanitise the records. `sanitise` changes names, email addresses and serial number in the computer list so there is no real personal information in there. That also changes the user records for any user who 'owns' a computer.  `users` removes all users who haven't been changed.

`groups` adds ten random computers to each computer group. Note that these computers will not actually conform to the group criteria, it just adds members so they can be used for testing.

After you do this you might want to use Jamf Cloud Package Replicator (https://github.com/BIG-RAT/jamfcpr) to copy packages from somewhere to your test instance.
