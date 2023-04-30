# sherp2.0

sherp2.0 is a discord bot that answers frequently asked questions for students at the University of Alberta. It is currently operable on the unofficial University of Alberta CS discord. Students contribute to the bots knowledge database by contributing to `commands.json`

## Running the bot locally

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
         2. Scroll down and check all options under Priviliedged Gateway Intents then save changes.
         3. Under OAuth2 select URL Generator and select bot from SCOPES.
         4. under bot permissions check the following:
             * Read Messages/View Channels
             * Send Messages
             * Embed Links
             * Attach files
    * Click on copy beside the generated URL and paste it into your browser's search bar. You will be prompted 
      by Discord to invite it to your server. Invite it to the server you created earlier.
2. Running the bot
   * Clone the repo and cd into the root directory
   * Create a .env file and add your bot token like this:
```python
BOT_TOKEN = 'MTEwMjMzNzc5ODQ1NzAxNjUyMw.GsbpKF.6Vocc_sXkDgXcH9Yv_Hhbayz6zhjc2FIgA4H9k'
```
   * install requirements using:
```python
pip install -r requirements.txt
```
   * run the bot using:
```
python .\bot.py
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.
