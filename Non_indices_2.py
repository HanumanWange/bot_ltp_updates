# SRF 2800 CE (MARCH SERIES)
# BUY ABOVE 128
# STOPLOSS 118
# TARGETS 135 / 145 / 160

# SIEMENS 5200 CE

# BUY ABOVE 187

# STOPLOSS 170
import re
# TARGETS 200 / 220 / 240
from time import sleep
from pya3 import *
import time
from datetime import datetime
from difflib import get_close_matches
# start_time = datetime.now()
# print(start_time)
# alice = 'a'
# alice = Aliceblue(user_id='1680737',api_key='S2jVBuakTjbkkmusbubKGoAhqBKRCpzvXmRNx9ekh9Vxal9nHpPWVRFNvSrNhzTQzPka6QHThU6qcXaEaj2zhyvXHnQAa7YCXYlcVqc0v319hOysal3DGSRCOfVWrCQc')
# session_id = alice.get_session_id()
# alice.get_contract_master("BFO")
# exit()

# alice.get_contract_master("NFO")

# if session_id['userId'] == None:
#     print('Please login to the account')


# message = """
# MARUTI 11600 CE  

# BUY ABOVE 290  

# STOPLOSS 270  

# TARGETS 310 / 330 / 350
# """

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

def get_bnf_instrument(alice, NIFTY_BANK_IDX,retries):
        # NIFTY_BANK_IDX = "Nifty Bank"
        # NIFTY_BANK_IDX = "Nifty 50"
        try:
            instru = alice.get_instrument_by_symbol('BFO', NIFTY_BANK_IDX)
            return instru
        except Exception:
            if retries > 0:
                return get_bnf_instrument(alice,NIFTY_BANK_IDX, retries - 1)
            else:
                print("Failed to get Nifty Bank instrument after multiple attempts")

def request_for_order_id(ele):
    try:
        return ele['NOrdNo']
    except KeyError as e:
        print(f"request order id error: {e}")
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


