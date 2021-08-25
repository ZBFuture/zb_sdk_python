import zb

if __name__ == '__main__':
    account = zb.AccountApi()
    symbols = account.get_symbols()
    print(symbols[0].base_currency)


