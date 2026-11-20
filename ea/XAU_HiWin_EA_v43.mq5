//+------------------------------------------------------------------+
//|  XAU HiWin  v43                                      magic 20263253
//|  = v42 + scalper setup S4 + ENGINE T (H1 trend follower).
//|  Both were checked on Vantage M1 2024-2026 with the calibrated
//|  simulator, with several settings each, before going in.
//|
//|  1. InpUseS4 false -> true (M15 EMA50/200 trend + RSI<35 pullback)
//|     improves every year at RSI 30, 35 and 40. Fixed 0.01 lot:
//|        RF 18.6 -> 21.5, max DD unchanged.
//|
//|  2. ENGINE T - H1 Donchian trend follower (tag "T1", own budget)
//|     close of the last H1 candle above the highest high (below the
//|     lowest low) of the InpTrendN candles before it -> enter. Stop
//|     InpTrendSLatr x H1 ATR, then trailed InpTrendTrailATR x H1 ATR
//|     behind the best price, once per hour. No target, no clock.
//|     Size: InpTrendRiskPct of equity lost if the stop is hit.
//|     Profitable in 2024, 2025 and 2026 with all 12 settings tried,
//|     longs AND shorts. At 0.25% risk it adds money without adding
//|     drawdown.
//|
//|  $5,000 account, 2024-2026 (simulator):
//|                     v42          v43
//|     final        50,934       96,935
//|     max DD        13.0%        13.0%
//|     2024           +912       +1,309
//|     2025         +3,989       +6,088
//|     median month  +2.0%        +3.5%
//|     worst month   -3.3%        -4.1%
//+------------------------------------------------------------------+
//+------------------------------------------------------------------+
//|  XAU HiWin  v42                                      magic 20263252
//|  = v41 + ENGINE L (London breakout) + recovery group target 0.
//|
//|  Found with a simulator calibrated on Vantage M1 data 2024-2026:
//|  609 of 612 v41 tester trades reproduced, 606 with the same result,
//|  yearly profit within 5% of the tester.
//|
//|  1. InpRecoverTPATR 0.75 -> 0.0
//|     a rescued group now closes at its average entry instead of
//|     0.75 ATR beyond it. Fixed 0.01 lot, 2024-2026:
//|        net 1,798 -> 1,559   max DD 190 -> 126   RF 9.5 -> 12.4
//|     Lower drawdown in 2025 (135 -> 80) and 2026 (190 -> 126).
//|
//|  2. ENGINE L - London breakout (tag "L1", its own budget, 1 per day)
//|     Range = high/low of the M5 candles from InpLdnRangeStart to
//|     InpLdnRangeEnd server time (the Asian session). After that, the
//|     first M5 close outside the range is traded at market. Stop = one
//|     range width, target = InpLdnTPmult range widths, and whatever is
//|     still open at InpLdnCloseHour is closed. Fixed 0.01 lot:
//|                 2024        2025        2026
//|        net      +289        +394      +1,678    PF 1.26/1.20/1.67
//|     17 of 17 setting combinations were profitable in every year.
//|     Its shorts made more than its longs, so it is not just gold's
//|     bull market. Monthly correlation with the scalper: 0.35.
//|     Scalper + L at HALF lot (InpLdnLotMult 0.5), fixed 0.01:
//|        net 1,559 -> 2,740   DD 126 -> 144   RF 12.4 -> 19.0
//|        2024 +60 -> +205   2025 +367 -> +564   2026 +1,132 -> +1,971
//+------------------------------------------------------------------+
//+------------------------------------------------------------------+
//|  XAU HiWin  v41                                      magic 20263251
//|  = v40 with two changes, both checked on 2024, 2025 AND 2026.
//|
//|  v40 on 2024.01.01-2026.11.19 (Vantage, $5,000), per 0.01 lot:
//|                      2024        2025        2026
//|     scalper         +122        +335      +1,203   <- wins every year
//|     B1 breakout      -17        -127        +354   <- wins in 2026 only
//|
//|  1. InpAtrHardMinPct 0.12 -> 0.14
//|     scalper, ATR below 0.13% of price: 2024 +30, 2025 -90, 2026 +3
//|     scalper only, floor 0.12 -> 0.14:
//|          2024  +121 -> +94   (PF 4.9 -> 43, max DD 20 -> 2)
//|          2025  +335 -> +405  (PF 1.41 -> 2.23)
//|          2026 +1203 -> +1208 (PF 1.73 -> 2.46, max DD 204 -> 167)
//|     The 0.14 level was first seen on the 2026 v38 log; 2024 and 2025
//|     were never used to pick it and they agree.
//|
//|  2. InpUseBreakout true -> false
//|     B1 lost money in 2024 (PF 0.94) and 2025 (PF 0.74). Its edge is
//|     2026's violent gold, not a rule that keeps working. Over the
//|     three years it adds +12% net but +20% drawdown.
//|     Switch it back on to compare; it is unchanged.
//|
//|  Whole 3 years, per 0.01: v40 net 1,870 DD 239 RF 7.8 PF 1.49
//|                           v41 net 1,706 DD 167 RF 10.2 PF 2.47 (est.)
//+------------------------------------------------------------------+
//+------------------------------------------------------------------+
//|  XAU HiWin  DUAL-LEAN  v40                           magic 20263250
//|  = v39 with the two volatility floors measured in % OF PRICE
//|    instead of in dollars.
//|
//|  v39 on 2024.01.01-2026.11.19 (Vantage, $5,000):
//|        2024 : scalper 1 trade all year, B1 25 trades,  net    -39
//|        2025 : scalper 153 trades (83 of them Oct-Dec), net +1,886
//|        2026 : scalper 547 trades,                      net +24,070
//|  The bot did not lose in 2024 - it switched itself off. Gold was
//|  $2,000-2,700, so an M5 ATR of $5.5 (and B1's $5.0) almost never
//|  happened. Both floors were set on 2026 prices ($3,900-5,400).
//|  A dollar floor quietly becomes a much higher bar when the price is
//|  lower, so the EA only "works" at the price level it was built on.
//|
//|  v40: InpAtrHardMinPct  = 0.12  (= $5.5 at the 2026 median $4,590)
//|       InpBreakAtrMinPct = 0.11  (= $5.0 at the same price)
//|  On 2026 this should trade almost exactly like v39. On 2024-2025 it
//|  will trade a lot more, and NOTHING in it was tuned on those years,
//|  so that run is the first real out-of-sample test of the strategy.
//|  Set both to 0 to get v39 back exactly.
//+------------------------------------------------------------------+
//+------------------------------------------------------------------+
//|  XAU HiWin  DUAL-LEAN  v39                           magic 20263249
//|  = v38 + ONE measured change + two optional tools to measure next.
//|
//|  ============ WHAT THE v38 TRADE LOG SAYS (908 trades) ===========
//|  Every original scalp that never went 2 ATR against us WON:
//|        552 trades, 100% wins, +31,660
//|  Every scalp that went 2 ATR against us got a recovery leg. As
//|  GROUPS (original + leg together) those 135 trades made -18,661:
//|        87 groups reached the group target   +13,189
//|        34 groups hit the stop               -28,144
//|        14 groups hit the 4h time stop        -3,706
//|  The leg itself is NOT the loser (the legs alone made +4,952); the
//|  loss is the original trade that went wrong. That is why switching
//|  the legs off lost money three times.
//|
//|  ============ CHANGE 1 (on): ATR hard floor 5.0 -> 5.5 ===========
//|  Scalper groups by ATR at the signal, per 0.01 lot:
//|        ATR 5.0-5.5 : 146 trades  -52   PF 0.90  13 bad groups
//|        ATR >= 5.5  : 539 trades +1374  PF 1.96  35 bad groups
//|  The 5.0-5.5 band lost in BOTH halves of the year (Jan-May PF 0.92,
//|  Jun-Nov PF 0.91), so it is not one bad month. Fixed-lot proxy for
//|  the whole EA (scalper + B1): net +1,693 -> +1,738, max DD 246 ->
//|  177 (-28%), recovery factor 6.9 -> 9.8, active days 187 -> 171.
//|
//|  ============ CHANGE 2 (OFF): group stop after a recovery leg =====
//|  InpGroupStopATR > 0 moves the stop of the whole group to
//|  (leg price -/+ that many ATR) when the leg opens, if tighter than
//|  the original 5 ATR stop. Rescue success fell from 70% (Jan-May)
//|  to 53% (Jun-Nov); this is the lever for that, but it can only be
//|  judged on price paths. Test 1.5 / 2.0 / 2.5 in the tester.
//|
//|  ============ CHANGE 3 (on): per-trade CSV log ==================
//|  InpLogCsv writes Common\Files\HiWin_v39_trades*.csv (one file per
//|  tester run, stamped with the PC time): every closed
//|  position with its ATR at entry, max adverse / favorable excursion
//|  (in ATR) and the time of the worst point. With that file the group
//|  stop above can be tuned WITHOUT guessing.
//|
//|  Also fixed: the chart panel read atr[1] before data was loaded
//|  ("array out of range" stops the EA when algo trading is off at
//|  start-up).
//+------------------------------------------------------------------+
//+------------------------------------------------------------------+
//|  XAU HiWin  DUAL-LEAN  v38                           magic 20263248
//|  = v28 with the two levers that each worked, applied together:
//|        InpUseS3              true -> false   (v36)
//|        InpUseBase            true -> false   (v36)
//|        InpMaxPositions       5    -> 2       (v37)
//|        InpMaxTotalPositions  5    -> 0       (v37)
//|
//|  RUN v37 FIRST. This build is only meaningful once the position
//|  cap has been measured on its own.
//|
//|  ============ WHERE WE ARE, Vantage @ $5,000 ====================
//|                      v28        v36         v9
//|      net          +16,061    +10,089    +16,374
//|      profit f.       1.22       1.30       1.93
//|      max DD        29.92%     21.62%     16.76%
//|      recovery f.     1.97       2.85       4.74
//|      Sharpe          6.71       8.25      18.30
//|      equity line     0.89       0.95       0.99
//|      trades         1,599      1,025        507
//|      ACTIVE DAYS      196        186         99
//|      lots / year      229        103         74
//|
//|  v36 cleared both of its stated tests: profit factor above 1.22
//|  and recovery factor above 1.97. It also cut the drawdown by more
//|  than eight points and kept 186 of 196 trading days, so the daily
//|  income is intact. The money it lost is the RSI rule's own +2,837
//|  plus the compounding that rode on it.
//|
//|  The whole project turns out to be ONE curve: the fewer trades it
//|  takes, the better each one is and the less it hurts when wrong.
//|      1,599 trades -> PF 1.22 -> DD 30%
//|      1,025 trades -> PF 1.30 -> DD 22%
//|        507 trades -> PF 1.93 -> DD 17%
//|
//|  ============ WHY THE CAP STILL HAS SOMETHING TO GIVE ===========
//|  Inside v36 the same pattern is still there. Engine A, grouped by
//|  how many engine-A positions were already open:
//|          0 others : 471 trades  +10,251   PF 2.0
//|          1 other  : 237 trades     +863   PF 1.0
//|          2 others : 115 trades   -1,920   PF 1.0
//|          3 others :  76 trades   -1,254   PF 1.0
//|          4 others :  38 trades     -800   PF 1.0
//|      0-1 others : 708 trades  +11,114
//|      2+  others : 232 trades   -4,128
//|
//|  ============ HOW TO JUDGE IT ===================================
//|  Vantage XAUUSD+, M5, 2026.01.01-2026.11.18, $5,000, 1:100,
//|  every tick based on real ticks. Beat v36:
//|      v36 : +10,089, PF 1.30, maxDD 21.62%, RF 2.85, 1,025 trades
//|  PF and RF both higher, and the trade count must stay near 1,000.
//|
//|  ============ AND THEN THE TEST THAT MATTERS MOST ===============
//|  Everything above was found on ONE broker's data. Whatever wins
//|  here has to be run again on IFCMarkets before it is believed.
//|  v28 @ IFC $5,000 : +20,163, PF 1.30, maxDD 25.73%, RF 3.14
//|  If the winner's profit factor and drawdown improve on THAT data
//|  too, it is a real finding. If they do not, it was fitted to
//|  Vantage 2026 and v28 stands.
//+------------------------------------------------------------------+
//+------------------------------------------------------------------+
//|                                              XAU_HiWin_EA_v2.mq5 |
//|  High win-rate gold scalper (M5).                                |
//|  Built from a data search on 17 months of XAUUSD M5 history      |
//|  (train on the first 60%, tested on the last 40%).               |
//|                                                                  |
//|  Entry (checked once per new M5 candle, on the closed candle):   |
//|   - M15 trend: EMA20 vs EMA50 strict trend (same as XAU Max)     |
//|   - BUY  in an up-trend   when RSI(14) < 45 (pullback)           |
//|   - SELL in a down-trend  when RSI(14) > 55 (pullback)           |
//|   - spread must be small relative to ATR (spread/ATR < 0.07)     |
//|   - server hours 8..20 only                                      |
//|  Exit: small take profit (0.5 x ATR), wide stop (5 x ATR),       |
//|        time stop after 48 candles.                               |
//|  => ~90% of trades win, but a loss is about 6 wins big.          |
//|  v2 (loss reduction, tested on the same 17 months of M5 data):   |
//|   - time-decay stop (OFF by default): after N candles the stop   |
//|     tightens to 1.5 ATR; it reduced profit too much in testing   |
//|   - skip weak trends (M5 ADX < 15)                               |
//|   - skip volatility spikes (ATR > 1.5 x its 50-candle average)   |
//|  Test on DEMO first. Needs M5 (the EA reads M5/M15 itself).      |
//+------------------------------------------------------------------+
#property copyright "XAU HiWin"
#property version   "43.00"
#property description "XAU HiWin v43: scalper (S1,S4,S5) + London breakout + H1 trend engine. magic 20263253."