def nonIndicesFunction(alice,message):
    
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
        # First Order placing for condition LTP > buy_above 
            if first_place:
                if second_check:
                    print("1-----first_place if condition",first_place,second_check)
                    if float(LTP) > buy_above : # limit,intraday #buy order
                        limit_order_indices = alice.place_order(transaction_type = TransactionType.Buy,
                                                    instrument = Instrument_obj,
                                                    quantity = lotsize,
                                                    order_type = OrderType.Limit,
                                                    product_type = ProductType.Intraday,
                                                    # ProductType1 = ProductType1.Intraday,
                                                    price = buy_above, #128+2
                                                    trigger_price = None, #128
                                                    stop_loss = None, #128-110 = 18
                                                    square_off = None, #140-128 = 12
                                                    trailing_sl = None,
                                                    is_amo = False,
                                                    order_tag='LTP > Buy Above')
                        # limit_order_indices_oid = limit_order_indices['NOrdNo']
                        # lmt_order_ind_his = alice.get_order_history(limit_order_indices_oid)
                        # print(lmt_order_ind_his['Status'])

                        limit_order_indices_oid = request_for_order_id(limit_order_indices)
                        # if limit_order_indices_oid == None:
                        
                        lmt_order_ind_his = request_for_order_history(alice, limit_order_indices_oid)
                        # print(limit_order_indices)
                        lmt_order_ind_status = lmt_order_ind_his['Status']
                        print('lmt_order_ind_status',lmt_order_ind_status)
                        first_place = False
                        # second_check = False
                        print(f'first_place {first_place}, second_check {second_check}')

            if first_place == False:
                if second_check:
                    print("1 check -----first_place",first_place,second_check)
                    lmt_order_ind_his = request_for_order_history(alice, limit_order_indices_oid)
                    lmt_order_ind_status = lmt_order_ind_his['Status']
                    # need to check
                    print("lmt_order_ind_status",lmt_order_ind_status)
                    if lmt_order_ind_status == 'complete' :
                        stop_loss_limit_for_sl =     alice.place_order(transaction_type = TransactionType.Sell,
                                        instrument = Instrument_obj,
                                        quantity = lotsize,
                                        order_type = OrderType.StopLossLimit,
                                        product_type = ProductType.Intraday,
                                        price = stoploss - 2 ,
                                        trigger_price = stoploss,
                                        stop_loss = stoploss,
                                        square_off = None,
                                        trailing_sl = None,
                                        is_amo = False,
                                        order_tag='order1')
                        limit_order_target =     alice.place_order(transaction_type = TransactionType.Sell,
                                        instrument = Instrument_obj,
                                        quantity = lotsize,
                                        order_type = OrderType.Limit,
                                        product_type = ProductType.Intraday,
                                        price = target ,
                                        trigger_price = None,
                                        stop_loss = stoploss,
                                        square_off = None,
                                        trailing_sl = None,
                                        is_amo = False,
                                        order_tag='order1')
                        # exit()
                        break
                    elif lmt_order_ind_status == 'cancelled' :
                        break 



            if second_check:
                 if first_place:
                    print("2-----second_check",first_place,second_check)
                    if float(LTP) < float(buy_above): # slm, intraday #buy order
                        limit_order_indices_2 = alice.place_order(transaction_type = TransactionType.Buy,
                                                    instrument = Instrument_obj,
                                                    quantity = int(lotsize),
                                                    order_type = OrderType.StopLossLimit,
                                                    product_type = ProductType.Intraday,
                                                    # ProductType1 = ProductType1.Intraday,
                                                    price = float(buy_above) + 2, #128+2
                                                    trigger_price = float(buy_above), #128
                                                    stop_loss = float(buy_above) - float(stoploss), #128-110 = 18
                                                    square_off = float(target)-float(buy_above), #140-128 = 12
                                                    trailing_sl = None,
                                                    is_amo = False,
                                                    order_tag='order1')
                        # limit_order_indices_oid_2 = limit_order_indices_2['NOrdNo']
                        # lmt_order_ind_his_2 = alice.get_order_history(limit_order_indices_oid_2)
                        # print(lmt_order_ind_his_2)
                        # print(lmt_order_ind_his_2['Status'])

                        limit_order_indices_oid_2 = request_for_order_id(limit_order_indices_2)
                        # if limit_order_indices_oid_2 == None:
                        #     exit()
                        lmt_order_ind_his_2 = request_for_order_history(alice, limit_order_indices_oid_2)
                        lmt_order_ind_status_2 = lmt_order_ind_his_2['Status']
                        print(lmt_order_ind_status_2)

                        second_check = False
            if second_check == False:
                print("2-----second_check",first_place,second_check)
                lmt_order_ind_his_2 = request_for_order_history(alice, limit_order_indices_oid_2)
                lmt_order_ind_status_2 = lmt_order_ind_his_2['Status']
                print("lmt_order_ind_status_2 2 ",lmt_order_ind_status_2)
                # print("2-----second_check",first_place,second_check)
                # trigger pending
                if lmt_order_ind_status_2 == 'complete':
                    stop_loss_limit_for_sl =     alice.place_order(transaction_type = TransactionType.Sell,
                                    instrument = Instrument_obj,
                                    quantity = lotsize,
                                    order_type = OrderType.StopLossLimit,
                                    product_type = ProductType.Intraday,
                                    price = stoploss - 2 ,
                                    trigger_price = stoploss,
                                    stop_loss = stoploss,
                                    square_off = None,
                                    trailing_sl = None,
                                    is_amo = False,
                                    order_tag='order1')
                    limit_order_target =     alice.place_order(transaction_type = TransactionType.Sell,
                                    instrument = Instrument_obj,
                                    quantity = lotsize,
                                    order_type = OrderType.Limit,
                                    product_type = ProductType.Intraday,
                                    price = target ,
                                    trigger_price = None,
                                    stop_loss = stoploss,
                                    square_off = None,
                                    trailing_sl = None,
                                    is_amo = False,
                                    order_tag='order1')
                    
                    # exit()
                    break
                elif lmt_order_ind_status_2 == 'cancelled':
                    break

        sleep(2)
    LTP = 0
    return 'Done'

file_path = "NFO.csv"
df = pd.read_csv(file_path)

def parse_trade_message(message: str):
    lines = message.strip().split("\n")
    first_line = lines[0]
    
    buy_above = int(re.search(r'BUY ABOVE (\d+)', message).group(1))
    stoploss = int(re.search(r'STOPLOSS (\d+)', message).group(1))
    targets = re.findall(r'\d+', lines[-1])  # Extract all numbers from the TARGETS line
    target = int(targets[0])  # First target value
    
    return first_line, buy_above, stoploss, target

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



# nonIndicesFunction(alice,message)
# print("First Line:", first_line)
# print("buy_above =", buy_above)
# print("stoploss =", stoploss)
# print("target =", target)
# print("Trading Symbol:", trading_symbol,lotsize)