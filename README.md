# NoSoft
NoSoft is a simple CLI messenger that works on the principle of separate chat rooms.

## Brief decription
+ Each client must be logged in before starting the chat. All credentials are stored in **database.db**.
+ The client can create a room or join an existing one.
+ Any number of clients can connect to the room.
+ When creating a room, the client receives an ID that others can use to connect.

## Configuration file
You can configure server settings in **settings.json**:  

` max_connections ` - maximum number of clients  
` port ` - port for connecting to the server

## Usage
Just elevate permissions of the **start_server.sh** script and run it:  

```chmod +x start_server.sh & ./start_server.sh ```