#include <Trade\Trade.mqh>

enum ENUM_HW_MODE
{
   HW_AUTO   = 0,  // Auto trade
   HW_NOTIFY = 1   // Signals only (no orders)
};

//=== Mode & safety ==================================================
/*
   XAU HiWin v9.0 = v3.0 plus the three things worth taking from "The Gold Space",
   a commercial EA tested on the same symbol, period, broker and $1000 deposit.

   What that EA did, for the record (fixed 0.01 lot, no compounding):
     net +1005, PF 2.63, max drawdown 4.69%, recovery factor 18.65,
     largest single loss -17.88, 645 trades, no losing month in 11.
   Its design is the opposite of ours: pending stop orders, a FIXED $2.50 stop,
   a trailing exit, and trades that last under a minute. Its average win (3.72)
   is bigger than its average loss (2.94); ours is the other way round.

   What is copied here, and why only these three:

   1. WIDER HOURS (they trade 0-21, we traded 8-20)
        hours 8-20  PF 2.99  net 1708   <- v3.0
        hours 7-21  PF 3.19  net 1882   <- taken
        hours 6-21  PF 2.92  net 1853
        hours 0-23  PF 1.63  net 1471   <- their full window hurts our style

   2. PENDING LIMIT ENTRY instead of a market order. We trade pullbacks, so
      waiting for a better price pays. Simulated with same-bar fills excluded:
        market entry            PF 1.72  net  962
        limit 0.3 ATR, 6 bars   PF 2.25  net 1084   <- taken
      If the limit is not filled within InpLimitWaitBars candles it is deleted.

   3. HOLIDAY FILTER - thin liquidity days, cheap insurance.

   NOT copied: their tight fixed stop and trailing exit. We tested that shape five
   times on this strategy (v2, v2.7, v4.0, v5.0, Manus settings) and it cost
   between 24% and 86% of the profit every time. A tight stop works with their
   one-minute breakout entries, not with a pullback that needs hours to resolve.

   Set InpUseLimitEntry=false and hours back to 8/20 to get exactly v3.0.
*/

input group "Mode and Safety"
input ENUM_HW_MODE InpMode      = HW_AUTO;    // Mode
input bool   InpAllowLive       = false;      // Allow auto trading on a REAL account
input long   InpMagic           = 20263253;   // Magic number (v43 - its own)
input int    InpSlippage        = 30;         // Slippage tolerance (points)
input bool   InpPush            = true;       // Push notifications to phone
input bool   InpPopup           = true;       // Popup alerts
input int    InpHeartbeatMin    = 60;         // "I am alive" message every N minutes (0=off)
input int    InpHourShift       = 0;          // v42.2: hours this broker's clock is AHEAD of Vantage (IFCMarkets = -1). All hour settings stay in Vantage time

//=== Strategy (values from the data search) =========================
input group "Strategy"
input int    InpTrendFast       = 20;         // M15 trend EMA fast
input int    InpTrendSlow       = 50;         // M15 trend EMA slow
input int    InpRsiPeriod       = 14;         // RSI period (M5)
input double InpRsiBuyBelow     = 45.0;       // Buy in up-trend when RSI below
input double InpRsiSellAbove    = 55.0;       // Sell in down-trend when RSI above
input int    InpAtrPeriod       = 14;         // ATR period (M5)
input double InpTPatr           = 0.5;        // Take profit = ATR x   (0.3 = ~94% wins, 0.8 = ~84%)
input double InpSLatr           = 5.0;        // Stop loss   = ATR x
input int    InpTimeStopBars    = 48;         // Close the trade after N M5 candles
input double InpMaxSpreadATR    = 0.10;       // Skip if spread / ATR is above this
input int    InpStartHour       = 7;          // First server hour to trade (v9.0: was 8)
input int    InpEndHour         = 21;         // Last server hour to trade (v9.0: was 20)
input bool   InpUseLimitEntry  = true;       // v9.0: enter with a pending limit at a better price instead of at market
input double InpLimitATR       = 0.3;        // ...this many ATR better than the signal close
input int    InpLimitWaitBars  = 3;          // ...delete the pending order if it is not filled within N candles
input string InpHolidayDates   = "2026.12.24,2026.12.25,2026.12.26,2026.12.31,2027.01.01";  // v9.0: no trading on these days
//=== v11.0: five entry setups instead of one ========================
//--- Measured on 17 months, fixed lot, max 2 open, same exits (train 60% / test 40%):
//---   S1 M15 trend + Bollinger touch   592 trades  PF 3.32   +2016   test PF 3.62
//---   S2 H1 trend + RSI<35 deep        438 trades  PF 2.95   +1373   test PF 2.31
//---   S3 M15 trend + RSI<40            520 trades  PF 2.07   +1317   test PF 3.43
//---   S4 M15 50/200 trend + RSI<35     544 trades  PF 2.28   +1512   test PF 2.17
//---   S5 M15 trend + 12-bar low + cloud 552 trades PF 3.06   +1894   test PF 2.13
//--- All five together roughly double the money of the best single one, but the
//--- drawdown grows about four times. They are not five independent edges:
//--- S1 and S5 overlap 40%, S2 and S4 overlap 76%.
input group "Entry setups (v11.0)"
input bool   InpUseS1          = true;       // S1: M15 trend + Bollinger touch + ADX  (best out-of-sample)
input bool   InpUseS2          = false;      // S2: H1 trend + deep RSI pullback
input bool   InpUseS3          = false;       // S3: M15 trend + RSI 40/60
input bool   InpUseS4          = true;       // S4: M15 50/200 trend + deep RSI (v43: ON - better in 2024, 2025 and 2026)
input bool   InpUseS5          = true;       // S5: M15 trend + 12-bar extreme + Ichimoku cloud
input bool   InpUseBase        = false;       // S0: the original v3.0 RSI 45/55 pullback
input int    InpBBPeriod       = 20;         // S1: Bollinger period (M5)
input double InpBBDev          = 2.0;        // S1: Bollinger deviations
input double InpS2Rsi          = 35.0;       // S2/S4: deep RSI level (buy below, sell above 100-this)
input double InpS3Rsi          = 45.0;       // S3: RSI level
input int    InpExtremeBars    = 12;         // S5: look-back candles for the extreme

//=== ENGINE B - the breakout rider (v28) ===========================
//--- The scalper (engine A) lives on small moves and REFUSES a volatility
//--- spike, because a spike is where its 0.5 ATR target gets run over. On
//--- 2026-11-19 gold fell 75 dollars in two hours and engine A sat it out,
//--- correctly by its own rules and uselessly by any other measure.
//--- Engine B is the opposite bet on the same chart: it waits for exactly
//--- the expansion engine A rejects, enters in the direction of the break,
//--- risks little and rides. Its trades are tagged B1 and it has its own
//--- position budget, so the two engines never crowd each other out.
input group "Engine B: breakout rider"
input bool   InpUseBreakout     = false;      // v28: run the breakout engine (v41: OFF - lost in 2024 and 2025)
input int    InpBreakLookback   = 20;         // the high/low of this many M5 candles must be broken
input double InpBreakSpikeMin   = 1.8;        // ATR must be at least this many x its own 50-candle average
input double InpBreakAtrMin     = 5.0;        // and never below this in absolute terms (only used when InpBreakAtrMinPct = 0)
input double InpBreakAtrMinPct  = 0.11;       // v40: ...or below this % of the price (0.11% = $5.0 at $4,590). 0 = use the dollar value
input double InpBreakSLatr      = 1.5;        // stop, in ATR
input double InpBreakTPatr      = 6.0;        // hard target, in ATR (the trail usually gets there first)
input double InpBreakTrailStart = 1.5;        // start trailing once the trade is this many ATR in profit
input double InpBreakTrailATR   = 1.5;        // trail this far behind price, in ATR
input int    InpBreakMaxPos     = 2;          // its own budget, separate from the scalper's
input double InpBreakLotMult    = 1.0;        // lot weight relative to the normal sizing rule
input int    InpBreakCooldown   = 12;         // no second breakout entry for this many M5 candles

//=== ENGINE L - London breakout (v42) ================================
input group "Engine L: London breakout (v42)"
input bool   InpUseLondon       = true;       // run the London breakout engine
input int    InpLdnRangeStart   = 3;          // range from this server hour...
input int    InpLdnRangeEnd     = 9;          // ...up to (not including) this server hour
input int    InpLdnCloseHour    = 21;         // close whatever is still open at this server hour
input double InpLdnTPmult       = 1.0;        // target = this many range widths (stop = one range width)
input double InpLdnLotMult      = 0.5;        // lot = normal sizing rule x this

//=== ENGINE T - H1 trend follower (v43) ==============================
input group "Engine T: H1 trend follower (v43)"
input bool   InpUseTrend        = true;       // run the trend engine
input int    InpTrendN          = 55;         // break of the highest high / lowest low of this many H1 candles
input double InpTrendSLatr      = 3.0;        // first stop, in H1 ATR(14)
input double InpTrendTrailATR   = 4.0;        // trailing distance behind the best price, in H1 ATR, moved once per hour
input double InpTrendRiskPct    = 0.25;       // % of equity lost if the first stop is hit

input string InpBlockHours      = "";         // server hours with no new entries (empty = none; the 12,15,16,20 idea was noise in the larger simulation)

//=== v2: loss reduction =============================================
input group "Loss reduction (v2)"
input int    InpDecayBars       = 0;          // After this many M5 candles the stop is tightened (0 = OFF; in your Strategy Tester run, 12 cut the profit too much)
input double InpDecayATR        = 1.5;        // ...to this many ATR from the entry (closed at once if already beyond)
input int    InpAdxPeriod       = 14;         // ADX period (M5)
input double InpAdxMin          = 12.0;       // Skip entries when M5 ADX is below this (0 = off)
input int    InpRangeBars       = 12;         // v2.3: look-back candles for the range filter (0 = off)
input double InpRangeMinATR     = 2.0;       // v2.3: skip when (range of last candles / ATR) is below this = dead market
input double InpAtrMin          = 6.3;        // v2.3: fixed volatility floor, ONLY used when InpAtrMinMode = 0
//--- v10.0: the fixed 6.3 floor was fitted on Jan-Mar 2026, when the median ATR at entry was 8.6-9.3.
//--- By October 2026 the median had fallen to 6.6 and the EA took 3 trades in seven weeks.
//--- Mode 1 compares ATR with its OWN recent history instead of with a number, so the floor
//--- follows the market instead of staying where last spring left it.
input int    InpAtrMinMode      = 1;          // 0 = fixed InpAtrMin ; 1 = adaptive percentile (v10.0)
input int    InpAtrLookback     = 576;        // adaptive: candles used for the ATR history (576 M5 = 2 trading days)
input double InpAtrPctile       = 20.0;       // adaptive: ATR must be above this percentile of that history
input double InpAtrHardMin      = 5.5;        // adaptive: never trade below this ATR (dollars; only used when InpAtrHardMinPct = 0)
input double InpAtrHardMinPct   = 0.14;       // never trade below this ATR as % of price (v41: 0.12 -> 0.14, better in 2024, 2025 and 2026). 0 = use the dollar value
input double InpSpikeMult       = 1.5;        // Skip entries when ATR is above this x its 50-candle average (0 = off)

