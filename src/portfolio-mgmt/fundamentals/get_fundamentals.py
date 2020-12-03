#!/usr/bin/env python3
from Collector import fetch_all_instruments, fetch_fundamental_data

if __name__ == "__main__":  
  instruments = fetch_all_instruments()
  fetch_fundamental_data(instruments)
