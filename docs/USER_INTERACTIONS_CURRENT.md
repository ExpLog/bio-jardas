# Current User Interactions

Bio Jardas is a Discord bot that interacts with users through passive listeners and explicit commands. The command prefix is `$`.

## Passive Interactions

The bot listens to all messages in enabled channels and may respond based on its current **intensity** setting and configured **message groups**.

### Automated Replies
* **Mentions:** If you mention the bot, it will respond with a message from the `mention` group.
* **Content-based Replies:** Some message groups use dynamic handlers (like `caralhamos`) that process words from your message to generate a response.
* **Random Replies:** In enabled channels, the bot may randomly select a message from assigned groups based on configured weights.

## Commands

Commands use the `$` prefix.

### General Commands
* `$status`: Shows the bot's current status, including intensity and assigned message groups for the current channel.
* `$intensity <value>`: Sets the bot's response intensity. Possible values: `off`, `low`, `medium`, `high`, `extreme`, `insane`. (Cooldown: 1 per 10s per channel).
* `$huggies`: Sends a hug to the user.
* `$fortune_teller`: Tells a fortune (limited to 1 per week).
* `$vocabulary <text>`: Adds `<text>` to the user-added vocabulary.
* `$roast <member>`: Roasts the specified member.
* `$roast me`: Roasts you.
* `$roast random`: Roasts a random member of the server. (Cooldown: 5 per 60s per user).

### Games
* `$russian_roulette`: Play Russian Roulette.
* `$hardcore_roulette`: Play Hardcore Roulette.
* `$glock_roulette`: Play Glock Roulette.
* `$shadow <hours>`: Try your luck; if you lose, you get shadow-banned for the specified hours.
* `$highscores`: Displays leaderboards for the roulette games.

### Admin Commands (Bot Owner Only)

#### Reply Configuration (`$reply`)
* `$reply groups`: Lists all available message groups.
* `$reply show channel`: Shows assigned message groups and their probabilities for the current channel.
* `$reply show user [member]`: Shows assigned message groups and their probabilities for a user.
* `$reply channel enable`: Enables replies for the current channel.
* `$reply channel disable`: Disables replies for the current channel.
* `$reply channel add <group_name> [weight] [independent_roll_probability]`: Adds a message group to the current channel.
* `$reply channel remove <group_names...>`: Removes message groups from the current channel.
* `$reply channel clear`: Clears all message groups from the current channel.
* `$reply channel apply-defaults`: Applies default message groups to the current channel.
* `$reply user add <member> <group_name> [weight] [independent_roll_probability]`: Adds a message group to a user.
* `$reply user remove <member> <group_names...>`: Removes message groups from a user.
* `$reply user clear <member>`: Clears all message groups from a user.

#### Vocabulary & Message Groups
* `$vocabulary_admin <group_name> <text>`: Adds `<text>` to a specific message group.
* `$add_message_group <group_name>`: Creates a new message group.

#### Scheduling (`$schedule`)
* `$schedule message --message-group <group> --cron <cron_expression> [--id <job_id>]`: Schedules a random message from a group.
* `$schedule event-reminder --event-name <name> [--event-link <link>] --cron <cron>|--timestamp <ts> [--message-group <group>] [--id <job_id>]`: Schedules an event reminder.
* `$schedule list`: Lists all scheduled jobs.
* `$schedule remove <job_id>`: Removes a scheduled job.
