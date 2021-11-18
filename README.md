# airlines-manager-bot
A dockerized CLI bot (crawler) to add some automations on the [Airlines Manager](airlines-manager.com) game.


## Setup

Copy the environment file template to the real env

```
cp .env.template .env
```

Edit the file to your data.

Start the container:

```
docker-compose up --build -d
```

And run the main CLI script

 ```
docker exec -it airlines-manager-bot python3 main.py
```
