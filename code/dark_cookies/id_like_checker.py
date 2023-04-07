from dateutil.relativedelta import relativedelta
from datetime import datetime
from dateutil import parser
from zxcvbn import zxcvbn
from decimal import Decimal
import re
import logging
 
def is_zxcvbn_id(value):
    logging.debug("Cookie Value = "+str(value))
    base_ten_guesses = 0
    values = re.split(':|=|\.|%|\|',value)
    logging.debug("values = "+str(values))
    for v in values:
        if len(v) > 100:
            #logging.warning(f"Long: {v}")
            return True
        if v != "":
            results = zxcvbn(v)
            if 'guesses_log10' in results:
                base_ten_guesses = results['guesses_log10']
    logging.debug("guesses_log10 = "+str(base_ten_guesses))
    if base_ten_guesses > 9:
        return True
    else:
        return False
    
def is_id_cookie(collection_datetime, value, expiry):
    if is_zxcvbn_id(value) and is_long_expiry_cookie(collection_datetime, expiry):
        return True
    else:
        return False
    
def is_long_expiry_cookie(collection_datetime, cookietimestamp):
    try:
        logging.debug("cookietimestamp:"+str(cookietimestamp))
        cookietimestamp = Decimal(cookietimestamp)
        if cookietimestamp > 0:
            cookie_expiry_datetime = datetime.fromtimestamp(cookietimestamp)
        else:
            cookie_expiry_datetime = datetime.min
        logging.debug("Parsed cookie timestamp - cookie_expiry_datetime: "+str(cookie_expiry_datetime))
    except Exception as e:
        logging.error("Failed to parse cookietimestamp: "+str(e))
        cookie_expiry_datetime = datetime.min
    try:
        collection_datetime = parser.parse(collection_datetime)
        collection_plus_one_month_datetime = collection_datetime + relativedelta(months=1)
        logging.debug("Parsed cookie collection timestamp - collection_plus_one_month_datetime: "+str(collection_plus_one_month_datetime))
    except Exception as e:
        logging.error("Failed to parse cookie collection timestamp: "+str(e))
        collection_plus_one_month_datetime = datetime.max
    if cookie_expiry_datetime > collection_plus_one_month_datetime:
        return True
    else:
        return False