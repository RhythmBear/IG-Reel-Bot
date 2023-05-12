from bot import InstaBot
import os

run_bot = InstaBot()
run_bot.login_to_instagram()
run_bot.interact_with_instagram(current_notif_count=0, dm_id=os.getenv('INSTA_DM_ID'))
