import logging
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes
from pya3 import *  # Ensure required functions are available
from Non_indices_2 import nonIndicesFunction  # Blocking function
import re
from difflib import get_close_matches

# Replace with your Telegram Bot Token
BOT_TOKEN = "7508697785:AAHzk6QrrKChUaN_KHdU8nDSSF6mWeDdx38"
BOT_TOKEN = "7970801467:AAEeWD5LmC-PBeYyMCzlEo7Ozj1Fj_jQTPI"
GROUP_CHAT_ID = '-4608251868'  # Replace with your group chat ID

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to handle messages asynchronously

def socket_open():  # Socket open callback function
        subscribe_flag = False
        global socket_opened
        socket_opened = True
        print('New Check Socket Opened')
        # Resubscribe the script when reconnecting the socket if subscribe_flag is True
        # if subscribe_flag:
        #     alice.subscribe(subscribe_list)


def feed_data(message):  # Socket feed data will receive in this callback function
        global LTP, subscribe_flag
        feed_message = json.loads(message)
        # print('New Check feed_message -',feed_message)
        if feed_message["t"] == "ck":
            subscribe_flag = True
        else:
            try:
                # if feed_message['tk'] == '2600':
                # if feed_message['tk'] == '26000':
                    LTP = feed_message['lp'] if 'lp' in feed_message else LTP  # If LTP in the response it will store in LTP variable 
                    LTP = int(LTP)
                    # LTP = feed_message.get('lp', LTP)  # If 'lp' in the response, it will store in LTP variable
                # elif feed_message['tk'] == str(ce_token):
                #     ce_LTP = float(feed_message['lp'])
                # elif feed_message['tk'] == str(pe_token):
                #     pe_LTP = float(feed_message['lp'])
            except Exception:
                pass

def subscribe_func(alice,subscribe_list, retry_sub_count):
        max_retries = 5
        retry_delay = 2  # seconds
        
        for attempt in range(retry_sub_count, max_retries):
            try:
                alice.subscribe(subscribe_list)
                return  # Exit if subscription is successful
            except Exception as e:
                print(f'subscription failed - {e} {datetime.now()}')
                sleep(retry_delay)
        print(f'Failed to subscribe after {max_retries} attempts.')
def get_nearest_symbol(df, symbol):
    all_symbols = df['Symbol'].dropna().unique().tolist()
    closest_match = get_close_matches(symbol.upper(), all_symbols, n=1, cutoff=0.7)
    
    if closest_match and closest_match[0] != symbol.upper():
        # user_input = input(f"Did you mean {closest_match[0]} instead of {symbol}? (Y/N): ")
        # if user_input.lower() == 'y':
        if True :
            return closest_match[0]
        # else:
        #     print("Operation aborted by user.")
        #     return None
    return symbol.upper()

def request_for_order_id(ele):
    try:
        return ele['NOrdNo']
    except KeyError as e:
        print(f"request order id error: {e}")
        return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    
    # Run nonIndicesFunction in the background without waiting
    asyncio.create_task(process_message(update, user_message,alice))
def parse_trade_message(message: str):
    lines = message.strip().split("\n")
    first_line = lines[0]
    
    buy_above = int(re.search(r'BUY ABOVE (\d+)', message).group(1))
    stoploss = int(re.search(r'STOPLOSS (\d+)', message).group(1))
    targets = re.findall(r'\d+', lines[-1])  # Extract all numbers from the TARGETS line
    target = int(targets[0])  # First target value
    
    return first_line, buy_above, stoploss, target
def get_trading_symbol(df, first_line):
    match = re.match(r'(\D+) (\d+) (PE|CE)(?: \((\w+) SERIES\))?', first_line, re.IGNORECASE)
    if not match:
        return None
    
    symbol, strike_price, option_type, series = match.groups()
    strike_price = float(strike_price)
    
    # Get the nearest symbol if exact match is not found
    nearest_symbol = get_nearest_symbol(df, symbol)
    if nearest_symbol is None:
        return None
    
    today = datetime.today()
    # filtered_df = df[df['Expiry Date'] >= today]
    # Filter the dataframe based on extracted values
    filtered_df = df[(df['Symbol'].str.upper() == nearest_symbol) &
                     (df['Strike Price'] == strike_price) &
                     (df['Option Type'].str.upper() == option_type.upper())]
    
    # Convert Expiry Date to datetime for sorting
    filtered_df['Expiry Date'] = pd.to_datetime(filtered_df['Expiry Date'])
    
    if series:
        # Filter for the given series month
        filtered_df = filtered_df[filtered_df['Trading Symbol'].str.contains(series[:3].upper(), case=False, na=False)]
    
    # Get the nearest expiry
    filtered_df = filtered_df.sort_values(by='Expiry Date')
    
    if not filtered_df.empty:
        return filtered_df.iloc[0]['Trading Symbol'],filtered_df.iloc[0]['Lot Size']
    return None
