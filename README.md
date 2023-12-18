# Redis + bytewax

Blogpost: https://bytewax.io/blog/redis-pubsub-input

This demo is designed for bytewax v0.18:

```
pip install bytewax==0.18
```

Alternatively, run all required listener/publisher scripts alongside a redis container using docker compose:

```
docker-compose up
```


## echo bytewax dataflow

```
python -m bytewax.run src/redis_dataflow_echo:flow
```

To adjust connection settings, copy [envrc template](./envrc_template) to `.envrc` (assuming you want to use [direnv](direnv.net)) and modify accordingly
