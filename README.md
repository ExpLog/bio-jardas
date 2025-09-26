# Bio Jardas

Discord bot for the Aveiro Discord community.


## TODO

### Features
* [ ] replies
  * [x] general replies
  * [x] mention replies
  * [ ] -mos replies
  * [x] add to default vocabulary
  * [x] add to any vocabulary
  * [x] replies configuration
    * [x] channel
    * [x] user
    * [x] intensity
  * [ ] help text for all reply commands
* [ ] roulette
  * [ ] russian roulette
  * [ ] hardcore roulette
  * [ ] scoreboard
  * [ ] self-ban/shadow
* [ ] good morning
* [ ] fortune-teller
* [ ] event reminder
* [x] huggies
* [ ] roast
  * [ ] roast user
  * [ ] random roast
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
