# Systematizing Active Momentum: A Quantitative Dissection of the Porterhouse Strategy and Fidelity-Based Replication

## The Empirical Case for Systematic Momentum

Within the rigorous domain of quantitative finance, momentum investing is frequently characterized as the premier market anomaly. It operates on a foundational premise that inherently contradicts the traditional, orthodox value investing paradigm of buying low and selling high. Instead, momentum capitalizes on the persistent, well-documented behavioral tendency of financial markets to underreact to positive fundamental news and structural shifts, establishing a framework where investors systematically buy high with the explicit mathematical intention of selling even higher.

This anomaly, initially formalized in the seminal 1993 academic research by Narasimhan Jegadeesh and Sheridan Titman, demonstrated empirically that buying recent equity winners while simultaneously avoiding historical laggards yields persistent outperformance across multiple asset classes and market cycles. Subsequent quantitative research by industry pioneers extended these findings, proving beyond reasonable doubt that momentum is not merely a statistical artifact of data mining, but a structural inefficiency driven by immutable human psychology.

Despite the overwhelming empirical evidence supporting the momentum factor, it remains a psychologically agonizing strategy for human discretionary managers to execute consistently. The behavioral finance concept known as the disposition effect reveals that human investors possess an overwhelming natural impulse to sell winning positions prematurely in order to lock in psychological victories and realize gains, while simultaneously holding or actively adding to losing positions in hopes of a mean-reverting recovery. This tendency—often described colloquially in the industry as "pulling out the flowers to water the weeds"—fatally undermines the compounding potential of long-term equity market leaders. The psychological friction of paying a higher price today for a security that traded at a massive discount only months prior prevents the vast majority of retail and institutional participants from participating in prolonged secular advances.

To override these cognitive biases, contemporary wealth managers have increasingly turned to strictly quantitative, rules-based selection models that remove the human element from the execution timeline. In May 2026, Ritholtz Wealth Management, a registered investment advisor overseeing more than $7.6 billion in assets, announced a strategic partnership with global asset manager Franklin Templeton to launch a proprietary, active equity separately managed account (SMA) known as the **Porterhouse Portfolio Strategy**. Designed explicitly to systematically hunt and hold the best-performing stocks in the market without emotional interference, the strategy offers a masterclass in modern dual-factor momentum implementation.

For the sophisticated self-directed investor, the mechanics of this institutional-grade strategy need not remain locked behind high-net-worth advisory minimums. By understanding the precise fundamental hurdles, technical momentum indicators, and absolute cash rules that govern the Porterhouse framework, an investor can algorithmically replicate the strategy. Utilizing the customized indexing capabilities of Fidelity Basket Portfolios, the deep filtering of the Fidelity Stock Screener, and the analytical orchestration of advanced large language models like Claude, the modern investor can construct a highly disciplined, monthly-rebalanced momentum engine scaled for upwards of forty securities.

## The Genesis of Porterhouse and the Elimination of Behavioral Friction

The foundational philosophy behind the Porterhouse strategy evolved directly from a long-running, rigorous internal research initiative at Ritholtz Wealth Management known colloquially as the "Best Stocks in the Market" methodology, developed by analysts Sean Russo and Josh Brown. The strategy's nomenclature—Porterhouse—was chosen as a deliberate, evocative culinary metaphor to contrast against diversified, broad-market approaches that seek to own a diluted sampling of the entire economic landscape.

Just as a patron at a high-end steakhouse does not order a sampler platter when they desire the absolute premium cut of meat, this strategy explicitly rejects the notion of owning everything. It is engineered to capture sustained advances by holding only the market's absolute leaders, providing a highly concentrated portfolio of strictly the most robust equities.

The primary objective of the strategy is not to predict the future macroeconomic environment, but to build an algorithmic system capable of ruthlessly responding to the present reality. Human investors constantly struggle to hold onto major winners because they demand perfect clarity behind the macroeconomic story driving the price action; they wait for the perfect narrative to validate the breakout, and by the time the narrative is clear, the alpha has been entirely extracted by early participants.

The quantitative methodology dictates that when a stock, or an entire sub-industry group, breaks to new 52-week highs and exhibits surging relative strength, the correct action is to simply execute the purchase without waiting for complete fundamental clarity. The edge lies in the structural discipline of the entry, combined with the merciless execution of the exit when the trend eventually fails.

