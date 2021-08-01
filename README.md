# Simple CRUD resource manager with quotas

Django api that allow to CRUD resources, manage users

## Installation

TODO: Describe the installation process

## Usage

1. Clone repo on a server that will run API
2. Make sure that docker is up to date
3. Run `docker-compose run test` to run tests for api
4. Run `docker-compose run api` to start api server
   
Api will be accesable on localhost:8000

## Endpoints

###/swagger
Endpoint which contains all documentation to api

###/register
Allow new user to register in the system using username, email and password. 

Note:
username and email must be unique.

###/login
Allow user registered in the system to authenticate using email and password and receive token pair for access and 
refresh. 

Note: Access token is used in Headers to requests. Example: `Authorization: Bearer <token>`.

###/refresh
Allow user to refresh access token 

###/resource
Allow user to CRUD resources which belongs to this user.

On create operation checked if the quota suffice and user is allowed to create resources.

If quota is depleted error message `"User's quota exceeded"` is received.

If user is prohibited from resource creation error message `"User is prohibited from creating resources by Admin"` id received

###/users
Allow user to view information about himself and to delete his account

###/admin
This section is dedicated to endpoints which requires admin permissions

####/admin/resources
Allows admin to CRUD any resource in the system

####/admin/users
Allows admin to list, delete any user the system

####/admin/quotas
Allows admin to set quotas for users.
Quota is number of resources which user could create.
Allowed is the state which allows/disallows new resource creation for user.



## Limitations and known errors
All limitations and known errors is result of developer's time constraint :)

Tests does not cover permissions check, meaning that case when user trying to access admin's api is not covered

Swagger shows some endpoints (register, login) as locked behind auth, but in fact they are free for all

Swagger does not show all errors codes that api return due to specific of ModelViewSet and the library interactions

