
import logging
import random
import sys
import inspect
import time
import requests
import os
from dotenv import load_dotenv

import arrow
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from telegram import Bot, Update
from telegram.ext import (CallbackContext, CallbackQueryHandler,
                          CommandHandler, ConversationHandler, Filters,
                          MessageHandler, TypeHandler, Updater)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')

bot = Bot(token=BOT_TOKEN)

chromeOptions = Options()
chromeOptions.add_argument("--headless")
chromeOptions.add_argument("--no-default-browser-check")
chromeOptions.add_argument("--no-first-run")
driver = uc.Chrome(options=chromeOptions)

connected_users = dict()
slot_status = {'timestamp': arrow.utcnow(), 'status': 'No data'}

def start(update: Update, context: CallbackContext) -> int:
    """Send message on /start."""
    # Get user that sent /start and log his name
    user = update.message.from_user
    logger.info("user is id: %s (username: %s) started the conversation." % (user.id, user.username))
    connected_users[str(user.id)] = user.id
    text = '''
        Hi! If there is any slot https://pieraksts.mfa.gov.lv/ru/moskva/index, I will let you know!

        Use /stop to stop updates.

        Use /slot to show current slot status.'''

    update.message.reply_text(inspect.cleandoc(text))
    return 1


def stop(update: Update, context: CallbackContext) -> int:
    """stoping updates"""
    user = update.message.from_user
    update.message.reply_text(
        f"You won't receive any updates anymore! Use /start to enable updates."
    )
    try:
        del connected_users[str(user.id)]
    except KeyError:
        pass
    return ConversationHandler.END


def slot(update: Update, context: CallbackContext) -> int:
    '''Showing timestamp of last check and status of slot'''
    text = f'''
        Timestamp: <b>{slot_status['timestamp'].shift(hours=+3).strftime('%A %d-%m-%Y, %H:%M:%S')} Moscow Time ({slot_status['timestamp'].humanize()})</b> 
        Status: <b>{slot_status['status']}</b>'''
    bot.sendMessage(chat_id=update.message.from_user.id, text=inspect.cleandoc(text), parse_mode='HTML')


def request(driver):  
    s = requests.Session()
    cookies = driver.get_cookies()
    for cookie in cookies:
            s.cookies.set(cookie['name'], cookie['value'])
    return s

def check_slot(context: CallbackContext):
    global slot_status
    bad_message = 'Šobrīd visi pieejamie laiki ir aizņemti' # meaning no slots
    while True:
        try:
            with driver:
                req = request(driver)
                response = req.get('https://pieraksts.mfa.gov.lv/ru/calendar/available-month-dates?year=2022&month=4')      
                message = response.json()
                logger.info(f'message: {message}')

                if 'status' in message:
                    if message['status'] == 404:
                
                        url = "https://pieraksts.mfa.gov.lv/ru/moskva/index"
                        driver.get(url)
                        logger.info(f'{driver.title} - {driver.current_url}')

                        elem = driver.find_element(By.ID, 'Persons[0][first_name]')
                        elem.send_keys('Pyotr' + Keys.TAB + 
                            'Kapitsa' + Keys.TAB + 
                            'pyotr_kapitsa@someunexistingdomain.com' + Keys.TAB + 
                            '+7555888555' + Keys.TAB + Keys.TAB + Keys.ENTER)
                        logger.info(f'name, email and phone has been entered.')
                        time.sleep(1)
                        
                        service_select = driver.find_element(By.CLASS_NAME, 'dropdown--wrapper')
                        service_select.click()
                        logger.info(f'clicked "{service_select.text}"')
                        time.sleep(1)
                        
                        checkbox_repatr = driver.find_element(By.CSS_SELECTOR, 'div.js-checkbox:nth-child(3)')
                        checkbox_repatr.click()
                        logger.info('clicked "Подача документов на вид на жительство по репатриации"')
                        time.sleep(1)

                        checkbox_confirmation = driver.find_element(By.CSS_SELECTOR, 'section.description:nth-child(4) > div:nth-child(2) > div:nth-child(7) > span:nth-child(2)')
                        checkbox_confirmation.click()
                        logger.info('agreed with terms of service.')
                        time.sleep(1)

                        submit_button = driver.find_element(By.CSS_SELECTOR, 'section.description:nth-child(4) > div:nth-child(2) > div:nth-child(8) > button:nth-child(1)')
                        submit_button.click()
                        logger.info('submit button pressed.')
                        time.sleep(1)

                        next_step_button = driver.find_element(By.CSS_SELECTOR, '.btn-next-step')
                        logger.info(f'clicked "{next_step_button.text}"')
                        next_step_button.click()

                else:          
                    # updating slot
                    slot_status = {'timestamp': arrow.utcnow(), 'status': message}

                    if message != bad_message:
                        # informing users of the bot
                        for user_id in connected_users:
                            bot.sendMessage(chat_id=user_id, text=f'Looks like need to check {url}, There is a slot on: {message}!')
                        
        except Exception as e:
            bot.sendMessage(chat_id=ADMIN_ID, text=f'Somethng went wrong: {e}')
            logger.error(f'Exception!: {e}')
        
        logger.info('waiting 50 sec and do stuff again.')
        time.sleep(50)


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your token and private key
    updater = Updater(BOT_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    j = updater.job_queue
    j.run_once(check_slot, when=1)

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("stop", stop))
    dispatcher.add_handler(CommandHandler("slot", slot))

    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