//=== Risk ===========================================================
input group "Risk"
input double InpRiskPct         = 0.0;        // Risk per trade (% of equity, to the stop)
input double InpFixedLot        = 0.0;        // Fixed lot (0 = use risk %)
input double InpLotPer1000     = 0.01;        // v2.6: lot per 1000 of equity, grows with the account (0 = off). WARNING: 0.05 wiped the test account in Feb 2026
input group "Recovery add (v2.8)"
input double InpRecoverAtATR    = 2.0;        // If a trade moves this many ATR AGAINST you, add ONE more same-direction trade (0 = off)
input double InpRecoverTPATR    = 0.0;        // Both trades then close together at (average entry + this many ATR) (v42: 0.75 -> 0, drawdown -34%)
input double InpRecoverLotMult  = 1.0;        // Lot of the recovery trade = original lot x this
input double InpMaxLot          = 5.0;        // Max lot
input double InpMaxMarginPct    = 30.0;       // Max margin per trade (% of free margin)
input double InpMaxLossAtMinLot = 5.0;        // Skip if min-lot loss exceeds this % of equity
input int    InpMaxPositions    = 2;          // Max open positions together (tester: 3rd stacked trade lost money)
input bool   InpFridayFilter    = true;       // No new trades late on Friday
input int    InpFridayStopHour  = 20;         // Friday stop hour (server time)

input group "Break-even lock (v2.7 - OFF by default)"
input double InpBeTriggerATR     = 0.0;       // Once price moves this many ATR in profit, pull the stop up (0 = OFF; 0.3 cut profit 24% in the tester)
input double InpBeLockATR        = 0.1;       // ...to entry + this many ATR. Only used when the trigger is above 0

input group "Account protection (v2.9)"
input double InpMaxOpenRiskPct   = 20.0;      // Hard cap: total loss if EVERYTHING open hits its stop, as % of equity (0 = off)
input double InpDailyLossPct     = 10.0;      // Stop trading for the rest of the day after losing this % of the day's starting balance (0 = off)
input double InpEmergencyFloatPct= 25.0;      // Panic button: close every position if floating loss exceeds this % of equity (0 = off)
input int    InpMaxTotalPositions = 0;        // v13: hard cap on OPEN POSITIONS INCLUDING recovery legs (0 = off)
input int    InpMaxRecoveryLegs  = 1;         // Max recovery adds per original trade (1 is tested; 2 raises both profit and tail risk)
input bool   InpRecoverSpikeGuard= true;      // Never add a recovery leg during a volatility spike (ATR > InpSpikeMult x average)
input bool   InpRecoverHoursOnly = true;      // Never add a recovery leg outside trading hours / after the Friday stop
input double InpGroupStopATR     = 0.0;       // v39: when a recovery leg opens, stop the whole group this many ATR beyond the leg price (0 = OFF, keep the original 5 ATR stop)

input group "Diagnostics (v39)"
input bool   InpLogCsv           = true;      // Write every closed position to Common\Files\HiWin_v43_trades_<time>.csv (ATR, MAE, MFE), one file per tester run

//=== globals ========================================================
CTrade   trade;
int      hAtrH1 = INVALID_HANDLE;                 // v43: engine T
datetime gTrendBar = 0;                          // v43
int      hRsi = INVALID_HANDLE, hAtr = INVALID_HANDLE, hTrF = INVALID_HANDLE, hTrS = INVALID_HANDLE, hAdx = INVALID_HANDLE;
double   rsi[], atr[], trF[], trS[], adx[];
int      hBB = INVALID_HANDLE, hT2F = INVALID_HANDLE, hT2S = INVALID_HANDLE,
         hH1F = INVALID_HANDLE, hH1S = INVALID_HANDLE, hIch = INVALID_HANDLE;   // v11.0
double   bbU[], bbL[], t2F[], t2S[], h1F[], h1S[], spA[], spB[];                // v11.0
double   atrL[];                                  // v10.0: ATR history for the adaptive floor
double   gAtrFloor = 0;                           // v10.0: the floor actually used on this candle
string   BlockReport();                           // v10.0: forward declaration
int      CountAllPositions();                     // v13: forward declaration
//--- v10.0 diagnostics: which filter is actually stopping the EA. Printed when the EA is removed
//--- and shown live on the chart panel, so a silent EA can be explained instead of guessed at.
long     gSignals = 0, gEntries = 0;
long     gBreakEntries = 0, gBreakTrails = 0;        // v28
datetime gLastBreak = 0;                             // v28
long     gBlkHours = 0, gBlkMaxPos = 0, gBlkAdx = 0, gBlkSpike = 0, gBlkAtr = 0, gBlkRange = 0, gBlkSpread = 0;
datetime lastBar = 0, lastBeat = 0;
ENUM_HW_MODE gMode = HW_AUTO;
string   gStatus = "Starting";
datetime gDay = 0;
double   gDayStart = 0;
bool     gDayLocked = false;

//+------------------------------------------------------------------+
void Alarm(string msg)
{
   Print("HiWin: ", msg);
   if(InpPopup) Alert("HiWin: ", msg);
   if(InpPush)  SendNotification("HiWin " + msg);
}
//+------------------------------------------------------------------+
int OnInit()
{
   gMode = InpMode;
   if(AccountInfoInteger(ACCOUNT_TRADE_MODE) == ACCOUNT_TRADE_MODE_REAL &&
      !InpAllowLive && gMode == HW_AUTO)
   {
      gMode = HW_NOTIFY;
      Print("HiWin: REAL account and InpAllowLive=false -> signals only, no orders.");
   }

   hRsi = iRSI(_Symbol, PERIOD_M5, InpRsiPeriod, PRICE_CLOSE);
   hAtr = iATR(_Symbol, PERIOD_M5, InpAtrPeriod);
   hTrF = iMA(_Symbol, PERIOD_M15, InpTrendFast, 0, MODE_EMA, PRICE_CLOSE);
   hTrS = iMA(_Symbol, PERIOD_M15, InpTrendSlow, 0, MODE_EMA, PRICE_CLOSE);
   hAdx = iADX(_Symbol, PERIOD_M5, InpAdxPeriod);
   if(InpUseTrend) hAtrH1 = iATR(_Symbol, PERIOD_H1, 14);   // v43
   if(InpUseS1) hBB  = iBands(_Symbol, PERIOD_M5, InpBBPeriod, 0, InpBBDev, PRICE_CLOSE);
   if(InpUseS4) { hT2F = iMA(_Symbol, PERIOD_M15, 50,  0, MODE_EMA, PRICE_CLOSE);
                  hT2S = iMA(_Symbol, PERIOD_M15, 200, 0, MODE_EMA, PRICE_CLOSE); }
   if(InpUseS2) { hH1F = iMA(_Symbol, PERIOD_H1, 20, 0, MODE_EMA, PRICE_CLOSE);
                  hH1S = iMA(_Symbol, PERIOD_H1, 50, 0, MODE_EMA, PRICE_CLOSE); }
   if(InpUseS5) hIch = iIchimoku(_Symbol, PERIOD_M5, 9, 26, 52);
   ArraySetAsSeries(bbU,true); ArraySetAsSeries(bbL,true);
   ArraySetAsSeries(t2F,true); ArraySetAsSeries(t2S,true);
   ArraySetAsSeries(h1F,true); ArraySetAsSeries(h1S,true);
   ArraySetAsSeries(spA,true); ArraySetAsSeries(spB,true);
   if(hRsi == INVALID_HANDLE || hAtr == INVALID_HANDLE || hTrF == INVALID_HANDLE || hTrS == INVALID_HANDLE || hAdx == INVALID_HANDLE)
   {
      Print("HiWin: failed to create indicator handles");
      return INIT_FAILED;
   }
   ArraySetAsSeries(rsi, true);
   ArraySetAsSeries(atr, true);
   ArraySetAsSeries(trF, true);
   ArraySetAsSeries(trS, true);
   ArraySetAsSeries(adx, true);
   ArraySetAsSeries(atrL, true);

   trade.SetExpertMagicNumber(InpMagic);
   trade.SetDeviationInPoints(InpSlippage);
   trade.SetTypeFillingBySymbol(_Symbol);

   if(Period() != PERIOD_M5)
      Print("HiWin: attach to an M5 chart (new-candle timing is taken from the chart).");

   CsvStart();   // v39
   Alarm(StringFormat("STARTED on %s | mode %s", _Symbol, gMode == HW_AUTO ? "AUTO" : "SIGNALS ONLY"));
   return INIT_SUCCEEDED;
}
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   Print("HiWin v43 filter report | ", BlockReport());
   if(hRsi != INVALID_HANDLE) IndicatorRelease(hRsi);
   if(hAtr != INVALID_HANDLE) IndicatorRelease(hAtr);
   if(hTrF != INVALID_HANDLE) IndicatorRelease(hTrF);
   if(hTrS != INVALID_HANDLE) IndicatorRelease(hTrS);
   if(hAdx != INVALID_HANDLE) IndicatorRelease(hAdx);
   if(hAtrH1 != INVALID_HANDLE) IndicatorRelease(hAtrH1);
   Comment("");
   Alarm("STOPPED (reason " + IntegerToString(reason) + ")");
}
//+------------------------------------------------------------------+
bool HourBlocked(int h)
{
   string parts[];
   int n = StringSplit(InpBlockHours, ',', parts);
   for(int i = 0; i < n; i++)
   {
      StringTrimLeft(parts[i]); StringTrimRight(parts[i]);
      if(parts[i] != "" && (int)StringToInteger(parts[i]) == h) return true;
   }
   return false;
}

string GVK(string k) { return "HW29_" + _Symbol + "_" + (string)InpMagic + "_" + k; }

//--- v42.2: broker time -> Vantage server time, so every hour setting means the same
//--- moment of the trading day on any broker (set InpHourShift once, nothing else)
datetime VT(datetime t) { return (datetime)((long)t - (long)InpHourShift * 3600); }

//+------------------------------------------------------------------+
//| v39: the ATR a scalp was opened with. Until v38 it was always     |
//| recomputed as |open - SL| / InpSLatr, which is only true while    |
//| the stop has never moved. The group stop moves it, so the value   |
//| is remembered (terminal global variable) the first time it is     |
//| read, while the stop is still the original one.                   |
//+------------------------------------------------------------------+
double EntryATR(ulong tk, double op, double sl)
{
   string k = GVK("A" + (string)tk);
   if(GlobalVariableCheck(k)) return GlobalVariableGet(k);
   if(sl <= 0 || InpSLatr <= 0) return 0;
   double a = MathAbs(op - sl) / InpSLatr;
   GlobalVariableSet(k, a);
   return a;
}

//+------------------------------------------------------------------+
//| v39: per-position excursion tracker for the CSV log.              |
//+------------------------------------------------------------------+
struct TrkRec
{
   ulong    tk;
   string   tag;
   bool     buy;
   datetime topen;
   double   op;
   double   atr;
   double   mae;     // worst adverse move, price units
   double   mfe;     // best favourable move, price units
   datetime tmae;
};
TrkRec   gTrk[];
string   gCsvName = "HiWin_v43_trades.csv";
string   CsvName() { return gCsvName; }
bool     CsvOn()   { return InpLogCsv && !MQLInfoInteger(MQL_OPTIMIZATION); }

int TrkFind(ulong tk)
{
   for(int i = ArraySize(gTrk) - 1; i >= 0; i--) if(gTrk[i].tk == tk) return i;
   return -1;
}

void TrackPositions()
{
   if(!CsvOn()) return;
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   if(bid <= 0 || ask <= 0) return;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong tk = PositionGetTicket(i);
      if(tk == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
      if(PositionGetInteger(POSITION_MAGIC) != InpMagic) continue;
      int j = TrkFind(tk);
      if(j < 0)
      {
         j = ArraySize(gTrk);
         ArrayResize(gTrk, j + 1);
         gTrk[j].tk    = tk;
         gTrk[j].tag   = PositionGetString(POSITION_COMMENT);
         gTrk[j].buy   = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY);
         gTrk[j].topen = (datetime)PositionGetInteger(POSITION_TIME);
         gTrk[j].op    = PositionGetDouble(POSITION_PRICE_OPEN);
         gTrk[j].mae   = 0;
         gTrk[j].mfe   = 0;
         gTrk[j].tmae  = gTrk[j].topen;
         double sl = PositionGetDouble(POSITION_SL);
         string t0 = StringSubstr(gTrk[j].tag, 0, 1);
         if(t0 == "B")      gTrk[j].atr = (sl > 0 && InpBreakSLatr > 0) ? MathAbs(gTrk[j].op - sl) / InpBreakSLatr : 0;
         else if(t0 == "L") gTrk[j].atr = (sl > 0) ? MathAbs(gTrk[j].op - sl) : 0;   // v42: unit = one range width
         else if(t0 == "T") gTrk[j].atr = (sl > 0 && InpTrendSLatr > 0) ? MathAbs(gTrk[j].op - sl) / InpTrendSLatr : 0;   // v43
         else if(t0 == "R") gTrk[j].atr = GlobalVariableCheck(GVK("A" + StringSubstr(gTrk[j].tag, 1)))
                                          ? GlobalVariableGet(GVK("A" + StringSubstr(gTrk[j].tag, 1))) : 0;
         else               gTrk[j].atr = EntryATR(tk, gTrk[j].op, sl);
      }
      double adv = gTrk[j].buy ? gTrk[j].op - bid : ask - gTrk[j].op;
      double fav = gTrk[j].buy ? bid - gTrk[j].op : gTrk[j].op - ask;
      if(adv > gTrk[j].mae) { gTrk[j].mae = adv; gTrk[j].tmae = TimeCurrent(); }
      if(fav > gTrk[j].mfe)   gTrk[j].mfe = fav;
   }
}

