# ukraine_discord
A script that gets the news from liveuamap.com to post is on Discord as a webhook

# Live view
The bot is currently running and posting news right now as an example inside [my personal Discord server](https://discord.gg/AlexFlipnote), inside the channel `#general_whatever` within the thread called `Ukraine Vs Russia - Discussion and News`.

# Requirements
- Python 3.6 or higher
- Discord webhook URL

# Credits
- [Atomikkunn](https://github.com/Atomikkunn)
  - Figuring out how to check what category each posts are

## Config file
| Variable | Description |
| --- | --- |
| embed_image | Define if images should be shown in embed or not (Bool) |
| user_agent | Make custom User-Agent for requests |
| webhook_url | Discord webhook URL from your Discord |
| article_fetch_limit | How many articles it will go through to see if anything's new |
| debug | Debug mode, true/false |

## Example outputs
![](https://i.alexflipnote.dev/P1967aY.png)

![](https://i.alexflipnote.dev/4Ty6Yb3.png)
