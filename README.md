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

### Take a look at
* [ ] gradio and/or streamlit for external apps