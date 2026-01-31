# Bio Jardas

Discord bot for the Aveiro Discord community.


## TODO

### Features
* [x] replies
  * [x] general replies
  * [x] mention replies
  * [x] -mos replies
  * [x] add to default vocabulary
  * [x] add to any vocabulary
  * [x] replies configuration
    * [x] channel
    * [x] user
    * [x] intensity
  * [ ] help text for all reply commands
  * [ ] delete messages - admin
  * [ ] configure intensity per channel
    * [ ] allow setting all configured/enabled channels in a guild at the same time
* [x] roulette
  * [x] russian roulette
  * [x] glock roulette
  * [x] hardcore roulette
  * [x] scoreboard
  * [x] self-ban/shadow
    * [x] remove ban after X hours has passed (requires scheduling)
* [x] good morning
* [x] fortune-teller
* [x] event reminder
* [x] huggies
* [x] roast
  * [x] roast user
  * [x] self roast
  * [x] random roast
* [ ] nuke
  * [ ] nuke count
  * [ ] nuke defuse
* [ ] word cloud
* [ ] health check

### Internal
* [ ] differentiate between user error and internal errors in logs
* [ ] change `Config` model to `BotConfig`
* [ ] add simple permission RBAC system with hardcoded roles
  * we'll rely on configured roles in the discord server
* [x] dependency injection
* [x] refactor models and repositories into domains
* [ ] migrations should create the default message groups
* [ ] cooldown errors should not throw exceptions in logs

### Take a look at
* [ ] gradio and/or streamlit for external apps


## Building Docker Image

### Mac
To build:

```bash
docker build -t tower.local:5000/bio-jardas:latest .
```

To run:

```bash
docker run --rm -v '/path/to/.env:/var/app/.env' --name bio-jardas tower.local:5000/bio-jardas:latest
```

### Mac To Linux

This builds and pushes to the registry in `tower.local`. Note that you need to set the docker daemon to allow insecure registries.
```bash
docker buildx build --platform linux/amd64 -t tower.local:5000/bio-jardas:latest --push --provenance false --sbom false .
```

Alternatively, we can use a tool like `skopeo` to push the image to the registry:
```bash
docker buildx build --platform linux/amd64 -t bio-jardas:latest --load .
skopeo copy \
  --dest-tls-verify=false \
  docker-daemon:bio-jardas:latest \
  docker://tower.local:5000/bio-jardas:latest
```

If you are using a Mac, then you need to run:
```bash
docker buildx build --platform linux/amd64 -t bio-jardas:latest --load .
SOCK=$(docker context inspect "$(docker context show)" \
  --format '{{ (index .Endpoints "docker").Host }}')
skopeo copy \
  --src-daemon-host="$SOCK" \
  --dest-tls-verify=false \
  docker-daemon:bio-jardas:latest \
  docker://tower.local:5000/bio-jardas:latest
```