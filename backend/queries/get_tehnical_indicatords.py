import ta


def calculate_technical_indicators(df):
    indicators = {}

    try:
        df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()
        df['stoch'] = ta.momentum.StochasticOscillator(df['high'], df['low'], df['close']).stoch()
        df['stochrsi'] = ta.momentum.StochRSIIndicator(df['close']).stochrsi()
        df['macd'] = ta.trend.MACD(df['close']).macd()
        df['adx'] = ta.trend.ADXIndicator(df['high'], df['low'], df['close']).adx()
        df['williams_r'] = ta.momentum.WilliamsRIndicator(df['high'], df['low'], df['close']).williams_r()
        df['cci'] = ta.trend.CCIIndicator(df['high'], df['low'], df['close']).cci()
        df['atr'] = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close']).average_true_range()
        df['ult_osc'] = ta.momentum.UltimateOscillator(df['high'], df['low'], df['close']).ultimate_oscillator()
        df['roc'] = ta.momentum.ROCIndicator(df['close']).roc()
        df['bull_bear_power'] = df['close'] - ta.trend.EMAIndicator(df['close'], window=13).ema_indicator()

        indicators['rsi'] = df['rsi'].iloc[-1]
        indicators['stoch'] = df['stoch'].iloc[-1]
        indicators['stochrsi'] = df['stochrsi'].iloc[-1]
        indicators['macd'] = df['macd'].iloc[-1]
        indicators['adx'] = df['adx'].iloc[-1]
        indicators['williams_r'] = df['williams_r'].iloc[-1]
        indicators['cci'] = df['cci'].iloc[-1]
        indicators['atr'] = df['atr'].iloc[-1]
        indicators['ult_osc'] = df['ult_osc'].iloc[-1]
        indicators['roc'] = df['roc'].iloc[-1]
        indicators['bull_bear_power'] = df['bull_bear_power'].iloc[-1]
    except:
        indicators = {indicator: 0 for indicator in [
                'rsi', 'stoch', 'stochrsi', 'macd', 'adx', 'williams_r', 'cci', 'atr', 'ult_osc', 'roc', 'bull_bear_power'
            ]}

    return indicators
