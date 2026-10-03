-- More coins (Argy's scope change, 2026-10-03): 11 coins with years of Binance history.
-- The worker and the API read the active assets from this table, so no code lists coins.
insert into public.assets (symbol, name, exchange_symbol) values
  ('DOGE', 'Dogecoin',      'DOGEUSDT'),
  ('ADA',  'Cardano',       'ADAUSDT'),
  ('LINK', 'Chainlink',     'LINKUSDT'),
  ('AVAX', 'Avalanche',     'AVAXUSDT'),
  ('UNI',  'Uniswap',       'UNIUSDT'),
  ('NEAR', 'NEAR Protocol', 'NEARUSDT'),
  ('LTC',  'Litecoin',      'LTCUSDT'),
  ('TRX',  'TRON',          'TRXUSDT'),
  ('DOT',  'Polkadot',      'DOTUSDT'),
  ('BCH',  'Bitcoin Cash',  'BCHUSDT'),
  ('XLM',  'Stellar',       'XLMUSDT')
on conflict (symbol) do nothing;
