#!/usr/bin/env python3

# NOTE: This script requires the API nodes used to have the market history plugin enabled
#       to obtain the quoteSettlement_price. 
#  See https://github.com/xeroc/python-bitshares/issues/53#event-1530147512

from getpass import getpass
from bitshares.asset import Asset
from bitshares import BitShares
#from bitshares.block import Block #Uncomment if using blocknumber as reference timestamp.
from bitshares.instance import set_shared_bitshares_instance
from bitshares.price import Price
from bitshares.market import Market
from sys import exit
import os
import math
import time
import pprint
import logging
import pendulum

# Constants
HOME	= "/home/acccnt/"  # The local account this script runs under
WPW     = ""			   # ADD YOUR PASSWORD FOR SQLite WALLET HERE
KEY     = ""			   # ADD YOUR PRIVATE KEY FOR WITNESS TO PUBLISH
SQL	    = HOME + ".local/share/bitshares/bitshares.sqlite"
LOG	    = HOME + "hertz.log"
FMT     = ("%(asctime)s %(message)s", "%m/%d/%Y %H:%M:%S")
ACNT	= ""				# ADD YOUR WITNESS ACCOUNT NAME HERE
FREQ	= 17 * 60			# Calc & publish feed every 17 minutes
LEVEL	= logging.INFO		# Set logging.DEBUG for gobs of data
NODES	= [
    "wss://bts.proxyhosts.info/wss"    # Known to have history plugin enabled
#    "wss://bitshares.crypto.fans/ws",	#location: "Munich, Germany"
#    "wss://bit.btsabc.org/ws",		#location: "Hong Kong"
#    "wss://bitshares.apasia.tech/ws",	#location: "Bangkok, Thailand"
#    "wss://japan.bitshares.apasia.tech/ws", #location: "Tokyo, Japan"
#    "wss://api.bts.blckchnd.com"	#location: "Falkenstein, Germany"
#    "wss://openledger.hk/ws",		#location: "Hong Kong"
#    "wss://bitshares.dacplay.org/ws",	#location:  "Hangzhou, China"
#    "wss://bitshares-api.wancloud.io/ws", #location:  "China"
#    "wss://ws.gdex.top",		#location: "China"
#    "wss://dex.rnglab.org",		#location: "Netherlands"
#    "wss://dexnode.net/ws",		#location: "Dallas, USA"
#    "wss://kc-us-dex.xeldal.com/ws",	#location: "Kansas City, USA"
#    "wss://la.dexnode.net/ws",		#location: "Los Angeles, USA"
#    "wss://btsza.co.za:8091/ws",	#location: "Cape Town, South Africa"
    ]

API = BitShares(NODES, nobroadcast=False)
set_shared_bitshares_instance(API)
logging.basicConfig(filename=LOG, level=LEVEL, format=FMT[0], datefmt=FMT[1])


