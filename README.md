# IG-Reel-Bot

## Define Environment Variables 
- INSTA_USERNAME = Your instagram username 
- INSTA_PASSWORD = Your Instagram password
- TELEGRAM_TOKEN= The bot token for the telegram bot that will be sending the messages
- INSTA_DM_ID= The url to the DM that will be recieving the instagram messages
- TELEGRAM_CHAT_ID= The telegram Id of the channel where the reels will be sent to

###
TO Use the Bot you will need 2 instagram accounts. 
- Account 1 will be the account sending the reels 
- Account 2 will be the account recieving the reels and that is what this script will be working with. 

Before running the script: 
- Use Instagram Web to open instagram.com
- Send a regular message from account 1 to acccount 2 
- The log into account 2 and ensure the message recieved from Account 1 is not in the requests section of Account 2's DM
- If it is, Click on the requests section and "Allow Account 2 to recieve messages from account 1."
- Once that is completed, Copy the URL that is displayed on the Address bar. That's the link to Account 1's DM
- It should look something like this. "https://www.instagram.com/direct/t/340282366841710300949128137536014401524"
- That is the link that you will pass as the INSTA_DM_ID environment Variable.

  INSTA_DM_ID=https://www.instagram.com/direct/t/340282366841710300949128137536014401524
  
### For the Telegram section
- Create a bot and get the token 
- Create a Public Telegram channel and add the Bot to that channel 
- Make the Bot an admin of that group and allow it to be able so send messages to the group.
- Once that is done Copy the id of the channel and pass it as an env variable
- It should look like this. '@testing_bot_12345'. 

  TELEGRAM_CHAT_ID='@testing_bot_12345'
 
Once The telgram and instagram requirements are met. You can not go ahead to prepare your ubuntu server for selenium 

## Before the script can be ran on the ubuntu server it is important to run the commands in this link --> [https://skolo.online/documents/webscrapping/#step-2-install-chromedriver] first 