void CsvStart()
{
   if(!CsvOn()) return;
   //--- every tester run gets its own file, stamped with the PC clock, so a second
   //--- test can never overwrite the first one. Live trading keeps one growing file.
   if(MQLInfoInteger(MQL_TESTER))
   {
      string stamp = TimeToString(TimeLocal(), TIME_DATE | TIME_SECONDS);
      StringReplace(stamp, ".", ""); StringReplace(stamp, ":", ""); StringReplace(stamp, " ", "_");
      gCsvName = "HiWin_v43_trades_" + stamp + ".csv";
   }
   else   //--- v42.2: one file per account, so two terminals on one PC never share a file
      gCsvName = "HiWin_v43_trades_" + (string)AccountInfoInteger(ACCOUNT_LOGIN) + ".csv";
   bool fresh = MQLInfoInteger(MQL_TESTER) || !FileIsExist(CsvName(), FILE_COMMON);
   if(!fresh) return;
   int h = FileOpen(CsvName(), FILE_WRITE | FILE_CSV | FILE_ANSI | FILE_COMMON, ',');
   if(h == INVALID_HANDLE) { Print("HiWin: cannot create ", CsvName(), " err ", GetLastError()); return; }
   Print("HiWin: trade log -> Common\\Files\\", CsvName());
   FileWrite(h, "pos_id", "tag", "side", "open_time", "open_price", "lots", "atr_entry",
             "close_time", "close_price", "net_pl", "exit", "mae_atr", "mfe_atr", "min_to_mae", "min_held");
   FileClose(h);
}

void CsvClosed(ulong deal)
{
   ulong pid = (ulong)HistoryDealGetInteger(deal, DEAL_POSITION_ID);
   GlobalVariableDel(GVK("A" + (string)pid));
   int j = TrkFind(pid);
   if(!CsvOn() || j < 0) return;

   long   rs = HistoryDealGetInteger(deal, DEAL_REASON);
   string ex = (rs == DEAL_REASON_TP) ? "tp" : (rs == DEAL_REASON_SL) ? "sl" :
               (rs == DEAL_REASON_SO) ? "stopout" : "ea";
   double pl = HistoryDealGetDouble(deal, DEAL_PROFIT) + HistoryDealGetDouble(deal, DEAL_SWAP)
             + 2.0 * HistoryDealGetDouble(deal, DEAL_COMMISSION);   // entry commission is charged the same
   datetime tc = (datetime)HistoryDealGetInteger(deal, DEAL_TIME);
   double a = gTrk[j].atr;

   int h = FileOpen(CsvName(), FILE_READ | FILE_WRITE | FILE_CSV | FILE_ANSI | FILE_COMMON, ',');
   if(h != INVALID_HANDLE)
   {
      FileSeek(h, 0, SEEK_END);
      FileWrite(h, (string)pid, gTrk[j].tag, gTrk[j].buy ? "buy" : "sell",
                TimeToString(gTrk[j].topen, TIME_DATE | TIME_SECONDS), DoubleToString(gTrk[j].op, _Digits),
                DoubleToString(HistoryDealGetDouble(deal, DEAL_VOLUME), 2), DoubleToString(a, 3),
                TimeToString(tc, TIME_DATE | TIME_SECONDS), DoubleToString(HistoryDealGetDouble(deal, DEAL_PRICE), _Digits),
                DoubleToString(pl, 2), ex,
                DoubleToString(a > 0 ? gTrk[j].mae / a : 0, 3), DoubleToString(a > 0 ? gTrk[j].mfe / a : 0, 3),
                DoubleToString((gTrk[j].tmae - gTrk[j].topen) / 60.0, 1), DoubleToString((tc - gTrk[j].topen) / 60.0, 1));
      FileClose(h);
   }
   int last = ArraySize(gTrk) - 1;
   if(j != last) gTrk[j] = gTrk[last];
   ArrayResize(gTrk, last);
}

//--- total money at risk if every open position hits its stop, as % of equity
double OpenRiskPct()
{
   double eq = AccountInfoDouble(ACCOUNT_EQUITY);
   if(eq <= 0) return 0;
   double risk = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong tk = PositionGetTicket(i);
      if(tk == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
      if(PositionGetInteger(POSITION_MAGIC) != InpMagic) continue;
      double op = PositionGetDouble(POSITION_PRICE_OPEN);
      double sl = PositionGetDouble(POSITION_SL);
      double vl = PositionGetDouble(POSITION_VOLUME);
      if(sl <= 0) continue;
      double p = 0;
      ENUM_ORDER_TYPE ot = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY) ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
      if(OrderCalcProfit(ot, _Symbol, vl, op, sl, p) && p < 0) risk += -p;
   }
   return risk / eq * 100.0;
}

double FloatingPL()
{
   double pl = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong tk = PositionGetTicket(i);
      if(tk == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
      if(PositionGetInteger(POSITION_MAGIC) != InpMagic) continue;
      pl += PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP);
   }
   return pl;
}

void CloseEverything(string why)
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong tk = PositionGetTicket(i);
      if(tk == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
      if(PositionGetInteger(POSITION_MAGIC) != InpMagic) continue;
      trade.PositionClose(tk);
   }
   Alarm("EMERGENCY CLOSE: " + why);
}

//--- day tracking + daily loss lock (reset cleanly every new day; ignored when the limit is off)
void UpdateDay()
{
   MqlDateTime dt;
   TimeToStruct(VT(TimeCurrent()), dt);
   dt.hour = 0; dt.min = 0; dt.sec = 0;
   datetime today = StructToTime(dt);
   if(today != gDay)
   {
      gDay = today;
      gDayStart = AccountInfoDouble(ACCOUNT_BALANCE);
      gDayLocked = false;
      GlobalVariableSet(GVK("DayStart"), gDayStart);
      GlobalVariableSet(GVK("Day"), (double)today);
      GlobalVariableSet(GVK("Locked"), 0);
      return;
   }
   if(gDayStart <= 0)
   {
      if(GlobalVariableCheck(GVK("DayStart"))) gDayStart = GlobalVariableGet(GVK("DayStart"));
      if(gDayStart <= 0) gDayStart = AccountInfoDouble(ACCOUNT_BALANCE);
      gDayLocked = (InpDailyLossPct > 0) && (GlobalVariableGet(GVK("Locked")) > 0.5);
   }
   if(InpDailyLossPct <= 0) { gDayLocked = false; return; }
   double dd = gDayStart - AccountInfoDouble(ACCOUNT_BALANCE);
   if(!gDayLocked && dd >= gDayStart * InpDailyLossPct / 100.0)
   {
      gDayLocked = true;
      GlobalVariableSet(GVK("Locked"), 1);
      Alarm("DAILY LOSS LIMIT reached (-" + DoubleToString(dd, 2) + "). No new trades today.");
   }
}

//--- true during an unusual volatility spike (same measure the entry filter uses)
bool SpikeNow()
{
   if(InpSpikeMult <= 0) return false;
   if(ArraySize(atr) < 52) return false;
   double sum = 0;
   for(int q = 2; q <= 51; q++) sum += atr[q];
   return (atr[1] > InpSpikeMult * sum / 50.0);
}

bool InTradingWindow()
{
   MqlDateTime now;
   TimeToStruct(VT(TimeCurrent()), now);
   if(InpFridayFilter && now.day_of_week == 5 && now.hour >= InpFridayStopHour) return false;
   if(now.hour < InpStartHour || now.hour > InpEndHour) return false;
   return true;
}

//--- v9.0: holiday list
bool IsHoliday()
{
   if(InpHolidayDates == "") return false;
   MqlDateTime dt; TimeToStruct(VT(TimeCurrent()), dt);
   string today = StringFormat("%04d.%02d.%02d", dt.year, dt.mon, dt.day);
   string parts[];
   int k = StringSplit(InpHolidayDates, ',', parts);
   for(int i = 0; i < k; i++)
   {
      StringTrimLeft(parts[i]); StringTrimRight(parts[i]);
      if(parts[i] == today) return true;
   }
   return false;
}

//--- v9.0: our pending limit orders
int CountPendings()
{
   int c = 0;
   for(int i = OrdersTotal() - 1; i >= 0; i--)
   {
      ulong tk = OrderGetTicket(i);
      if(tk == 0) continue;
      if(OrderGetString(ORDER_SYMBOL) != _Symbol) continue;
      if(OrderGetInteger(ORDER_MAGIC) != InpMagic) continue;
      c++;
   }
   return c;
}

//--- delete pendings that waited too long, or that no longer make sense
void ManagePendings()
{
   if(!InpUseLimitEntry) return;
   ulong kill[]; int nk = 0;
   bool shut = gDayLocked || IsHoliday() || !InTradingWindow();
   for(int i = OrdersTotal() - 1; i >= 0; i--)
   {
      ulong tk = OrderGetTicket(i);
      if(tk == 0) continue;
      if(OrderGetString(ORDER_SYMBOL) != _Symbol) continue;
      if(OrderGetInteger(ORDER_MAGIC) != InpMagic) continue;
      long setup = OrderGetInteger(ORDER_TIME_SETUP);
      bool old = (TimeCurrent() - setup) >= (long)MathMax(1, InpLimitWaitBars) * 300;
      if(old || shut) { ArrayResize(kill, nk + 1); kill[nk++] = tk; }
   }
   for(int i = 0; i < nk; i++) trade.OrderDelete(kill[i]);
}

int CountPositions()
{
   int n = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong tk = PositionGetTicket(i);
      if(tk == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
      if(PositionGetInteger(POSITION_MAGIC) != InpMagic) continue;
      string cmA = PositionGetString(POSITION_COMMENT);
      if(StringSubstr(cmA, 0, 1) == "R") continue;   // recovery legs do not count
      if(StringSubstr(cmA, 0, 1) == "B") continue;   // v28: engine B has its own budget
      if(StringSubstr(cmA, 0, 1) == "L") continue;   // v42: engine L has its own budget
      if(StringSubstr(cmA, 0, 1) == "T") continue;   // v43: engine T has its own budget
      n++;
   }
   return n;
}
//+------------------------------------------------------------------+
// time stop: close trades older than N M5 candles
//--- v2.8 recovery add: a pullback trade that fails (price keeps going against it) gets ONE more entry
//    at a better price; both close at (average entry + InpRecoverTPATR x ATR) or at the same original stop.
int RecoveryCount(ulong origTicket)
{
   string tag = "R" + (string)origTicket;
   int c = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong tk = PositionGetTicket(i);
      if(tk == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
      if(PositionGetInteger(POSITION_MAGIC) != InpMagic) continue;
      if(PositionGetString(POSITION_COMMENT) == tag) c++;
   }
   return c;
}