## Architectural Framework: The Canvas Direct Indexing Platform

The Porterhouse strategy represents a significant structural departure from the mechanics of traditional passive momentum exchange-traded funds (ETFs) that populate the retail landscape. The strategy's foundational architecture was originally built upon Canvas, an interactive, web-based custom indexing platform originally developed by quantitative pioneer O'Shaughnessy Asset Management (OSAM) and subsequently acquired by Franklin Templeton, which manages approximately $1.7 trillion in global assets.

The deployment of this strategy through a Separately Managed Account rather than a traditional pooled vehicle provides profound advantages in flexibility, tax efficiency, and mandate execution.

Canvas operates as an end-to-end portfolio management system that empowers the creation of highly personalized, tax-aware portfolios at scale through the specific mechanics of direct indexing. Rather than forcing clients into pooled investment vehicles like mutual funds or ETFs, the Canvas platform allocates capital directly into the individual underlying securities. This structural distinction is paramount for a high-turnover strategy like active momentum.

Owning the individual equities directly allows the quantitative engine to continuously monitor and harvest tax losses on a daily basis, aggressively managing the capital gains generated by the frequent trading inherent to momentum investing. When a momentum strategy requires exiting a position that has suffered a rapid reversal, the direct indexing structure allows the investor to capture that specific capital loss to offset gains captured elsewhere in the portfolio, a mechanism entirely unavailable within the pooled structure of a mutual fund.

Furthermore, the decision to deploy the Porterhouse strategy as an SMA provides several critical strategic advantages, primarily revolving around the concept of absolute versus relative momentum. Traditional momentum ETFs are structurally constrained by their regulatory prospectuses, which almost universally enforce a "fully invested" mandate. This means that during a severe, protracted bear market or a systemic liquidity crisis, a traditional momentum ETF is forced to utilize relative momentum—meaning it must buy and hold the stocks that are simply declining less rapidly than their peers.

If the broader market is collapsing, these funds are frequently jammed into defensive sectors such as consumer staples, healthcare, or utilities purely because they offer a slight relative outperformance, despite suffering absolute negative returns that destroy client wealth. The Porterhouse architecture explicitly rejects this relative momentum constraint, operating under strict absolute momentum rules that permit cash reallocation.

| Architectural Feature | Traditional Momentum ETF | Custom Direct Indexing (Porterhouse/Fidelity) |
|---|---|---|
| Ownership Structure | Pooled investment vehicle | Direct ownership of individual securities |
| Tax Management | Inefficient, handled at the fund level | Account-level, highly efficient tax-loss harvesting |
| Market Exposure Constraint | Fully invested mandate required by prospectus | Flexible capital allocation permitted |
| Bear Market Methodology | Employs Relative Momentum (buys "least bad" stocks) | Employs Absolute Momentum (retreats to cash/Treasuries) |
| Reconstitution Velocity | Typically quarterly, semi-annually, or annually | Evaluated monthly for rapid trend adaptation |

## The Quantitative Vanguard: Dual-Factor Selection Methodology

Unlike rudimentary momentum systems that rely exclusively on raw price trends and trailing returns, the modern selection model utilizes a sophisticated dual-factor approach. It demands that a security exhibit not only blistering technical price momentum but also robust, verifiable underlying fundamental business quality. This dual mandate ensures that the portfolio is not filled with low-quality, speculative equities rising purely on retail euphoria or short-squeeze dynamics, but rather targets substantial businesses whose price appreciation is supported by underlying economic realities.

### Liquidity Constraints and the Russell 1000 Universe

To ensure adequate liquidity, institutional sponsorship, and to avoid the extreme volatility associated with micro-cap equities, the strategy establishes a strict initial boundary condition. The investable universe is stringently limited to the top 50 percent of the Russell 1000 Index. By restricting the screening pool to roughly the 500 largest publicly traded companies in the United States, the strategy ensures that it is riding the momentum of mature, highly capitalized enterprises.

This liquidity constraint is vital for a strategy that requires monthly rebalancing, as moving substantial capital into illiquid small-cap names can result in severe slippage, eroding the alpha generated by the momentum factor. This boundary condition provides the initial funnel through which all subsequent fundamental and technical filters are applied.

