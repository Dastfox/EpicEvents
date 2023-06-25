# UML

User
^
|
| (one-to-one)
|
UserWithRole
|
| (one-to-many)
v
Client <---(many-to-one)---> Contract <---(one-to-many)---> Event
| ^
| (one-to-many) |
v |
Event <-------------------|
|
| (one-to-many)
v
UserWithRole
