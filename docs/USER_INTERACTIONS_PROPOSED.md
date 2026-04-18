# Proposed User Interaction Improvements

This document outlines the proposed improvements to the Bio Jardas interaction model, focusing on command consolidation, tree simplification, and a more intuitive help system.

## 1. Command Consolidation & Reorganization

### Unified Vocabulary Management
Consolidate all vocabulary and message group management into a single `$vocabulary` group to reduce top-level clutter:
* `$vocabulary <text>`: (Default) Add to user-added vocabulary (current `$vocabulary`).
* `$vocabulary add <group_name> <text>`: Add text to a specific message group (current `$vocabulary_admin`).
* `$vocabulary group create <name>`: Create a new message group (current `$add_message_group`).

### Unified Reply Configuration
Move the `config` commands into the `reply` domain to centralize response-related settings and eliminate redundancy:
* `$reply intensity <value>`: Sets the reply probability (current `$intensity`).
* `$reply status [target]`: A single polymorphic command for checking configuration and probabilities.
    * **No target:** Shows current channel settings (intensity, enabled status, assigned groups).
    * **User target:** Shows probabilities and groups assigned to that user.
    * **Channel target:** Shows probabilities and groups assigned to that specific channel.
    * *This replaces `$status`, `$reply show channel`, and `$reply show user`.*

### Roast Consistency
Ensure the `$roast` group handles its logic consistently as a single intuitive entry point:
* `$roast [me|random|<member>]`

## 2. Enhanced Help System

### Nested Command Visibility
Override the help command behavior to ensure that invoking a group (e.g., `$help reply`) or calling a group without arguments automatically lists all available subcommands and their descriptions.

### Meaningful Help Strings
Replace all "WIP help" and "TODO" placeholders with clear, user-friendly descriptions. This provides necessary information only when the user explicitly seeks it, avoiding unsolicited bot messages.

### Access-Aware Help
The help system should respect the bot owner check, filtering or marking Admin-only subcommands (like `$vocabulary add`) so the interface remains relevant to the caller.

## 3. Feedback Policy

### Preserving Emojis
Maintain the use of emoji reactions for success and error feedback (e.g., cooldowns, permission errors). This design choice effectively communicates status without causing message spam in the server.

## 4. Proposed Top-Level Structure

By consolidating these domains, the bot's interface becomes significantly more organized:

**Public Commands:**
* `$huggies`, `$fortune_teller`, `$roast`, `$vocabulary <text>`
* `$russian_roulette`, `$hardcore_roulette`, `$glock_roulette`, `$shadow`, `$highscores`

**Admin Commands:**
* `$reply ...` (Intensity, Status [target], Channel/User management)
* `$vocabulary [add|group]`
* `$schedule ...` (Message, Event-reminder, List, Remove)