def request_for_order_history(alice, oid):
    try:
        for i in range(13):
            a = alice.get_order_history(oid)
            # print(a)
            if a:
                return a
            sleep(5)
        print('*****__unable to get order history')
        
        return None
    except Exception as e:
        l = f"request_for_order_history error: {e}"
        print(l)
        sleep(1)
        return request_for_order_history(alice, oid) 
    main(alice,instrument_name,buy_above,stoploss,target,lotsize)
async def nonIndicesFunction(alice,message,context: ContextTypes.DEFAULT_TYPE):
    file_path = "NFO.csv"
    df = pd.read_csv(file_path)
    first_line, buy_above, stoploss, target = parse_trade_message(message)
    Instrument_obj,lotsize = get_trading_symbol(df, first_line)
    global socket_opened,subscribe_flag,subscribe_list,LTP
    buy_above = float(buy_above)
    stoploss = float(stoploss)
    target = float(target)
    lotsize = int(lotsize)*2
    print(buy_above,stoploss,target)
    LTP = float(0)
    print(type(buy_above),type(LTP))
    socket_opened = False
    subscribe_flag = False
    subscribe_list = []
    unsubscribe_list = []
    # lotsize = lotsize * 2


    Instrument_obj = alice.get_instrument_by_symbol('NFO', Instrument_obj)
    subscribe_list = [Instrument_obj]
    retry_sub_count = 1
    print('starting websocket')

    try:
        alice.start_websocket(socket_open_callback=socket_open, subscription_callback=feed_data, run_in_background=True)
    except Exception as e:
        print(f'Pseudo Error - Socket-Error',e)

    while not socket_opened:
        pass
    print(subscribe_list)
    try:
        alice.subscribe(subscribe_list)
    except Exception as e :
         print('Error in sub - ',e)
    # SRF 2800 CE (MARCH SERIES)
    # BUY ABOVE 128
    # STOPLOSS 118
    # TARGETS 135 / 145 / 160



    # BUY ABOVE 128 - 
    # 1. check LTP and Buy above 128 only 
    second_check = True
    first_place  = True
    # end_time = datetime.now()
    # print('--------------------------',end_time-start_time)
    while True:
        if LTP != 0:
            print('Inside condition ltp -',LTP)    
            if float(LTP) > buy_above : # limit,intraday #buy order
                await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=LTP)
            if float(LTP) > buy_above : # limit,intraday #buy order
                await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=LTP)
            
        sleep(1)



                        
# Function to process messages in a separate async task
async def process_message(update: Update, user_message: str,alice) -> None:
    try:
        # Run the function in a separate thread so it doesn't block
        response = await asyncio.to_thread(nonIndicesFunction, alice,user_message)  
        await update.message.reply_text(response if response else "No response generated.")
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await update.message.reply_text("An error occurred while processing your request.")

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Bot is running! Send a message to process.")

def main(alice):
    # Initialize bot application
    app = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run bot in polling mode
    logger.info("Bot is starting...")
    app.run_polling()

if __name__ == "__main__":
    # user_id_assgn = '445378'
    # api_key_assgn = '0zCLVVJKCZHJN6MOrR4uvH7Hf3xMIsq06ySHzCr4X4FuuyF8dLKXV4R6FBVAYj9K4KpPpnRSudDyZrzXMvBEMPcUZZ3IuhAhThYJNBfakY6IQ1i8vgGlYkBjmqEdXzyD'


    user_id_assgn = '1680737'
    api_key_assgn ='S2jVBuakTjbkkmusbubKGoAhqBKRCpzvXmRNx9ekh9Vxal9nHpPWVRFNvSrNhzTQzPka6QHThU6qcXaEaj2zhyvXHnQAa7YCXYlcVqc0v319hOysal3DGSRCOfVWrCQc'
    global alice
    alice = 'a'
    alice = Aliceblue(user_id=user_id_assgn,api_key=api_key_assgn)
    alice.get_session_id()


    main(alice)
    
