# A Simple [Battlesnake](http://play.battlesnake.com) Written in Python

This is an implementation of the [Battlesnake API](https://docs.battlesnake.com/references/api). 

It is designed to be stateless - a decision is made based on the board state provided on request.

It has code to:

- Avoid the edges of the map.
- Avoid collisions with other snakes on the board.
- Avoid entering spaces too small to fit.
- Avoid hazard spaces unless it's the only spot for food
- Seek food when other snakes are larger, and avoid it if we're the largest.
- Blindly find food when very low in health.
- Take a certain winning move if the other snake has one available move
- Take a drafting larger snake to a wall, just to see what happens

### Next steps

- Improve hazard code to reduce time spent in hazards.
- Improve tail chasing code to chase enemy tails.
- Improve squeeze code to determine if an escape route would open due to a tail

### Possible refactoring

- Improve pathfinder code to use a multi-node tree
- Optimize to run on the Raspberry Pi

### Technologies Used

* [Python3](https://www.python.org/)
* [CherryPy](https://cherrypy.org/)

### Resources

Battlesnake documentation is available at [docs.battlesnake.com](https://docs.battlesnake.com), including detailed Guides, API References, and Tips.

You can also join the Battlesnake Developer Community on [Slack](https://play.battlesnake.com/slack) and [Discord](https://play.battlesnake.com/discord). We have a growing community of Battlesnake developers of all skill levels wanting to help everyone succeed and have fun with Battlesnake :)
