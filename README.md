# sanitise

Recently I needed some data in my personal Jamf Pro Cloud instance. Copying them from anywhere will introduce a security hole so I wrote these tools to sanitise the records. `sanitise` changes names, email addresses and serial number in the computer list so there is no real personal information in the computer list. That also changes the user records for any user who 'owns' a computer.  `users` removes all users who haven't been changed.

`groups` adds ten random computers to each computer group. Note that these computers will not actually conform to the group criteria, it just adds members so they can be used for testing.



Tool to sanitise computer records on your testing Jamf Pro instance