### Fundamental Floor: Earnings, Cash Flow, and the HALO Framework

For a stock to transition from the broader large-cap universe onto the strategy's high-conviction buy list, it must first survive a rigorous fundamental gauntlet designed to filter out fundamentally flawed enterprises. The quantitative engine screens heavily for companies demonstrating superior earnings strength, sustained revenue growth, and pristine cash flow generation. This fundamental floor is essential for separating genuine, sustainable business momentum from ephemeral, hype-driven price spikes.

The emphasis on cash flow analysis, specifically, provides a more reliable metric than traditional earnings per share. In the realm of quantitative screening, the **Price-to-Cash-Flow (P/CF) ratio** is vastly preferred because raw cash generation is significantly harder for corporate accountants to manipulate than Generally Accepted Accounting Principles (GAAP) earnings. By demanding that a company exhibit top-tier cash flow metrics, the strategy ensures that the underlying enterprise possesses the actual financial liquidity to fund future growth, pay dividends, or execute share buybacks, all of which provide a fundamental tailwind that supports the technical price momentum.

#### The HALO Framework: Heavy Assets, Low Obsolescence

Beyond these basic quantitative metrics, the underlying research methodology applies a highly sophisticated qualitative thematic overlay to its fundamental selection, heavily prioritizing a framework designated as **HALO**—**Heavy Assets, Low Obsolescence**. Developed in direct response to the rapid proliferation of artificial intelligence, machine learning, and advanced large language models, the HALO framework seeks to identify businesses that are functionally and structurally immune to digital disruption.

The fundamental litmus test for a HALO security questions whether an artificial intelligence chatbot, language model, or generative code could conceivably eliminate the need for the company's core product or service in the near or intermediate future. If the answer is yes, or even a plausible maybe, the stock is immediately discarded from consideration.

To successfully pass this fundamental hurdle, the company must possess physical, tangible, "heavy" assets. This includes:

- Expansive physical logistics networks
- Immense physical retail footprints
- Raw material extraction capabilities
- Massive physical inventory that requires real-world movement and storage

Examples of such non-obviated needs include concrete manufacturing, senior living facilities, aerospace components, raw energy refining, and physical retail goods like groceries or tires.

Crucially, the HALO framework does not merely seek companies that are hiding from technological advancement in analog industries; rather, it actively identifies enterprises where artificial intelligence acts as a massive margin-expanding catalyst rather than an existential threat. Companies that clear this fundamental hurdle are uniquely positioned to utilize automation and machine learning to streamline their vast physical operations, lower human labor costs, and expand profit margins.

Because their core physical products remain fundamentally irreplaceable by software code, the implementation of AI serves only to enhance their operational efficiency. Historical candidates passing these rigorous fundamental tests have included:

- Robust infrastructure materials providers (Martin Marietta, Vulcan Materials)
- Diversified global hospitality chains (Marriott)
- Legacy energy refiners (Phillips 66)
- Dominant global logistics retailers (Walmart)

## Technical Confirmation: Absolute Momentum and Market Leadership

Satisfying the fundamental quality constraints and thematic HALO criteria merely grants a stock the right to be evaluated for its technical merit. The strategy's defining characteristic is its ruthless, unyielding demand for absolute price momentum. The foundational technical rule is that the stock must be actively trending higher—described visually in technical analysis parlance as moving steadily "up and to the right" on a standard price chart.

The strategy evaluates these technical signals on a strict monthly basis, acknowledging that momentum is an incredibly fast-moving factor that requires constant vigilance. While traditional smart-beta indices may wait for an annual or semi-annual reconstitution to refresh their holdings—a structural flaw that often results in holding onto decaying, negative-returning trends for months too long—the Porterhouse model re-evaluates its trend strength every thirty days to ensure it is holding nothing but current market leaders.

While the exact proprietary algorithms and customized lookback weightings of the OSAM Canvas platform are heavily guarded institutional secrets, the technical indicators utilized to identify the "Best Stocks in the Market" rely on deeply established quantitative metrics that can be analyzed and understood.

### The Three Pillars of Technical Analysis

