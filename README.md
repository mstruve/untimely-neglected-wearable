# A Simple [Battlesnake](http://play.battlesnake.com) Written in Python

This is a basic implementation of the [Battlesnake API](https://docs.battlesnake.com/references/api). 

It has code to:

- Avoid the edges of the map.
- Avoid collisions with other snakes on the board.

### Next steps

- Gathering food badly
- Avoiding traps (one way in, no way out)

### Technologies Used

* [Python3](https://www.python.org/)
* [CherryPy](https://cherrypy.org/)

## Customizing Your Battlesnake

Now you're ready to start customizing your Battlesnake's appearance and behavior.

### Changing Appearance

Locate the `index` function inside [server.py](server.py#L15). At the end of that function tou should see a line that looks like this:

```python
return {
    "apiversion": "1",
    "author": "",
    "color": "#888888",
    "head": "default",
    "tail": "default",
}
```

This function is called by the game engine periodically to make sure your Battlesnake is healthy, responding correctly, and to determine how your Battlesnake will appear on the game board. See [Battlesnake Personalization](https://docs.battlesnake.com/references/personalization) for how to customize your Battlesnake's appearance using these values.

Whenever you update these values, go to the page for your Battlesnake and select 'Refresh Metadata' from the option menu. This will update your Battlesnake to use your latest configuration and those changes should be reflected in the UI as well as any new games created.

### Changing Behavior

On every turn of each game your Battlesnake receives information about the game board and must decide its next move.

Locate the `move` function inside [server.py](server.py#L37). Possible moves are "up", "down", "left", or "right". To start your Battlesnake will choose a move randomly. Your goal as a developer is to read information sent to you about the board (available in the `data` variable) and decide where your Battlesnake should move next.

See the [Battlesnake Game Rules](https://docs.battlesnake.com/references/rules) for more information on playing the game, moving around the board, and improving your algorithm.

### Updating Your Battlesnake

After making changes to your Battlesnake, you can restart your Repl to have the change take effect (or in many cases your Repl will restart automatically).

Once the Repl has restarted you can [create a new game](https://play.battlesnake.com/account/games/create/) with your Battlesnake to watch your latest changes in action.

**At this point you should feel comfortable making changes to your code and starting new Battlesnake games to test those changes!**

### Resources

All documentation is available at [docs.battlesnake.com](https://docs.battlesnake.com), including detailed Guides, API References, and Tips.

You can also join the Battlesnake Developer Community on [Slack](https://play.battlesnake.com/slack) and [Discord](https://play.battlesnake.com/discord). We have a growing community of Battlesnake developers of all skill levels wanting to help everyone succeed and have fun with Battlesnake :)