void ManageRecovery()
{
   if(InpRecoverAtATR <= 0 || InpSLatr <= 0) return;

   //--- 1) close recovery legs whose original trade is gone
   ulong closeList[];
   int nc = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong tk = PositionGetTicket(i);
      if(tk == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
      if(PositionGetInteger(POSITION_MAGIC) != InpMagic) continue;
      string cm = PositionGetString(POSITION_COMMENT);
      if(StringSubstr(cm, 0, 1) != "R") continue;
      ulong ot = (ulong)StringToInteger(StringSubstr(cm, 1));
      if(!PositionSelectByTicket(ot))
      { ArrayResize(closeList, nc + 1); closeList[nc++] = tk; }
   }
   for(int k = 0; k < nc; k++) trade.PositionClose(closeList[k]);

   //--- 2) guards: a recovery add is the one place where a runaway move can really hurt
   if(gDayLocked)                                { gStatus = "Daily limit: no recovery adds"; return; }
   if(InpRecoverHoursOnly && !InTradingWindow()) { gStatus = "Outside window: no recovery adds"; return; }
   if(InpRecoverSpikeGuard && SpikeNow())        { gStatus = "Volatility spike: no recovery adds"; return; }

   //--- 3) open a recovery leg for original trades that moved far enough against us
   ulong origs[];
   int no = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong tk = PositionGetTicket(i);
      if(tk == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
      if(PositionGetInteger(POSITION_MAGIC) != InpMagic) continue;
      string cmO = PositionGetString(POSITION_COMMENT);
      if(StringSubstr(cmO, 0, 1) == "R") continue;  // v11.0: originals carry S0..S5
      if(StringSubstr(cmO, 0, 1) == "B") continue;  // v28: a breakout trade is never rescued
      if(StringSubstr(cmO, 0, 1) == "L") continue;  // v42: nor a London trade
      if(StringSubstr(cmO, 0, 1) == "T") continue;  // v43: nor a trend trade
      ArrayResize(origs, no + 1); origs[no++] = tk;
   }
   for(int k = 0; k < no; k++)
   {
      ulong tk = origs[k];
      if(!PositionSelectByTicket(tk)) continue;
      if(RecoveryCount(tk) >= MathMax(1, InpMaxRecoveryLegs)) continue;
      if(!PositionSelectByTicket(tk)) continue;

      long   type = PositionGetInteger(POSITION_TYPE);
      double op   = PositionGetDouble(POSITION_PRICE_OPEN);
      double sl   = PositionGetDouble(POSITION_SL);
      double vol  = PositionGetDouble(POSITION_VOLUME);
      if(sl <= 0) continue;
      bool   isBuy = (type == POSITION_TYPE_BUY);
      if(isBuy ? (sl >= op) : (sl <= op)) continue;   // stop already locked in profit: no recovery needed
      double atrE = EntryATR(tk, op, sl);   // v39: remembered, the stop may have moved
      if(atrE <= 0) continue;
      double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      bool   buy = isBuy;
      double adverse = buy ? (op - bid) : (ask - op);
      if(adverse < InpRecoverAtATR * atrE) continue;

      double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP); if(step <= 0) step = 0.01;
      double minL = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
      double maxL = MathMin(SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX), InpMaxLot);
      double lot  = MathFloor(vol * InpRecoverLotMult / step) * step;
      lot = MathMax(minL, MathMin(lot, maxL));

      double px = buy ? ask : bid;
      double m = 0;
      if(OrderCalcMargin(buy ? ORDER_TYPE_BUY : ORDER_TYPE_SELL, _Symbol, lot, px, m) &&
         m > AccountInfoDouble(ACCOUNT_MARGIN_FREE) * InpMaxMarginPct / 100.0) continue;

      //--- weighted average over the WHOLE group (original + every recovery leg it already has)
      string tag = "R" + (string)tk;
      double gVol = vol, gCost = op * vol;
      for(int q = PositionsTotal() - 1; q >= 0; q--)
      {
         ulong qt = PositionGetTicket(q);
         if(qt == 0) continue;
         if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
         if(PositionGetInteger(POSITION_MAGIC) != InpMagic) continue;
         if(PositionGetString(POSITION_COMMENT) != tag) continue;
         double qv = PositionGetDouble(POSITION_VOLUME);
         gVol  += qv;
         gCost += PositionGetDouble(POSITION_PRICE_OPEN) * qv;
      }
      double avg = (gCost + px * lot) / (gVol + lot);
      double tp  = NormalizeDouble(buy ? avg + InpRecoverTPATR * atrE : avg - InpRecoverTPATR * atrE, _Digits);
      double stopsLvl = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL) * _Point;
      if(buy  && tp - bid <= stopsLvl) continue;
      if(!buy && ask - tp <= stopsLvl) continue;

      //--- v39: optional group stop - the whole group dies InpGroupStopATR beyond the leg,
      //--- instead of at the original 5 ATR stop. Only ever tightens.
      double gsl = sl;
      if(InpGroupStopATR > 0)
      {
         double c = NormalizeDouble(buy ? px - InpGroupStopATR * atrE : px + InpGroupStopATR * atrE, _Digits);
         bool tighter = buy ? (c > sl) : (c < sl);
         bool legal   = buy ? (bid - c > stopsLvl + _Point) : (c - ask > stopsLvl + _Point);
         if(tighter && legal) gsl = c;
      }

      //--- portfolio risk cap: what would be at stake if EVERYTHING stopped out
      if(InpMaxOpenRiskPct > 0)
      {
         double addRisk = 0;
         if(OrderCalcProfit(buy ? ORDER_TYPE_BUY : ORDER_TYPE_SELL, _Symbol, lot, px, gsl, addRisk) && addRisk < 0)
         {
            double eq = AccountInfoDouble(ACCOUNT_EQUITY);
            if(eq > 0 && OpenRiskPct() + (-addRisk / eq * 100.0) > InpMaxOpenRiskPct)
            { gStatus = "Risk cap: recovery add skipped"; continue; }
         }
      }

      //--- v13: the cap that the v9.0 report asked for. In that run the EA
      //--- reached 3 and 4 open positions through recovery legs, and the
      //--- trades opened with 2 already running were the ONLY losing group
      //--- (31 trades, PF 0.70, net -108) while every other group made money.
      if(InpMaxTotalPositions > 0 && CountAllPositions() >= InpMaxTotalPositions)
      { gStatus = "Position cap reached: no recovery add"; continue; }

      bool ok = buy ? trade.Buy(lot, _Symbol, 0.0, gsl, tp, tag) : trade.Sell(lot, _Symbol, 0.0, gsl, tp, tag);
      if(ok)
      {
         //--- every position of this group now closes at the same target
         if(PositionSelectByTicket(tk)) trade.PositionModify(tk, gsl, tp);
         for(int q = PositionsTotal() - 1; q >= 0; q--)
         {
            ulong qt = PositionGetTicket(q);
            if(qt == 0) continue;
            if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
            if(PositionGetInteger(POSITION_MAGIC) != InpMagic) continue;
            if(PositionGetString(POSITION_COMMENT) != tag) continue;
            if(MathAbs(PositionGetDouble(POSITION_TP) - tp) > _Point ||
               MathAbs(PositionGetDouble(POSITION_SL) - gsl) > _Point) trade.PositionModify(qt, gsl, tp);
         }
         Alarm("RECOVERY ADD " + (buy ? "BUY " : "SELL ") + DoubleToString(lot, 2) +
               " | group target " + DoubleToString(tp, _Digits) + " | group stop " + DoubleToString(gsl, _Digits));
      }
   }
}

void ManageTimeStop()
{
   if(InpTimeStopBars <= 0 && InpDecayBars <= 0 && InpBeTriggerATR <= 0) return;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong tk = PositionGetTicket(i);
      if(tk == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
      if(PositionGetInteger(POSITION_MAGIC) != InpMagic) continue;
      if(StringSubstr(PositionGetString(POSITION_COMMENT), 0, 1) == "B") continue;   // v28: engine B trails, it has no clock
      if(StringSubstr(PositionGetString(POSITION_COMMENT), 0, 1) == "L") continue;   // v42: engine L closes at InpLdnCloseHour
      if(StringSubstr(PositionGetString(POSITION_COMMENT), 0, 1) == "T") continue;   // v43: engine T trails, it has no clock
      datetime ot = (datetime)PositionGetInteger(POSITION_TIME);

      //--- v2.7 break-even lock (OFF unless InpBeTriggerATR > 0).
      //    A locked trade can never reach -InpRecoverAtATR, so it never gets a recovery leg.
      if(InpBeTriggerATR > 0 && InpSLatr > 0)
      {
         double bop = PositionGetDouble(POSITION_PRICE_OPEN);
         double bsl = PositionGetDouble(POSITION_SL);
         double btp = PositionGetDouble(POSITION_TP);
         bool   bbuy = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY);
         if(bsl > 0 && ((bbuy && bsl < bop) || (!bbuy && bsl > bop)))
         {
            double atrB  = EntryATR(tk, bop, bsl);   // v39
            double stopsB = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL) * _Point;
            if(bbuy)
            {
               double bid2 = SymbolInfoDouble(_Symbol, SYMBOL_BID);
               double nsl  = NormalizeDouble(bop + InpBeLockATR * atrB, _Digits);
               if(bid2 - bop >= InpBeTriggerATR * atrB && bid2 - nsl > stopsB + _Point)
                  trade.PositionModify(tk, nsl, btp);
            }
            else
            {
               double ask2 = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
               double nsl  = NormalizeDouble(bop - InpBeLockATR * atrB, _Digits);
               if(bop - ask2 >= InpBeTriggerATR * atrB && nsl - ask2 > stopsB + _Point)
                  trade.PositionModify(tk, nsl, btp);
            }
         }
      }

      //--- time-decay stop: after N candles tighten the wide stop (close at once if already beyond it)
      if(InpDecayBars > 0 && (TimeCurrent() - ot) >= (long)InpDecayBars * 300)
      {
         double op = PositionGetDouble(POSITION_PRICE_OPEN);
         double sl0 = PositionGetDouble(POSITION_SL);
         double tp0 = PositionGetDouble(POSITION_TP);
         if(sl0 > 0 && InpSLatr > 0)
         {
            double dist   = MathAbs(op - sl0);
            double target = InpDecayATR * EntryATR(tk, op, sl0);   // v39
            if(dist > target * 1.01)
            {
               double stopsLvl = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL) * _Point;
               if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY)
               {
                  double newSL = NormalizeDouble(op - target, _Digits);
                  if(SymbolInfoDouble(_Symbol, SYMBOL_BID) - newSL <= stopsLvl + _Point) { trade.PositionClose(tk); continue; }
                  trade.PositionModify(tk, newSL, tp0);
               }
               else
               {
                  double newSL = NormalizeDouble(op + target, _Digits);
                  if(newSL - SymbolInfoDouble(_Symbol, SYMBOL_ASK) <= stopsLvl + _Point) { trade.PositionClose(tk); continue; }
                  trade.PositionModify(tk, newSL, tp0);
               }
            }
         }
      }

      if(InpTimeStopBars > 0 && TimeCurrent() - ot >= (long)InpTimeStopBars * 300)
         trade.PositionClose(tk);
   }
}
//+------------------------------------------------------------------+
bool LoadData()
{
   if(CopyBuffer(hRsi, 0, 0, 3, rsi) < 3) return false;
   if(CopyBuffer(hAtr, 0, 0, 52, atr) < 52) return false;
   if(CopyBuffer(hAdx, 0, 0, 3, adx) < 3) return false;
   if(CopyBuffer(hTrF, 0, 0, 6, trF) < 6) return false;
   if(CopyBuffer(hTrS, 0, 0, 6, trS) < 6) return false;
   if(InpUseS1 && hBB  != INVALID_HANDLE)
   { if(CopyBuffer(hBB, 1,0,3,bbU)<3 || CopyBuffer(hBB, 2,0,3,bbL)<3) return false; }
   if(InpUseS4 && hT2F != INVALID_HANDLE)
   { if(CopyBuffer(hT2F,0,0,6,t2F)<6 || CopyBuffer(hT2S,0,0,6,t2S)<6) return false; }
   if(InpUseS2 && hH1F != INVALID_HANDLE)
   { if(CopyBuffer(hH1F,0,0,6,h1F)<6 || CopyBuffer(hH1S,0,0,6,h1S)<6) return false; }
   if(InpUseS5 && hIch != INVALID_HANDLE)
   { if(CopyBuffer(hIch,2,0,3,spA)<3 || CopyBuffer(hIch,3,0,3,spB)<3) return false; }
   return (atr[1] > 0);
}
//+------------------------------------------------------------------+
// same strict trend as XAU Max (M15, last closed candle)
int TrendDir()
{
   double c = iClose(_Symbol, PERIOD_M15, 1);
   if(trF[1] > trS[1] && trS[1] > trS[4] && c > trS[1]) return 1;
   if(trF[1] < trS[1] && trS[1] < trS[4] && c < trS[1]) return -1;
   return 0;
}
//+------------------------------------------------------------------+
double LossPerLot(int dir, double entry, double slDist)
{
   double sl = (dir == 1) ? entry - slDist : entry + slDist;
   double p = 0;
   ENUM_ORDER_TYPE ot = (dir == 1) ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
   if(!OrderCalcProfit(ot, _Symbol, 1.0, entry, sl, p) || p >= 0) return 0;
   return -p;
}
//+------------------------------------------------------------------+
double CalcLot(int dir, double entry, double slDist)
{
   double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double maxLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   double step   = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   if(step <= 0) step = 0.01;
   int dg = (int)MathMax(0.0, MathRound(-MathLog10(step)));

   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   double lpl = LossPerLot(dir, entry, slDist);
   if(lpl <= 0) return 0;

   double lot;
   if(InpFixedLot > 0)         lot = InpFixedLot;
   else if(InpLotPer1000 > 0)  lot = equity / 1000.0 * InpLotPer1000;
   else                        lot = (equity * InpRiskPct / 100.0) / lpl;
   lot = MathFloor(lot / step) * step;
   if(lot < minLot)
   {
      if(lpl * minLot > equity * InpMaxLossAtMinLot / 100.0) return 0;   // too risky for this account
      lot = minLot;
   }
   lot = MathMin(lot, MathMin(maxLot, InpMaxLot));

   double free = AccountInfoDouble(ACCOUNT_MARGIN_FREE);
   double m = 0;
   ENUM_ORDER_TYPE ot = (dir == 1) ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
   if(OrderCalcMargin(ot, _Symbol, lot, entry, m) && m > 0)
   {
      double cap = free * InpMaxMarginPct / 100.0;
      if(m > cap)
      {
         lot = MathFloor(lot * (cap / m) / step) * step;
         if(lot < minLot) return 0;
      }
   }
   return NormalizeDouble(lot, dg);
}
//+------------------------------------------------------------------+
//| v13: every position this EA holds, recovery legs included.        |
//| CountPositions() deliberately ignores legs, because the entry      |
//| logic treats a group as one trade. The risk does not: four legs    |
//| in the same direction die to one move. This is the number that     |
//| the hard cap is applied to.                                        |
//+------------------------------------------------------------------+
int CountAllPositions()
{
   int c = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong tk = PositionGetTicket(i);
      if(tk == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
      if(PositionGetInteger(POSITION_MAGIC) != InpMagic) continue;
      if(StringSubstr(PositionGetString(POSITION_COMMENT), 0, 1) == "B") continue;   // v28
      if(StringSubstr(PositionGetString(POSITION_COMMENT), 0, 1) == "L") continue;   // v42
      if(StringSubstr(PositionGetString(POSITION_COMMENT), 0, 1) == "T") continue;   // v43
      c++;
   }
   return c;
}
//+------------------------------------------------------------------+
//+------------------------------------------------------------------+
//| v42 ENGINE L - London breakout                                    |
//+------------------------------------------------------------------+
datetime gLdnDay = 0;   // server day on which engine L already fired