#### Pillar 1: Intermediate-to-Long-Term Trend Alignment

The strategy relies heavily on moving average crossovers to confirm trend persistence and eliminate market noise. Specifically, the relationship between the 50-day simple moving average and the 200-day simple moving average is a critical determinant of a stock's technical health.

A stock trading consistently above a rising 200-day moving average, with the 50-day moving average serving as dynamic, rising support, is viewed as being in a confirmed **Stage 2 structural uptrend**. Any violation of these moving averages suggests a transition from accumulation to distribution, triggering immediate technical warnings.

#### Pillar 2: Momentum Velocity and RSI Dynamics

Momentum requires velocity, and the **Relative Strength Index (RSI)** is utilized to gauge the speed, magnitude, and change of price movements over localized periods. Conventional retail trading wisdom often views an RSI above 70 strictly as a bearish "overbought" signal that demands immediate selling. However, robust institutional momentum strategies interpret prolonged, elevated RSI readings as a confirmation of immense buying pressure and structural institutional accumulation.

The strategy particularly favors stocks that have:

1. Reached new 52-week highs
2. Pushed the RSI into the high 60s or 70s
3. Demonstrated a healthy technical "coiling" or consolidation phase where the RSI cools off slightly without the underlying price suffering a devastating drawdown

This setup frequently precedes the next explosive leg higher, indicating that the asset has digested its recent gains and is preparing for further expansion.

#### Pillar 3: Momentum Lookback Periods and Trend Strength

The quantitative engine analyzes momentum lookback periods to establish trend strength. Quantitative literature, including research pioneered by entities like O'Shaughnessy, indicates that simple one-month price returns capture too much mean-reverting noise. Instead, the sweet spot for equity momentum evaluation typically resides between the six-month and twelve-month lookback windows.

By analyzing the cross-sectional momentum of assets over 3-month, 6-month, and 9-month horizons, the strategy identifies equities exhibiting persistent, durable strength rather than fleeting, news-driven volatility. Furthermore, when multiple large-cap constituents within a highly specific sub-industry—described as "Russian-doll style" sector nesting—simultaneously shatter 52-week highs and exhibit surging relative strength, it provides a systemic, macroeconomic confirmation of the trend.

## Dynamic Asset Allocation: The Cash Accordion and Absolute Sell Disciplines

The true, durable edge of a systematic momentum strategy does not lie merely in the ability to identify which stocks will rise, but rather in its unwavering, algorithmic response to shifting market conditions and deteriorating trends. The strategy is engineered to act as an expanding and contracting accordion, dynamically adjusting its risk exposure based on the abundance or scarcity of verifiable market leadership. This variable exposure is the core mechanism of absolute momentum, separating it from the flawed mandates of fully-invested funds.

### Risk-On Environments: Portfolio Expansion

During robust, broad-based bull markets where capital is flowing freely and numerous economic sectors are participating in the advance, the screening algorithm will identify a massive surplus of companies meeting both the fundamental and technical dual-factor criteria. In this risk-on environment, the portfolio naturally expands its holdings.

If the mandate allows for upwards of forty securities, the portfolio will comfortably hold forty high-conviction names, maximizing its exposure to the equity risk premium and compounding capital at maximum velocity.

### Risk-Off Environments: The Sell Discipline

However, as the business cycle eventually matures and market internals begin to inevitably deteriorate, equity leadership narrows. Fewer and fewer stocks are able to maintain their 50-day moving averages, sustain high RSI readings, or generate top-quartile cash flows. When this occurs, the strategy enforces its strict sell discipline without emotional hesitation.

The criteria for exiting a position are fundamentally different from the criteria for entry. A stock is ruthlessly excised from the portfolio the moment its technical trend definitively breaks—whether through:

- A catastrophic violation of its long-term moving averages
- A prolonged period of severe relative underperformance compared to the benchmark
- A fundamental deterioration in its earnings trajectory

### The Cash Accordion and Treasury Allocation

Because the strategy operates under an absolute momentum mandate without relative constraints, the capital harvested from these liquidations is not blindly redeployed into the next-best, deteriorating equity. If the screening algorithm searches the market and cannot find replacement equities that meet the rigorous entry hurdles, the total number of holdings in the portfolio systematically shrinks.

