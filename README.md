# Bio Jardas

Discord bot for the Aveiro Discord community.

## Building Docker Image

### Mac

This is useful for running the bot locally.

To build:

```bash
docker build -t tower.local:5000/bio-jardas:latest .
```

To run:

```bash
docker run --rm -v '/path/to/.env:/var/app/.env' --name bio-jardas tower.local:5000/bio-jardas:latest
```

### Mac To Linux

This builds and pushes to the registry in `tower.local`. Note that you need to set the
docker daemon to allow insecure registries.

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

### Linux (amd64)

This builds and pushes to the registry in `tower.local`. Note that you need to set the
docker daemon to allow insecure registries.

```bash
docker build -t tower.local:5000/bio-jardas:latest .
docker push tower.local:5000/bio-jardas:latest
```

## TODO

### Features

* replies
    * [x] general replies
    * [x] mention replies
    * [x] -mos replies
    * [x] add to default vocabulary
    * [x] add to any vocabulary
        * [ ] vocabulary_admin should have a suboption to create the message group
    * [x] replies configuration
        * [x] channel
        * [x] user
        * [x] intensity
    * [ ] help text for all reply commands
    * [ ] delete messages - admin
    * [ ] configure intensity per channel
        * [ ] allow setting all configured/enabled channels in a guild at the same time
* games
    * roulette
        * [x] russian roulette
        * [x] glock roulette
        * [x] hardcore roulette
        * [x] scoreboard
            * [ ] fix empty highscores
            * [ ] reset each month and announce winners
        * [x] self-ban/shadow
            * [x] remove ban after X hours has passed (requires scheduling)
    * gambling
        * [ ] simple slots
        * [ ] roulette
    * jardas points
        * [ ] gain points when bot randomly replies to user
        * [ ] gain points for roulette streaks
        * [ ] gain points for how long you self-ban
        * [ ] gamble points on slots (?)
* assorted features
    * [x] good morning
    * [x] fortune-teller
    * [x] event reminder
    * [x] huggies
* roast
    * [x] roast user
    * [x] self roast
    * [x] random roast
        * [ ] costs jardas points
* [ ] nuke
    * [ ] spend jardas points to protect/disarm nuke (winner wins)
        * [ ] starting the nuke costs a high initial point investment, then needs to be
          protected against disarms
* [ ] word cloud

### Internal

* [ ] differentiate between user error and internal errors in logs
* [ ] change `Config` model to `BotConfig`
* [ ] add simple permission RBAC system with hardcoded roles
    * we'll rely on configured roles in the discord server
* [x] dependency injection
* [x] refactor models and repositories into domains
* [ ] migrations should create the default message groups
* [ ] cooldown errors should not throw exceptions in logs
* [ ] handle DMChannel.name gracefully (DMChannels have no name)
* [ ] allow fine-grained cooldown per user per feature
    * Some users are abusing $roast random and should be rate limited much harder,
      perhaps even temporarily banned from the feature
* [ ] set up dev bot

### Take a look at

* [ ] gradio and/or streamlit for external apps