int CountLondon()
{
   int c = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong tk = PositionGetTicket(i);
      if(tk == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
      if(PositionGetInteger(POSITION_MAGIC) != InpMagic) continue;
      if(StringSubstr(PositionGetString(POSITION_COMMENT), 0, 1) == "L") c++;
   }
   return c;
}

//--- high / low of today's M5 candles whose server hour is in [start, end)
bool LondonRange(double &hi, double &lo)
{
   datetime b1 = VT(iTime(_Symbol, PERIOD_M5, 1));
   datetime day0 = (datetime)((long)b1 - (long)b1 % 86400);
   hi = -DBL_MAX; lo = DBL_MAX;
   for(int sh = 1; sh < 400; sh++)
   {
      datetime t0 = iTime(_Symbol, PERIOD_M5, sh);
      if(t0 == 0) break;
      datetime t = VT(t0);
      if(t < day0) break;
      int h = (int)(((long)t % 86400) / 3600);
      if(h < InpLdnRangeStart || h >= InpLdnRangeEnd) continue;
      hi = MathMax(hi, iHigh(_Symbol, PERIOD_M5, sh));
      lo = MathMin(lo, iLow(_Symbol, PERIOD_M5, sh));
   }
   return (hi > lo && lo < DBL_MAX);
}

//--- once per new M5 candle: the first close outside today's range is traded at market
void CheckLondon()
{
   if(!InpUseLondon || gMode != HW_AUTO) return;
   datetime b1 = VT(iTime(_Symbol, PERIOD_M5, 1));
   datetime day0 = (datetime)((long)b1 - (long)b1 % 86400);
   if(gLdnDay == day0) return;                                  // one trade a day
   int h = (int)(((long)b1 % 86400) / 3600);
   if(h < InpLdnRangeEnd || h >= InpLdnCloseHour - 2) return;
   double hi, lo;
   if(!LondonRange(hi, lo)) return;
   double c1 = iClose(_Symbol, PERIOD_M5, 1);
   int dir = (c1 > hi) ? 1 : (c1 < lo) ? -1 : 0;
   if(dir == 0) return;
   gLdnDay = day0;
   if(CountLondon() > 0) return;

   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double entry = (dir == 1) ? ask : bid;
   double rng   = MathMax(hi - lo, 0.5);
   double sl = NormalizeDouble(entry - dir * rng, _Digits);
   double tp = NormalizeDouble(entry + dir * InpLdnTPmult * rng, _Digits);
   double stopsLvl = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL) * _Point;
   if(rng <= stopsLvl + _Point) return;

   double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP); if(step <= 0) step = 0.01;
   double lot = CalcLot(dir, entry, rng) * MathMax(0.0, InpLdnLotMult);
   lot = MathFloor(lot / step + 1e-9) * step;
   lot = MathMax(lot, SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN));
   lot = MathMin(lot, SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX));

   bool ok = (dir == 1) ? trade.Buy (lot, _Symbol, 0.0, sl, tp, "L1")
                        : trade.Sell(lot, _Symbol, 0.0, sl, tp, "L1");
   if(ok) Alarm("L1 London breakout " + ((dir == 1) ? "BUY " : "SELL ") + DoubleToString(lot, 2) +
                " | range " + DoubleToString(lo, _Digits) + " - " + DoubleToString(hi, _Digits));
   else   gStatus = "L1 order rejected: " + (string)trade.ResultRetcode();
}

//--- every tick: close engine L positions at the end of its day
void ManageLondon()
{
   if(!InpUseLondon) return;
   MqlDateTime now; TimeToStruct(VT(TimeCurrent()), now);
   long today = (long)VT(TimeCurrent()) / 86400;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong tk = PositionGetTicket(i);
      if(tk == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
      if(PositionGetInteger(POSITION_MAGIC) != InpMagic) continue;
      if(StringSubstr(PositionGetString(POSITION_COMMENT), 0, 1) != "L") continue;
      //--- v42.1: also close on the first tick of a later day - on holidays the market
      //--- shuts before InpLdnCloseHour and the trade used to stay open overnight
      bool oldDay = (long)VT((datetime)PositionGetInteger(POSITION_TIME)) / 86400 < today;
      if(now.hour >= InpLdnCloseHour || oldDay) trade.PositionClose(tk);
   }
}
//+------------------------------------------------------------------+
//| v43 ENGINE T - H1 Donchian trend follower                         |
//+------------------------------------------------------------------+

//--- the price a trend trade has reached at its best since it opened (M5 highs / lows)
double TrendBest(bool buy, datetime opened)
{
   int sh = iBarShift(_Symbol, PERIOD_M5, opened, false);
   if(sh < 0) return 0;
   int idx = buy ? iHighest(_Symbol, PERIOD_M5, MODE_HIGH, sh + 1, 0)
                 : iLowest (_Symbol, PERIOD_M5, MODE_LOW,  sh + 1, 0);
   if(idx < 0) return 0;
   return buy ? iHigh(_Symbol, PERIOD_M5, idx) : iLow(_Symbol, PERIOD_M5, idx);
}