def get_hertz_feed(reference_timestamp, current_timestamp, period_days, phase_days, reference_asset_value, amplitude):
    """
    Given the reference timestamp, the current timestamp, the period (in days), the phase (in days), the reference asset value (ie 1.00) and the amplitude (> 0 && < 1), output the current hertz value.
    You can use this formula for an alternative HERTZ asset!
    Be aware though that extreme values for amplitude|period will create high volatility which could cause black swan events. BSIP 18 should help, but best tread carefully!
    """
    try:
        hz_reference_timestamp = pendulum.parse(reference_timestamp).timestamp() # Retrieving the Bitshares2.0 genesis block timestamp
        hz_period = pendulum.SECONDS_PER_DAY * period_days
        hz_phase = pendulum.SECONDS_PER_DAY * phase_days
        hz_waveform = math.sin(((((current_timestamp - (hz_reference_timestamp + hz_phase))/hz_period) % 1) * hz_period) * ((2*math.pi)/hz_perio$
        hz_value = reference_asset_value + ((amplitude * reference_asset_value) * hz_waveform)
    except:
        return -9897675453
    return hz_value


def publish_hertz_feed(api, witness):
    # Getting the value of USD in BTS
    try:
        market = Market("USD:BTS") # Set reference market to USD:BTS
        price = market.ticker()["quoteSettlement_price"] # Get Settlement price of USD
        price.invert() # Switching from quantity of BTS per USD to USD price of one BTS.

        #Hertz variables:
        #Change only for alternative Algorithm Based Assets.
        hertz_reference_timestamp = "2015-10-13T14:12:24+00:00" # Bitshares 2.0 genesis block timestamp
        hertz_current_timestamp = pendulum.now().timestamp() # Current timestamp for reference within the hertz script
        hertz_amplitude = 0.14 # 14% fluctuating the price feed $+-0.14 (2% per day)
        hertz_period_days = 28 # Aka wavelength, time for one full SIN wave cycle.
        hertz_phase_days = 0.908056 # Time offset from genesis till the first wednesday, to set wednesday as the primary Hz day.
        hertz_reference_asset_value = 1.00 # $1.00 USD, not much point changing as the ratio will be the same.

        # Calculate the current value of Hertz in USD
        hertz_value = get_hertz_feed(hertz_reference_timestamp, hertz_current_timestamp, hertz_period_days,
                                     hertz_phase_days, hertz_reference_asset_value, hertz_amplitude)
                                                                                                                            
        if not hertz_value == -9897675453:
            hertz = Price(hertz_value, "USD/HERTZ") # Limit the hertz_usd decimal places & convert from float.

            # Calculate HERTZ price in BTS (THIS IS WHAT YOU PUBLISH!)
            hertz_bts = price.as_base("BTS") * hertz.as_quote("HERTZ")

            hertz_core_exchange_rate = 0.80 # 20% offset, CER > Settlement!
            hertz_cer = hertz_bts * hertz_core_exchange_rate

            # Log a few outputs
            logging.info("Price of HERTZ in USD: {}".format(hertz))
            logging.info("Price of HERTZ in BTS: {}".format(hertz_bts))
            logging.info("Price of BTS in USD: {}".format(price))
            logging.info("Price of USD in BTS: {}".format(price.invert()))
            logging.info("\n")                                                                                                                              

            # Log and publish the price feed to the BTS DEX
            feed = pprint.pformat( api.publish_price_feed(
                "HERTZ",
                hertz_bts,
                cer=hertz_cer, # Setting in line with Wackou's price feed scripts
                mssr=110,
                mcr=200,
                account=witness)
                )
            # logging.info(feed)  # Uncomment to add raw data to log
        else:
            logging.info("Error in get_hertz_feed, skipping publish")
                                                                                                                            
    except Exception as inst:
        err = pprint.pformat(inst)          # __str__ allows args to be printed directly,
        logging.info(err + "Error in publish_hertz_feed, skipping publish")

                                 
# Get sensitive input such as password or private key from user.
# Won't exit until both inputs match.
def get_secret_input(prompt):
    secret = ""
    while not secret:
        print(prompt)
        in1 = getpass()    	# Only drawback is "Password:" prompt
        print("Enter it again to verify.")
        in2 = getpass()	
        if in1 == in2:
            secret = in1
            print("Now add it to the code to avoid future prompting.\n")
            return secret
        else: print("Your inputs don't match! Try again...")


# First time run - initialize / open the wallet
def open_wallet(credentials):
    pw     = credentials['WPW']
    api    = credentials['API']
    pKey   = credentials['KEY']
    wallet = credentials['SQL']

    # Get a wallet password from user if it isn't defined in Constants
    if not pw:
        pw = get_secret_input("Please enter your wallet password")
        credentials['WPW'] = pw

    if api.wallet.created():
        try:
            api.wallet.unlock(pw)
        except:
            print("A wallet exists but the password won't unlock it.")
            prompt= "Recreate the wallet with the password you entered (y/n)?"
            if input(prompt) == 'y':
                 print("Sorry, no way currently to remove old wallet state.")
                 print("You will need to manage the wallet externally.")
#                os.remove(wallet)
#                api.wallet.reset()
# Need to purge existing wallet state to allow a new one to be created here.
#                api.storage.MasterPassword.purge()
                 exit(-1) 	# Remove this when reCreation works
            else:
                print("Ok, sorry it didn't work out. Bye!")
                exit(-1)

    if not api.wallet.created():
        try:
            print("No wallet exists! Creating one now..")
            api.wallet.newWallet(pw)
            api.wallet.unlock(pw)
            prompt = "Please enter the private key for your witness"
            if not pKey:
                pKey = get_secret_input(prompt)
                credentials['KEY'] = pKey
            api.wallet.addPrivateKey(pKey)
        except:
            print("A problem occured opening the wallet.")
            exit(-2)

    return(credentials)

# ------------------------------ Main Loop --------------------------------- #

if __name__ == "__main__":

    # Open the wallet. Prompt for witness password and private key as required
    credentials = open_wallet( {'API':API,'WPW':WPW,'KEY':KEY,'SQL':SQL} )

    # Update the constants from user input for subsequent publishing
    WPW = credentials['WPW']
    KEY = credentials['KEY']

    # This loop continuously publishes the feed at the defined interval
    while (True):
        publish_hertz_feed(API, ACNT)
        time.sleep(FREQ)

