# Bitifier

## Description
A Bitcoin bot written in Python to do margin funding on Bitfinex and slow-motion trading on Kraken.com and Bitfinex.com.

## Todo
- [ ] rewrite API
  - [ ] rewrite BFXAPI
  - [ ] implement kraken API
- [ ] implement scheduler
  - [ ] implement funding module
    - [ ] move account code to module code
    - [ ] adapt to new API architecture
  - [ ] implement trading module
    - [ ] implement statistics polling
    - [ ] implement statistics analysis
    - [ ] implement trading based on statistics