The capital generated from selling the broken momentum stocks is immediately rotated out of the equity market and into short-term United States Treasuries or cash equivalents.

This absolute momentum cash-accordion rule ensures that the portfolio systematically de-risks during choppy, highly volatile, or structurally bearish markets. In extreme scenarios, such as a localized financial crisis or a deep structural recession where correlations approach one and all equities suffer catastrophic drawdowns, the strategy is theoretically capable of reducing its equity exposure to zero.

In such a scenario, the portfolio would rest entirely in risk-free Treasury yields, preserving capital and sidestepping the devastation until authentic, fundamentally supported price momentum re-emerges in the equity market. This methodology requires immense psychological discipline from the investor, as it inherently means the portfolio will occasionally experience behavioral whipsaws—such as selling a stock that ultimately recovers, or sitting safely in cash during the initial, highly volatile stages of a market bottom.

However, this is the accepted mathematical tradeoff required to avoid prolonged, capital-destroying drawdowns. The objective is not to catch the exact bottom, but to capture the sustained meat of the trend.

## Fidelity Implementation Pipeline: Screener Architecture for a 40-Stock Portfolio

For the self-directed investor seeking to implement this precise dual-factor momentum philosophy without paying the management fees associated with an institutional SMA, the technological ecosystem provided by Fidelity Investments offers all the necessary infrastructure for comprehensive replication. Successfully executing this strategy for a target portfolio of upwards of forty securities requires combining the quantitative filtering capabilities of the robust Fidelity Stock Screener with the execution architecture of Fidelity Basket Portfolios.

### Monthly Execution and Screening Process

The monthly execution of this active strategy begins with running a strict, multi-variable query through the Fidelity Stock Screener to generate the new target "buy list". The screener allows retail and institutional investors to filter through a massive universe of over 10,000 global equities using more than 140 customizable criteria, including proprietary fundamental ratings provided by S&P Global and technical overlays powered by Recognia.

To effectively emulate the dual-factor criteria of the target strategy, the investor must rigorously configure the screener across several dimensions to isolate large-cap, high-quality momentum equities.

### Configuration Dimensions

#### 1. The Universe and Liquidity Constraint

To mirror the top 50 percent of the Russell 1000 index, the screener's Market Capitalization filter must be aggressively set to exclude all small-cap and micro-cap equities. Setting a minimum market capitalization threshold of **$15 billion to $20 billion** ensures the screening universe is restricted exclusively to large-cap and mega-cap enterprises. This eliminates the noise of low-float penny stocks that may exhibit false momentum due to retail manipulation.

#### 2. The Fundamental Quality Overlay

Fidelity provides access to deep fundamental metrics that can expertly proxy the cash flow and earnings requirements demanded by the institutional methodology.

**Earnings Growth:** The screener must be configured to require positive trailing and forward-projected Earnings Per Share (EPS) growth, ensuring the company is actually expanding its profitability.

**Cash Flow Quality:** Utilizing the Price-to-Cash-Flow (P/CF) ratio metric is paramount. Because cash flow is highly resistant to accounting manipulation, setting the screener to seek companies ranking in the top percentiles for cash flow generation ensures a robust, undeniable fundamental foundation. Fidelity's screener allows users to sort specifically for stocks scoring "better than 80% of all stocks in universe" on these specific fundamental metrics.

**S&P Global Quality Scores:** Fidelity deeply integrates fundamental analysis scores from S&P Global that quantitatively assess valuation, quality, growth stability, and overall financial health. Implementing a strict filter that only accepts stocks with high quantitative quality scores ensures the fundamental side of the dual-factor model is fully satisfied.

#### 3. The Technical Momentum Triggers

Fidelity's screener includes highly specific technical pattern and indicator filters, allowing the user to precisely isolate absolute momentum and trend strength without needing external charting software.

**Price Action & Highs:** The screener must be configured to identify stocks that are currently trading within a very close percentage (e.g., 5%) of their 52-week or 6-month absolute price highs, confirming they are participating in the current market leadership.

**Relative Strength Index (RSI) Dynamics:** Fidelity allows for highly specific RSI filtering. To locate equities that have exhibited massive recent strength but are not immediately exhausted, the investor can utilize the proprietary "Relative Strength Index Turnover" filter. This advanced filter specifically identifies stocks that have:

- Hit a 6-month price high recently
- Achieved an RSI of at least 70 (indicating immense, undeniable buying pressure)
- Subsequently seen their RSI cool off by at least 5% (indicating a healthy, required consolidation phase without breaking the primary price trend)

**Moving Averages:** Applying a baseline filter requiring:

- Current stock price > 50-day Simple Moving Average (SMA)
- 50-day SMA > 200-day SMA

This perfectly encapsulates the necessary structural uptrend requirement.

### Fidelity Screener Configuration Reference

| Fidelity Screener Dimension | Specific Parameter Setting | Rationale for Strategy Emulation |
|---|---|---|
| Liquidity & Size | Market Capitalization > $20 Billion | Emulates top 50% of Russell 1000, ensures liquidity |
| Fundamental Health | Positive EPS Growth, Top Quartile Price/Cash Flow | Avoids low-quality, speculative momentum traps |
| Trend Persistence | Current Price > 50-day SMA > 200-day SMA | Ensures absolute, structural Stage 2 uptrend |
| Momentum Velocity | RSI 14-day Turnover Filter (Hit 70, pulled back 5%) | Confirms buying pressure, identifies healthy consolidation |
| Price Proximity | Current Price within 5% of 52-week high | Verifies current market leadership and breakout status |

### Execution Timing

By executing this sophisticated, multi-layered query on the final trading day of every month, the investor generates a condensed, high-conviction list of equities that meet the exact theoretical parameters of the target dual-factor strategy, ready for portfolio implementation.

## Operationalizing the Reconstitution via Fidelity Basket Portfolios

Generating the list of forty qualifying momentum equities is only the analytical half of the systematic equation; the operational execution of buying, sizing, selling, and monthly rebalancing is where the strategy historically generates friction for retail investors. To manage a forty-stock portfolio without incurring massive bid-ask friction costs, generating catastrophic tax events, or dedicating countless manual hours to trade execution, the investor must deploy **Fidelity Basket Portfolios**.

For a flat monthly brokerage fee, Fidelity Basket Portfolios empower retail investors to effectively act as their own institutional direct-indexing provider, allowing the creation of custom indices holding between two and fifty individual securities. This upper limit of fifty securities perfectly accommodates the concentrated, forty-stock premium-cut philosophy of the strategy, leaving ample room for cash vehicles.

### The Dynamic Basket Configuration

When initially constructing the momentum basket, the investor inputs the forty ticker symbols that survived the fundamental and technical screening funnel into the Fidelity Basket Portfolio interface. If the market is in a healthy, broad-based uptrend, the investor allocates an equal target weight to each of these equities within the basket (e.g., **2.5% each for 40 stocks**).

Crucially, the investor must also deliberately include a short-term Treasury ETF—such as:

- SPDR Bloomberg 1-3 Month T-Bill ETF (**BIL**)
- iShares Short Treasury Bond ETF (**SHV**)

—as a permanent resident within the basket architecture. In a fully risk-on environment where forty stocks qualify, the target weight for this Treasury ETF is set to 0% or a nominal 1%. This mechanism creates the dormant cash reserve vehicle required for the absolute momentum sell discipline, ready to expand when needed.

### The Monthly Rebalance and the Sell Discipline

Momentum factors decay over time, and macroeconomic regimes shift unexpectedly. To maintain the mathematical integrity of the strategy, the portfolio must be ruthlessly curated on a monthly basis. At the close of each month, the investor must review the current holdings within the Fidelity Basket against the established technical sell rules.

If an existing holding has:

- Violently violated its 50-day moving average
- Suffered a catastrophic drop in relative strength
- Simply no longer appears on the updated Fidelity Stock Screener output

—it has lost its momentum status and must be systematically excised.

### Execution via Fidelity Dashboard

Through the personalized Fidelity dashboard, this execution is highly streamlined. The investor:

1. Selects the specific momentum basket and clicks "Manage"
2. From this interface, deletes offending, broken-trend equities from the basket configuration
3. Simultaneously adds new market leaders that emerged on the current month's screener output to the basket
4. Maintains fixed percentage weightings for retained equity positions
5. Aggressively increases the target weight of the short-term Treasury ETF to absorb excess capital if the market environment is deteriorating

