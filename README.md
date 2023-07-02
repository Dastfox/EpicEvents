# endpoints

| Resource     | Endpoint           | Methods | Description                    | Request Body        |
| ------------ | ------------------ | ------- | ------------------------------ | ------------------- |
| UserWithRole | `/users/`          | GET     | Get all users with roles.      | N/A                 |
|              |                    | POST    | Create a new user with a role. | UserWithRole object |
|              | `/users/{id}/`     | PUT     | Update a user's role.          | UserWithRole object |
|              | `/users/{id}/`     | DELETE  | Delete a user with a role.     | N/A                 |
|              |                    |         |                                |                     |
| Client       | `/clients/`        | GET     | Get all clients.               | N/A                 |
|              |                    | POST    | Create a new client.           | Client object       |
|              | `/clients/{id}/`   | PUT     | Update a client.               | Client object       |
|              | `/clients/{id}/`   | DELETE  | Delete a client.               | N/A                 |
|              |                    |         |                                |                     |
| Event        | `/events/`         | GET     | Get all events.                | N/A                 |
|              |                    | POST    | Create a new event.            | Event object        |
|              | `/events/{id}/`    | PUT     | Update an event.               | Event object        |
|              | `/events/{id}/`    | DELETE  | Delete an event.               | N/A                 |
|              |                    |         |                                |                     |
| Contract     | `/contracts/`      | GET     | Get all contracts.             | N/A                 |
|              |                    | POST    | Create a new contract.         | Contract object     |
|              | `/contracts/{id}/` | PUT     | Update a contract.             | Contract object     |
|              | `/contracts/{id}/` | DELETE  | Delete a contract.             | N/A                 |
