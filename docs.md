 How to use?
 in file config.ini change token = to your telegram bot token it looks like 1234567890:AhgjHsk_ssD_psismjs98ks7ss
 users_count = * if you allow access to all telegram users if not users_count = 2 or that number which users you wnat to add
 After this if users_count = 2 add user0 = <user_telegram_id> without <> it looks like 506421571 and user1 = 506421534
 than add an admin like users, admin is required 
 create a user account in cloud.mongodb.com/
 Create a user in mongodb 
 And add to user = <user_you_create_in_mongodb> without <> and password = <password_for_mongo_user> without <>
 mongo_url = mongodb+srv://{0}:{1}@<cluster_url>/test?retryWrites=true&w=majority edit only <cluster_url> that will be given in your mongodb account
 Than 
 $pip install -r requirements.txt
 $python bot.py
 In another window if you t linux: $apt-get install ngrok
 If you at windows go to website ngrok.com/ and download ngrok in work directory
 $ngrok http 5000 
 Than in your browser api.telegram.org/bot<your_legram_bot_token>/setwebhook?url=https://someurl.com/ without<>
 And all your bot is working