//--- once per new H1 candle: trail the open trend trade, then look for a new break
void CheckTrend()
{
   if(!InpUseTrend || gMode != HW_AUTO || hAtrH1 == INVALID_HANDLE) return;
   datetime h0 = iTime(_Symbol, PERIOD_H1, 0);
   if(h0 == 0 || h0 == gTrendBar) return;
   double a[];
   ArraySetAsSeries(a, true);
   if(CopyBuffer(hAtrH1, 0, 0, 2, a) < 2 || a[1] <= 0) return;
   gTrendBar = h0;
   double atrH = a[1];
   double stopsLvl = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL) * _Point;

   bool open = false;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong tk = PositionGetTicket(i);
      if(tk == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
      if(PositionGetInteger(POSITION_MAGIC) != InpMagic) continue;
      if(StringSubstr(PositionGetString(POSITION_COMMENT), 0, 1) != "T") continue;
      open = true;
      bool   buy = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY);
      double sl  = PositionGetDouble(POSITION_SL);
      double best = TrendBest(buy, (datetime)PositionGetInteger(POSITION_TIME));
      if(best <= 0) continue;
      double ns = NormalizeDouble(buy ? best - InpTrendTrailATR * atrH : best + InpTrendTrailATR * atrH, _Digits);
      double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID), ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      bool better = buy ? (ns > sl + _Point) : (sl <= 0 || ns < sl - _Point);
      bool legal  = buy ? (bid - ns > stopsLvl + _Point) : (ns - ask > stopsLvl + _Point);
      if(better && legal) trade.PositionModify(tk, ns, 0.0);
   }
   if(open || gDayLocked) return;

   int n = MathMax(5, InpTrendN);
   int hi = iHighest(_Symbol, PERIOD_H1, MODE_HIGH, n, 2);
   int lo = iLowest (_Symbol, PERIOD_H1, MODE_LOW,  n, 2);
   if(hi < 0 || lo < 0) return;
   double c1 = iClose(_Symbol, PERIOD_H1, 1);
   int dir = (c1 > iHigh(_Symbol, PERIOD_H1, hi)) ? 1 : (c1 < iLow(_Symbol, PERIOD_H1, lo)) ? -1 : 0;
   if(dir == 0) return;

   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK), bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double entry = (dir == 1) ? ask : bid;
   double slDist = InpTrendSLatr * atrH;
   if(slDist <= stopsLvl + _Point) return;
   double lpl = LossPerLot(dir, entry, slDist);
   if(lpl <= 0) return;
   double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP); if(step <= 0) step = 0.01;
   double lot = AccountInfoDouble(ACCOUNT_EQUITY) * InpTrendRiskPct / 100.0 / lpl;
   lot = MathFloor(lot / step + 1e-9) * step;
   lot = MathMax(lot, SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN));
   lot = MathMin(lot, MathMin(SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX), InpMaxLot));
   double sl = NormalizeDouble(entry - dir * slDist, _Digits);
   bool ok = (dir == 1) ? trade.Buy(lot, _Symbol, 0.0, sl, 0.0, "T1") : trade.Sell(lot, _Symbol, 0.0, sl, 0.0, "T1");
   if(ok) Alarm("T1 trend " + ((dir == 1) ? "BUY " : "SELL ") + DoubleToString(lot, 2) + " | stop " + DoubleToString(sl, _Digits));
   else   gStatus = "T1 order rejected: " + (string)trade.ResultRetcode();
}
//+------------------------------------------------------------------+
int CountBreakout()
{
   int c = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong tk = PositionGetTicket(i);
      if(tk == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
      if(PositionGetInteger(POSITION_MAGIC) != InpMagic) continue;
      if(StringSubstr(PositionGetString(POSITION_COMMENT), 0, 1) == "B") c++;
   }
   return c;
}
//+------------------------------------------------------------------+
//| ENGINE B - the breakout rider                                     |
//| Three conditions, all on the last CLOSED M5 candle:               |
//|   1. the market has just woken up - ATR is at least               |
//|      InpBreakSpikeMin times its own 50-candle average             |
//|   2. ATR is above InpBreakAtrMin in absolute terms, so a "spike"   |
//|      in a dead market does not count                              |
//|   3. that candle closed beyond the high (or low) of the previous  |
//|      InpBreakLookback candles                                     |
//| Direction comes from the break itself, not from the M15 trend:    |
//| a break IS the new trend, and waiting for the M15 averages to     |
//| agree means arriving after the move.                              |
//+------------------------------------------------------------------+
int SigBreakout()
{
   if(!InpUseBreakout || InpBreakLookback < 3) return 0;
   if(ArraySize(atr) < 52) return 0;
   double sum = 0;
   for(int q = 2; q <= 51; q++) sum += atr[q];
   double avg = sum / 50.0;
   if(avg <= 0) return 0;
   if(atr[1] < InpBreakSpikeMin * avg) return 0;
   double bMin = (InpBreakAtrMinPct > 0) ? iClose(_Symbol, PERIOD_M5, 1) * InpBreakAtrMinPct / 100.0 : InpBreakAtrMin;   // v40
   if(atr[1] < bMin)                    return 0;
   int hi = iHighest(_Symbol, PERIOD_M5, MODE_HIGH, InpBreakLookback, 2);
   int lo = iLowest (_Symbol, PERIOD_M5, MODE_LOW,  InpBreakLookback, 2);
   if(hi < 0 || lo < 0) return 0;
   double c1 = iClose(_Symbol, PERIOD_M5, 1);
   if(c1 > iHigh(_Symbol, PERIOD_M5, hi)) return  1;
   if(c1 < iLow (_Symbol, PERIOD_M5, lo)) return -1;
   return 0;
}
//+------------------------------------------------------------------+
//| A breakout is chased at market - a limit order would simply never |
//| be filled on the move it is trying to catch.                      |
//+------------------------------------------------------------------+
void OpenBreakout(int dir)
{
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double a   = atr[1];
   if(a <= 0 || ask <= 0 || bid <= 0) return;

   double entry  = (dir == 1) ? ask : bid;
   double slDist = InpBreakSLatr * a;
   double tpDist = InpBreakTPatr * a;
   double sl = NormalizeDouble((dir == 1) ? entry - slDist : entry + slDist, _Digits);
   double tp = NormalizeDouble((dir == 1) ? entry + tpDist : entry - tpDist, _Digits);

   long   stopsLvl = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL);
   double minDist  = stopsLvl * _Point;
   if(MathAbs(entry - sl) <= minDist + _Point)
   { gStatus = "B1: stop too close to price"; return; }

   double lot = CalcLot(dir, entry, slDist) * MathMax(0.0, InpBreakLotMult);
   double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP); if(step <= 0) step = 0.01;
   double vmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double vmax = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   lot = MathFloor(lot / step) * step;
   if(lot < vmin) lot = vmin;
   if(lot > vmax) lot = vmax;
   if(lot <= 0) return;

   bool ok = (dir == 1) ? trade.Buy (lot, _Symbol, 0.0, sl, tp, "B1")
                        : trade.Sell(lot, _Symbol, 0.0, sl, tp, "B1");
   if(ok)
   {
      gBreakEntries++;
      gLastBreak = iTime(_Symbol, PERIOD_M5, 0);
      gStatus = "B1 breakout " + ((dir == 1) ? "BUY" : "SELL") + " at market";
      Alarm("HiWin B1 breakout " + ((dir == 1) ? "BUY" : "SELL"));
   }
   else gStatus = "B1 order rejected: " + (string)trade.ResultRetcode();
}
//+------------------------------------------------------------------+
//| Engine B has no take-profit discipline and no clock - it has a    |
//| trailing stop. That is the whole point: the scalper caps its win  |
//| at 0.5 ATR, this one lets the move decide where it ends.          |
//+------------------------------------------------------------------+
void ManageBreakout()
{
   if(!InpUseBreakout || InpBreakTrailATR <= 0) return;
   if(ArraySize(atr) < 2) return;
   double a = atr[1];
   if(a <= 0) return;
   long   stopsLvl = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL);
   double minDist  = stopsLvl * _Point;

   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong tk = PositionGetTicket(i);
      if(tk == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol) continue;
      if(PositionGetInteger(POSITION_MAGIC) != InpMagic) continue;
      if(StringSubstr(PositionGetString(POSITION_COMMENT), 0, 1) != "B") continue;

      bool   isBuy = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY);
      double op    = PositionGetDouble(POSITION_PRICE_OPEN);
      double sl    = PositionGetDouble(POSITION_SL);
      double tp    = PositionGetDouble(POSITION_TP);
      double cur   = isBuy ? SymbolInfoDouble(_Symbol, SYMBOL_BID)
                           : SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      if(cur <= 0) continue;
      double prof = isBuy ? (cur - op) : (op - cur);
      if(prof < InpBreakTrailStart * a) continue;

      double want = NormalizeDouble(isBuy ? cur - InpBreakTrailATR * a
                                          : cur + InpBreakTrailATR * a, _Digits);
      if(isBuy  && (cur - want) <= minDist + _Point) continue;
      if(!isBuy && (want - cur) <= minDist + _Point) continue;
      if(isBuy  && sl > 0 && want <= sl + _Point) continue;
      if(!isBuy && sl > 0 && want >= sl - _Point) continue;
      if(trade.PositionModify(tk, want, tp)) gBreakTrails++;
   }
}
//+------------------------------------------------------------------+
void OpenTrade(int dir, string tag)
{
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double spread = ask - bid;
   double stopsLvl = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL) * _Point;
   double a = atr[1];

   if(spread > a * InpMaxSpreadATR)
   {
      gStatus = StringFormat("Skipped: spread %.2f too high vs ATR %.2f (cap %.2f)", spread, a, a * InpMaxSpreadATR);
      gBlkSpread++;
      return;
   }

   double slDist = MathMax(a * InpSLatr, stopsLvl + spread + _Point);
   double tpDist = MathMax(a * InpTPatr, stopsLvl + spread + _Point);
   double entry = (dir == 1) ? ask : bid;
   double sl = NormalizeDouble((dir == 1) ? entry - slDist : entry + slDist, _Digits);
   double tp = NormalizeDouble((dir == 1) ? entry + tpDist : entry - tpDist, _Digits);
   string side = (dir == 1) ? "BUY" : "SELL";
   string info = StringFormat("%s %s | Entry %s | SL %s | TP %s | ATR %s | RSI %s", _Symbol, side,
                              DoubleToString(entry, _Digits), DoubleToString(sl, _Digits),
                              DoubleToString(tp, _Digits), DoubleToString(a, 2),
                              DoubleToString(rsi[1], 0));

   if(gMode == HW_NOTIFY)
   {
      Alarm("SIGNAL " + info);
      gStatus = side + " signal sent";
      return;
   }

   //--- v9.0: pending limit at a better price
   if(InpUseLimitEntry && InpLimitATR > 0)
   {
      double px = NormalizeDouble((dir == 1) ? bid - InpLimitATR * a : ask + InpLimitATR * a, _Digits);
      double gap = (dir == 1) ? (bid - px) : (px - ask);
      if(gap <= stopsLvl + _Point) { gStatus = "Limit too close to price"; return; }
      double psl = NormalizeDouble((dir == 1) ? px - slDist : px + slDist, _Digits);
      double ptp = NormalizeDouble((dir == 1) ? px + tpDist : px - tpDist, _Digits);
      double plot = CalcLot(dir, px, slDist);
      if(plot <= 0) { gStatus = "Skipped: lot / risk / margin"; return; }

      if(InpMaxOpenRiskPct > 0)
      {
         double addRisk = 0;
         if(OrderCalcProfit((dir == 1) ? ORDER_TYPE_BUY : ORDER_TYPE_SELL, _Symbol, plot, px, psl, addRisk) && addRisk < 0)
         {
            double eq = AccountInfoDouble(ACCOUNT_EQUITY);
            if(eq > 0 && OpenRiskPct() + (-addRisk / eq * 100.0) > InpMaxOpenRiskPct)
            { gStatus = "Skipped: portfolio risk cap"; return; }
         }
      }

      bool okp = (dir == 1) ? trade.BuyLimit (plot, px, _Symbol, psl, ptp, ORDER_TIME_GTC, 0, tag)
                            : trade.SellLimit(plot, px, _Symbol, psl, ptp, ORDER_TIME_GTC, 0, tag);
      if(okp)
      {
         gStatus = side + " limit placed at " + DoubleToString(px, _Digits);
         Alarm("LIMIT " + side + " " + DoubleToString(plot, 2) + " @ " + DoubleToString(px, _Digits) +
               " | SL " + DoubleToString(psl, _Digits) + " | TP " + DoubleToString(ptp, _Digits));
      }
      else
      {
         gStatus = "Limit rejected: " + IntegerToString((int)trade.ResultRetcode());
         Print("HiWin: pending failed ", trade.ResultRetcode(), " ", trade.ResultRetcodeDescription());
      }
      return;
   }

   double lot = CalcLot(dir, entry, slDist);
   if(lot <= 0) { gStatus = "Skipped: lot / risk / margin"; return; }

   if(InpMaxOpenRiskPct > 0)
   {
      double addRisk = 0;
      if(OrderCalcProfit((dir == 1) ? ORDER_TYPE_BUY : ORDER_TYPE_SELL, _Symbol, lot, entry, sl, addRisk) && addRisk < 0)
      {
         double eq = AccountInfoDouble(ACCOUNT_EQUITY);
         if(eq > 0 && OpenRiskPct() + (-addRisk / eq * 100.0) > InpMaxOpenRiskPct)
         { gStatus = "Skipped: portfolio risk cap"; return; }
      }
   }

   bool ok = (dir == 1) ? trade.Buy(lot, _Symbol, 0.0, sl, tp, tag)
                        : trade.Sell(lot, _Symbol, 0.0, sl, tp, tag);
   uint rc = trade.ResultRetcode();
   if(!ok && (rc == TRADE_RETCODE_REQUOTE || rc == TRADE_RETCODE_PRICE_CHANGED))
   {
      ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      entry = (dir == 1) ? ask : bid;
      sl = NormalizeDouble((dir == 1) ? entry - slDist : entry + slDist, _Digits);
      tp = NormalizeDouble((dir == 1) ? entry + tpDist : entry - tpDist, _Digits);
      ok = (dir == 1) ? trade.Buy(lot, _Symbol, 0.0, sl, tp, tag)
                      : trade.Sell(lot, _Symbol, 0.0, sl, tp, tag);
      rc = trade.ResultRetcode();
   }

   if(ok && (rc == TRADE_RETCODE_DONE || rc == TRADE_RETCODE_PLACED))
   {
      gStatus = side + " executed";
      Alarm("EXECUTED " + info + " | Lot " + DoubleToString(lot, 2));
   }
   else
   {
      gStatus = "Order rejected: " + IntegerToString((int)rc);
      Print("HiWin: order failed, retcode ", rc, " ", trade.ResultRetcodeDescription());
   }
}
//+------------------------------------------------------------------+
//| v11.0: the five entry setups. Each returns 1 (buy), -1 (sell), 0. |
//| The shared filters (volatility floor, dead-market range, spread,   |
//| hours, position cap) still apply to all of them afterwards.        |
//+------------------------------------------------------------------+
int TrendDir();   // v11.0: forward declaration, the setups below call it
int TrendOf(const double &f[], const double &sl[], ENUM_TIMEFRAMES tf)
{
   if(ArraySize(f) < 5 || ArraySize(sl) < 5) return 0;
   double c = iClose(_Symbol, tf, 1);
   if(f[1] > sl[1] && sl[1] > sl[4] && c > sl[1]) return  1;
   if(f[1] < sl[1] && sl[1] < sl[4] && c < sl[1]) return -1;
   return 0;
}
bool NoSpike()
{
   if(InpSpikeMult <= 0 || ArraySize(atr) < 52) return true;
   double sum = 0;
   for(int q = 2; q <= 51; q++) sum += atr[q];
   return (atr[1] <= InpSpikeMult * sum / 50.0);
}
//--- S0: the original v3.0 entry - M15 trend + RSI 45/55 pullback
int SigS0()
{
   if(!InpUseBase) return 0;
   int tr = TrendDir();
   if(tr == 0) return 0;
   if(tr ==  1 && rsi[1] < InpRsiBuyBelow)  return  1;
   if(tr == -1 && rsi[1] > InpRsiSellAbove) return -1;
   return 0;
}
//--- S1: M15 trend + the candle touches the Bollinger band + ADX + no spike
int SigS1()
{
   if(!InpUseS1 || hBB == INVALID_HANDLE) return 0;
   int tr = TrendDir();
   if(tr == 0 || !NoSpike()) return 0;
   if(InpAdxMin > 0 && adx[1] < InpAdxMin) return 0;
   double lo1 = iLow(_Symbol, PERIOD_M5, 1), hi1 = iHigh(_Symbol, PERIOD_M5, 1);
   if(tr ==  1 && lo1 <= bbL[1]) return  1;
   if(tr == -1 && hi1 >= bbU[1]) return -1;
   return 0;
}
//--- S2: H1 trend + a deep RSI pullback + no spike
int SigS2()
{
   if(!InpUseS2 || hH1F == INVALID_HANDLE) return 0;
   int tr = TrendOf(h1F, h1S, PERIOD_H1);
   if(tr == 0 || !NoSpike()) return 0;
   if(tr ==  1 && rsi[1] < InpS2Rsi)         return  1;
   if(tr == -1 && rsi[1] > 100.0 - InpS2Rsi) return -1;
   return 0;
}
//--- S3: M15 trend + RSI 40/60 + no spike
int SigS3()
{
   if(!InpUseS3) return 0;
   int tr = TrendDir();
   if(tr == 0 || !NoSpike()) return 0;
   if(tr ==  1 && rsi[1] < InpS3Rsi)         return  1;
   if(tr == -1 && rsi[1] > 100.0 - InpS3Rsi) return -1;
   return 0;
}
//--- S4: the slower M15 trend (50/200) + a deep RSI pullback + ADX
int SigS4()
{
   if(!InpUseS4 || hT2F == INVALID_HANDLE) return 0;
   int tr = TrendOf(t2F, t2S, PERIOD_M15);
   if(tr == 0) return 0;
   if(InpAdxMin > 0 && adx[1] < InpAdxMin) return 0;
   if(tr ==  1 && rsi[1] < InpS2Rsi)         return  1;
   if(tr == -1 && rsi[1] > 100.0 - InpS2Rsi) return -1;
   return 0;
}
//--- S5: M15 trend + close at a 12-bar extreme + price outside the Ichimoku cloud
int SigS5()
{
   if(!InpUseS5 || hIch == INVALID_HANDLE || InpExtremeBars < 2) return 0;
   int tr = TrendDir();
   if(tr == 0) return 0;
   double c1  = iClose(_Symbol, PERIOD_M5, 1);
   double top = MathMax(spA[1], spB[1]), bot = MathMin(spA[1], spB[1]);
   int li = iLowest (_Symbol, PERIOD_M5, MODE_LOW,  InpExtremeBars, 2);
   int hi = iHighest(_Symbol, PERIOD_M5, MODE_HIGH, InpExtremeBars, 2);
   if(li < 0 || hi < 0) return 0;
   if(tr ==  1 && c1 <= iLow (_Symbol, PERIOD_M5, li) && c1 > top) return  1;
   if(tr == -1 && c1 >= iHigh(_Symbol, PERIOD_M5, hi) && c1 < bot) return -1;
   return 0;
}
//+------------------------------------------------------------------+
//| v10.0: volatility floor that follows the market.                  |
//| Returns the ATR value the current candle has to beat.             |
//| Mode 0 = the old fixed number. Mode 1 = the InpAtrPctile-th       |
//| percentile of the last InpAtrLookback candles' ATR, which rises   |
//| in a busy market and falls in a quiet one.                        |
//+------------------------------------------------------------------+
double AtrFloorNow()
{
   if(InpAtrMinMode == 0) return InpAtrMin;
   int n = InpAtrLookback;
   if(n < 50) return InpAtrMin;
   if(CopyBuffer(hAtr, 0, 1, n, atrL) < n) return InpAtrMin;   // not enough history yet -> old behaviour
   double cur = atr[1];
   int below = 0;
   for(int i = 0; i < n; i++) if(atrL[i] < cur) below++;
   double rank = 100.0 * below / n;
   if(rank < InpAtrPctile) return cur + 1.0;      // below its own percentile -> fail the test
   //--- passes the percentile test; the hard floor still applies (v40: in % of price by default)
   if(InpAtrHardMinPct > 0) return iClose(_Symbol, PERIOD_M5, 1) * InpAtrHardMinPct / 100.0;
   return MathMax(InpAtrHardMin, 0.0);
}
//+------------------------------------------------------------------+
string BlockReport()
{
   return StringFormat("signals %d -> entries %d | blocked: hours %d, maxpos %d, ADX %d, spike %d, ATR %d, range %d, spread %d | B1 entries %d",
                       (int)gSignals, (int)gEntries, (int)gBlkHours, (int)gBlkMaxPos, (int)gBlkAdx,
                       (int)gBlkSpike, (int)gBlkAtr, (int)gBlkRange, (int)gBlkSpread, (int)gBreakEntries);
}
//+------------------------------------------------------------------+
void ShowPanel()
{
   string s = "XAU HiWin v43 |  A: TP " + DoubleToString(InpTPatr, 1) +
              " ATR / SL " + DoubleToString(InpSLatr, 1) + " ATR\n";
   s += "Mode: " + (gMode == HW_AUTO ? "AUTO" : "SIGNALS ONLY") + "\n";
   s += "Spread: " + IntegerToString((int)SymbolInfoInteger(_Symbol, SYMBOL_SPREAD)) + " pts\n";
   s += "Open positions: " + IntegerToString(CountAllPositions()) + " / " +
        IntegerToString(InpMaxTotalPositions) + " (originals " + IntegerToString(CountPositions()) + ")" +
        "  |  pending: " + IntegerToString(CountPendings()) + "\n";
   s += "Open risk if all stops hit: " + DoubleToString(OpenRiskPct(), 1) + "% of equity (cap " +
        DoubleToString(InpMaxOpenRiskPct, 0) + "%)\n";
   s += "Today: " + DoubleToString(AccountInfoDouble(ACCOUNT_BALANCE) - gDayStart, 2) +
        (gDayLocked ? "  [LOCKED]" : "") + "\n";
   s += "ATR now: " + DoubleToString(ArraySize(atr) > 1 ? atr[1] : 0.0, 2) + "  |  floor: " +
        (InpAtrMinMode == 0 ? DoubleToString(InpAtrMin, 2) : DoubleToString(gAtrFloor, 2) + " (adaptive)") + "\n";
   s += "Filters: " + BlockReport() + "\n";
   s += "Engine B: " + IntegerToString(CountBreakout()) + " / " + IntegerToString(InpBreakMaxPos) +
        " open, " + IntegerToString((int)gBreakEntries) + " taken, " +
        IntegerToString((int)gBreakTrails) + " trail moves\n";
   s += "Status: " + gStatus;
   Comment(s);
}
//+------------------------------------------------------------------+
void OnTradeTransaction(const MqlTradeTransaction &trans,
                        const MqlTradeRequest &request,
                        const MqlTradeResult &result)
{
   if(trans.type != TRADE_TRANSACTION_DEAL_ADD) return;
   ulong deal = trans.deal;
   if(deal == 0 || !HistoryDealSelect(deal)) return;
   if(HistoryDealGetString(deal, DEAL_SYMBOL) != _Symbol) return;
   if(HistoryDealGetInteger(deal, DEAL_MAGIC) != InpMagic) return;
   if(HistoryDealGetInteger(deal, DEAL_ENTRY) != DEAL_ENTRY_OUT) return;
   CsvClosed(deal);   // v39

   double pl = HistoryDealGetDouble(deal, DEAL_PROFIT) + HistoryDealGetDouble(deal, DEAL_SWAP)
             + HistoryDealGetDouble(deal, DEAL_COMMISSION);
   Alarm(StringFormat("CLOSED %s %s lot @ %s | P/L %s", _Symbol,
                      DoubleToString(HistoryDealGetDouble(deal, DEAL_VOLUME), 2),
                      DoubleToString(HistoryDealGetDouble(deal, DEAL_PRICE), _Digits),
                      DoubleToString(pl, 2)));
}
//+------------------------------------------------------------------+
void OnTick()
{
   if(gMode == HW_AUTO)
   {
      UpdateDay();

      //--- panic button first: nothing else matters if the account is bleeding
      if(InpEmergencyFloatPct > 0)
      {
         double eq = AccountInfoDouble(ACCOUNT_EQUITY);
         double fl = FloatingPL();
         if(eq > 0 && fl < 0 && (-fl / eq * 100.0) >= InpEmergencyFloatPct)
         {
            CloseEverything("floating loss " + DoubleToString(-fl / eq * 100.0, 1) + "% of equity");
            gDayLocked = true;
            GlobalVariableSet(GVK("Locked"), 1);
         }
      }

      TrackPositions();            // v39: MAE / MFE for the CSV log
      ManageTimeStop();
      ManageBreakout();            // v28
      ManageLondon();              // v42
      ManageRecovery();
      ManagePendings();
   }

   //--- heartbeat
   if(InpHeartbeatMin > 0 && TimeCurrent() - lastBeat >= (long)InpHeartbeatMin * 60)
   {
      lastBeat = TimeCurrent();
      if(lastBeat > 0 && MQLInfoInteger(MQL_TESTER) == 0)
         Alarm("alive | open " + IntegerToString(CountPositions()) + " | " + gStatus);
   }

   //--- once per new M5 candle
   datetime barT = iTime(_Symbol, PERIOD_M5, 0);
   if(barT == lastBar) return;
   lastBar = barT;

   if(gMode == HW_AUTO &&
      (!TerminalInfoInteger(TERMINAL_TRADE_ALLOWED) || !MQLInfoInteger(MQL_TRADE_ALLOWED)))
   { gStatus = "Algo trading is OFF"; ShowPanel(); return; }

   if(!LoadData())
   { gStatus = "Loading data..."; ShowPanel(); return; }

   CheckTrend();   // v43: engine T trades around the clock, once per new H1 candle

   //--- hour of the signal candle (the candle that just closed)
   MqlDateTime sig;
   TimeToStruct(VT(iTime(_Symbol, PERIOD_M5, 1)), sig);
   if(HourBlocked(sig.hour)) return;
   if(sig.hour < InpStartHour || sig.hour > InpEndHour)
   { gStatus = "Outside trading hours"; gBlkHours++; ShowPanel(); return; }

   MqlDateTime now;
   TimeToStruct(VT(TimeCurrent()), now);
   if(InpFridayFilter && now.day_of_week == 5 && now.hour >= InpFridayStopHour)
   { gStatus = "Friday: no new trades"; ShowPanel(); return; }

   if(gDayLocked)
   { gStatus = "Daily loss limit: locked until tomorrow"; ShowPanel(); return; }

   if(IsHoliday())
   { gStatus = "Holiday: no trading today"; ShowPanel(); return; }

   //--- v28: ENGINE B runs FIRST and on its own budget. It has to be before the
   //--- scalper's position gate, or a book full of scalps would hide every
   //--- breakout; and before the spike filter, which exists to reject exactly
   //--- the candle this engine is looking for.
   if(gMode == HW_AUTO && InpUseBreakout && CountBreakout() < InpBreakMaxPos)
   {
      bool cooled = true;
      if(InpBreakCooldown > 0 && gLastBreak > 0)
         cooled = (iTime(_Symbol, PERIOD_M5, 0) - gLastBreak) >= (long)InpBreakCooldown * 300;
      if(cooled)
      {
         int bdir = SigBreakout();
         if(bdir != 0)
         {
            double bspread = SymbolInfoDouble(_Symbol, SYMBOL_ASK) - SymbolInfoDouble(_Symbol, SYMBOL_BID);
            if(InpMaxSpreadATR <= 0 || atr[1] <= 0 || bspread <= InpMaxSpreadATR * atr[1])
               OpenBreakout(bdir);
            else gStatus = "B1 skipped: spread too wide";
         }
      }
   }

   //--- v42: ENGINE L, own budget, before the scalper's position gate
   CheckLondon();

   //--- v13: the cap is checked on EVERY position this EA holds, legs included,
   //--- so a group of one original + one leg really does fill the book.
   if(gMode == HW_AUTO &&
      (CountPositions() + CountPendings() >= InpMaxPositions ||
       (InpMaxTotalPositions > 0 && CountAllPositions() + CountPendings() >= InpMaxTotalPositions)))
   { gStatus = "Max positions open"; gBlkMaxPos++; ShowPanel(); return; }

   gStatus = "Waiting for a setup";
   int dir = 0;
   string tag = "";
   if(dir == 0) { dir = SigS1(); if(dir != 0) tag = "S1"; }
   if(dir == 0) { dir = SigS5(); if(dir != 0) tag = "S5"; }
   if(dir == 0) { dir = SigS3(); if(dir != 0) tag = "S3"; }
   if(dir == 0) { dir = SigS0(); if(dir != 0) tag = "S0"; }
   if(dir == 0) { dir = SigS2(); if(dir != 0) tag = "S2"; }
   if(dir == 0) { dir = SigS4(); if(dir != 0) tag = "S4"; }
   if(dir != 0) gStatus = tag + " signal";
   if(dir != 0) gSignals++;
   if(dir != 0 && tag != "S1" && tag != "S4" && InpAdxMin > 0 && adx[1] < InpAdxMin)
   { gStatus = "Skipped: weak trend (M5 ADX " + DoubleToString(adx[1], 1) + ")"; gBlkAdx++; dir = 0; }
   if(dir != 0 && InpSpikeMult > 0)
   {
      double sum = 0;
      for(int q = 2; q <= 51; q++) sum += atr[q];
      if(atr[1] > InpSpikeMult * sum / 50.0)
      { gStatus = "Skipped: volatility spike"; gBlkSpike++; dir = 0; }
   }
   if(dir != 0)
   {
      gAtrFloor = AtrFloorNow();
      if(gAtrFloor > 0 && atr[1] < gAtrFloor)
      {
         gStatus = "Skipped: low volatility (ATR " + DoubleToString(atr[1], 2) +
                   " < floor " + DoubleToString(gAtrFloor, 2) + ")";
         gBlkAtr++; dir = 0;
      }
   }
   if(dir != 0 && InpRangeBars > 0)
   {
      int hi = iHighest(_Symbol, PERIOD_M5, MODE_HIGH, InpRangeBars + 1, 1);
      int lo = iLowest (_Symbol, PERIOD_M5, MODE_LOW,  InpRangeBars + 1, 1);
      if(hi >= 0 && lo >= 0)
      {
         double rng = (iHigh(_Symbol, PERIOD_M5, hi) - iLow(_Symbol, PERIOD_M5, lo)) / atr[1];
         if(rng < InpRangeMinATR)
         { gStatus = "Skipped: dead market (range " + DoubleToString(rng, 2) + " ATR)"; gBlkRange++; dir = 0; }
      }
   }
   if(dir != 0) { gEntries++; OpenTrade(dir, tag); }

   ShowPanel();
}
//+------------------------------------------------------------------+
