# sherp2.0

sherp2.0 is a discord bot that answers frequently asked questions for students at the University of Alberta. It is currently operable on the unofficial University of Alberta CS discord server. Students can contribute to the bots knowledge database by contributing to `data`

## Features
- [schedubuddy](https://schedubuddy.com/) integration (credit: @aarctan):
   - Create combinations of schedules based on user's choice of courses
   - View all classes you can enroll in at the same time given a classroom location
- Check course description and prerequisites (credit: @aarctan, @nathandrapeza and @steventango) [Course Data](https://github.com/steventango/synapse/blob/master/data/ualberta.ca.json)
- Request Kattis problems based on difficulty and other parameters (credit: @GurveerSohal)
- Slash Commands (credit: @DhanrajHira)
- Starboard (credit: @ArtDynasty13)
- Magic 8-ball
- Shortcuts to many well known facts
- Shortcuts to copypastas popular on the CS discord server

## Running the bot locally
**Note:** If all you want to do is add new commands then you dont need to setup the bot, You can just clone the repo and contribute to `data/commands.json` or any of the other files in `data` folder. For more advanced changes, it is recommended to get a discord bot running locally to test functionality.

Here are the steps you need to follow if you want to run the bot locally for testing purposes:

### Prerequisites:
1. A discord server that you can invite the bot to and do testing.
2. python3
3. pip

### Steps:
1. Create a discord bot for testing using the Discord Developer Portal https://discord.com/developers/applications
    * Click on "New Application" and provide a name for your bot (make sure you try to give it a unique name), then accept terms of service and click Create.
    * Once created, you will be redirected to the bot dashboard where you can configure its settings.
         1. Select the Bot section under settings, click on Reset Token, and save the token somewhere (you will need it later).
         2. You will also need the bots application ID. This can also be found in the developer dashboard under General Information.
         3. Scroll down and check all options under Privileged Gateway Intents then save changes.
         4. Under OAuth2 select URL Generator and select bot from SCOPES.
         5. under bot permissions check the following:
             * Read Messages/View Channels
             * Send Messages
             * Embed Links
             * Attach files
    * Click on copy beside the generated URL and paste it into your browser's search bar. You will be prompted 
      by Discord to invite it to your server. Invite it to the server you created earlier.
2. Running the bot
   * Clone the repo and cd into the root directory
   * Create a .env file and add your bot token and application ID like this:
```python
BOT_TOKEN = 'MTEwMjMzNzc5ODQ1NzAxNjUyMw.GsbpKF.6Vocc_sXkDgXcH9Yv_Hhbayz6zhjc2FIgA4H9k'
DISCORD_APP_ID = 1099815557760373847
```
   * install requirements using:
```python
pip install -r requirements.txt
```
   * run the bot using:
```
python .\bot.py
```
   * when running the bot for the first time, please run `?sync` in order for slash commands to work without issue

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.
