# Mafia GM Tool #
A Program to allocate roles in a modded game of mafia & assist in running the game.

### Role Info
Simplified Role Sheet [Here](./Simplified-Role-Sheet.odp)
Detailed Role Descriptions: https://docs.google.com/document/d/1GgAKyC6A48pYSVx96a-Yz4girl6JzwH0_gW3UI0X_n0/edit?usp=sharing

### Running The Game

#### Before Starting The Program
To begin, you will require a means of distributing the roles secretly to players (i.e. printed cards) and a way to communicate text information to players.

If you intend to run a game for the same group of people for multiple rounds, it is recommended to create a `defualts.txt` file and listing the names of your players in it.

If you want to filter which roles you want to be in play, you can add a `JSON` file in the `Scripts` folder following the format of the other two files. Note that:
- Roles in nested lists cannot have duplicates.
- There is only ever 1 evil leader in play
- `overflow` stores a duplicatable role used to allow for a theoretically uncapped player size but is not recommended.
- The "max players" used to determine when overflow is used is automatically calculated on loading.
- The `evil_support` is used to determine at which player counts minions are added in.

### Setup Menu
Upon starting the program, you are greeted with the setup menu:

![An image of the stup menu](images\image.png)

You can either add players by typing their name into the textbox and use the `add` button or enter key to type it in or you can use the `defaults` button to load the contents of `defaults.txt`.

From there, you can use the `script` button to load any valid JSON file in the `Scripts` folder. By default, the `Everything.json` file is loaded.

To change what roles are in play, you can `randomise` them or click individual roles to cycle through the remaining options.

The `settings` button allows you to adjust some features in the game, such as a starting drunk and instant death gambler.

From there, you may press `quit` to terminate the program, press `Load Backup` if a game previously crashed or press `play` to confirm your choices and move on.

### Game Menu