Once the new target weights are established in the interface, the investor executes the massive portfolio update with a single action. By selecting "Rebalance" and clicking "Place order," the Fidelity routing engine:

- Simultaneously calculates the required fractional share adjustments
- Automatically sells the necessary portions of the broken equities
- Intelligently deploys the harvested capital into the new momentum leaders and the Treasury ETF

This single-click execution aligns the real-world account balance perfectly with the new theoretical target weights, eliminating the need for manual spreadsheet calculations and individual trade tickets.

## Mitigating Tax Friction via "Smart Buy" Contributions

One of the most severe structural headwinds to a high-turnover active momentum strategy in a taxable brokerage account is the frequent realization of short-term capital gains, which can severely erode compound returns over a multi-decade horizon. While the retail investor does not have access to the automated, daily tax-loss harvesting algorithms inherent to Franklin Templeton's institutional Canvas platform, they can utilize Fidelity's proprietary **"Smart Buy"** feature to dramatically improve their tax efficiency.

If the investor is adding new external capital to the strategy on a monthly basis (e.g., through recurring payroll deposits), the Smart Buy algorithm automatically analyzes the current real-world basket weights against the prescribed target weights. Instead of executing a traditional, aggressive rebalance—which forces the sale of massive winning stocks to buy the underweights, thereby triggering taxable events—Smart Buy routes 100% of the new inbound cash exclusively toward the most underweight securities in the basket.

By achieving balance through targeted, incoming contributions rather than forced internal liquidations, the investor can maintain their desired momentum weightings while allowing their largest multi-month winners to continue compounding completely tax-deferred. This effectively neutralizes a significant portion of the tax drag associated with momentum strategies unless extreme market movements force a hard sell.

## Algorithmic Orchestration: Deploying Claude as a Systematic Co-Pilot

Managing a dynamic forty-stock portfolio, running continuous multi-factor screens, objectively evaluating absolute sell signals, and calculating precise fractional target weights for cash offsets requires a high degree of quantitative rigor. To completely eliminate human error, override lingering emotional biases, and streamline this complex monthly workflow, the self-directed investor can employ an advanced Large Language Model (LLM)—specifically a high-parameter reasoning engine like Claude—to serve as the programmatic co-pilot and quantitative analyst for the strategy.

By treating the LLM as a systematic engine bound by absolute rules, the monthly reconstitution process can be reduced from hours of manual spreadsheet tracking and emotional deliberation to a highly efficient, ten-minute data pipeline.

### Phase 1: Data Ingestion and The Objective Sell Screen

On the final trading day of the month, the investor:

1. Exports the current holdings of their Fidelity Basket Portfolio as a raw CSV file (containing ticker symbols, current weights, and current market prices)
2. Navigates to the Fidelity Technical Analysis portal
3. Exports the current 50-day moving average and 14-day RSI data for those specific forty tickers

These datasets are fed directly into the Claude LLM interface with a strictly defined, immutable system prompt. Claude is instructed to act as a systematic momentum engine, devoid of macroeconomic opinions. It evaluates the current holdings against the absolute sell rules:

**Quantitative Rule 1:** If the Current Price is less than the 50-day SMA by more than 2%, tag the ticker as **"SELL_VIOLATION"**

**Quantitative Rule 2:** If the 14-day RSI has remained below 45 for two consecutive weeks, tag the ticker as **"SELL_MOMENTUM_DECAY"**

**Quantitative Rule 3:** If Current Price is greater than the 50-day SMA and RSI is greater than 50, tag the ticker as **"HOLD_ACTIVE"**

Claude processes the numerical data array and instantly returns a definitive list of the broken securities that must be excised from the portfolio, completely removing the investor's emotional desire to hold onto a losing position in hopes of a rebound.

### Phase 2: The Buy Screen and Qualitative HALO Verification

Simultaneously, the investor runs the pre-configured Fidelity Stock Screener (Market Cap > $20B, Top Quartile Cash Flow, Price near 52-week high, RSI turnover). The resulting list of new qualifying tickers is exported as a CSV and uploaded into the active Claude session.

Claude is prompted to:

