# Bitifier

## Description
A Bitcoin bot written in Python to do margin funding on Bitfinex and (once I rewrote the trading part) trades on kraken. Although there exist other bots that do the same this is one has fairly minimal requirements.
This is a side project and I am no software developer so use with caution. I work on it while I can but can not make any guarantees that it will work and perform up to ones expectations. I have used it for a year know and it served its purpose very well - apart from the trading part.
The project was based on [MarginBot](https://github.com/HFenter/MarginBot) and follows roughly its lending strategy. However it has been adapted through the configuration and can be adapted through there.
So for your own sake try to understand the code. I will work on the documentation as well in the near future.

## Features

- Bitfinex Bitcoin lending
- Bitfinex USD lending
- *very* crude RSI based Kraken trading (currently working on better method)

## Dependencies

Python packages
Python 3.5 (might work on others but untested)
krakenex
Peewee (with SQLCipher playhouse extension)

## Todo

- [ ] create virtualenv && requirements.txt
- [ ] clean code
- [ ] rewrite API
  - [x] rewrite BFXAPI
  - [x] implement kraken API
- [ ] implement scheduler
  - [x] implement funding module
    - [ ] move account code to module code
    - [ ] adapt to new API architecture
  - [ ] implement trading module
    - [x] implement statistics polling
    - [x] implement statistics analysis
    - [ ] implement in-memory data pruning
    - [ ] implement trading based on statistics

## Disclaimer

This work is very raw, under development and there is a ton of dead code in there. I will eventually work on all these issues however I don'have the necessary time to put more effort in to it right now.
Updates follow as my work/life balance permits.

## Donations

If you find this software useful feel free to send a small donation my way.

Bitcoin Address:
3H9oa2bQJg2p9akaemUvcoQBMj1VociM2R

![BTC QR Code](btc_addr_qr.png "BTC Donation Address QR Code")