1. Cross-reference the new "buy list" with the retained "HOLD" list from the current portfolio
2. Identify the net-new additions required for the upcoming month
3. Run a rapid semantic analysis on the core business descriptions of the new tickers
4. Flag any companies whose revenue models are highly vulnerable to generative AI obsolescence

If the screener inadvertently returned an educational software company highly vulnerable to AI disruption, Claude flags the ticker as failing the HALO constraint, ensuring only "heavy asset" or "low obsolescence" equities are admitted to the final portfolio.

### Phase 3: Target Weight Generation and the Cash Accordion

The most complex mathematical component of the monthly reconstitution is managing the cash accordion dynamically based on the number of surviving equities. Claude is provided with a fixed set of portfolio sizing logic:

- **Maximum allowable equity positions:** 40
- **Fixed equity weight:** 2.5% per stock (if fully invested)
- **If the sum of qualifying HOLDs and net-new BUYs equals N (where N < 40):**
  - Total equity allocation = N × 2.5%
  - Remaining portfolio percentage = 100% − (N × 2.5%)
  - Assign remainder to designated short-term Treasury ETF (e.g., BIL or SHV)

Claude instantaneously computes the precise target weightings for the new month based on the exact number of stocks surviving the dual-factor screen. It outputs a clean, formatted Markdown table listing every ticker and its required percentage weight, perfectly formatted for manual entry into the Fidelity platform.

### Execution Phase Summary

| Investor Action | Claude (LLM) Orchestration Task |
|---|---|
| **1. Sell Discipline** | Export current holdings & technicals to CSV | Evaluates price vs. SMA/RSI; generates objective "SELL" list |
| **2. Buy Identification** | Run Fidelity Screener, export new list to CSV | Cross-references holdings; applies semantic HALO AI-disruption filter |
| **3. Asset Allocation** | Provide maximum parameters (e.g., 40 stocks) | Calculates N × 2.5% equity weight; assigns remainder to Treasury ETF |
| **4. Final Execution** | Input Claude's target weights into Fidelity | Outputs final, formatted target weight table for seamless platform entry |

Armed with the LLM-generated target weight table, the investor:

1. Logs into the Fidelity dashboard
2. Navigates to the Basket Portfolio and clicks "Manage"
3. Deletes the tickers Claude flagged as "SELL"
4. Inputs the new verified tickers
5. Types in the LLM-calculated target percentages
6. Clicks "Rebalance" and "Place order"

The Fidelity routing engine simultaneously calculates the required fractional share adjustments, automatically sells the necessary portions of the broken equities, and intelligently deploys the harvested capital into the new momentum leaders and the Treasury ETF. This single-click execution aligns the real-world account balance perfectly with the new theoretical target weights, completing the institutional-grade workflow in minutes.

## Conclusion: The Democratization of Systematic Momentum

The historical pursuit of equity market outperformance has been continually derailed by the psychological frailties of the human mind. The disposition effect, the fear of missing out, and the paralyzing dread of bearing losses consistently force discretionary investors to abandon long-term compounding in favor of short-term emotional relief.

The architecture of modern institutional momentum strategies represents a comprehensive, mathematical solution to this behavioral dilemma. By utilizing rigorous dual-factor screening to isolate fundamental quality and absolute price momentum, while employing strict, automated sell disciplines to seamlessly transition to cash when market leadership decays, these systems bypass human emotion entirely.

While the exact proprietary algorithms and the daily tax-loss harvesting mechanics of institutional platforms remain closely guarded structural advantages, the core philosophical and mathematical tenets of the strategy are now fully replicable by the retail public. By synthesizing the deep fundamental and technical filtering capabilities of the Fidelity Stock Screener with the dynamic, one-click execution architecture of Fidelity Basket Portfolios, the disciplined investor can build a highly responsive momentum engine.

Furthermore, when this technological infrastructure is orchestrated by the analytical and computational capabilities of an advanced Large Language Model like Claude, the result is a systematized, emotionless, and mathematically rigorous portfolio management pipeline.

The true edge in modern financial markets is no longer found in futilely attempting to predict the macroeconomic future, but in building the systematic frameworks capable of ruthlessly, algorithmically responding to the undeniable reality of the present.
