'use client';

import React, { useState, useEffect } from "react";
import { ResponsiveGridLayout, useContainerWidth } from "react-grid-layout";
import "react-grid-layout/css/styles.css";
import "react-resizable/css/styles.css";
import { getPortfolio, getTickerHistory } from "../../lib/api";
import { TrendingUp, DollarSign, Activity, Terminal } from "lucide-react";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

interface Holding {
  id: number;
  ticker: string;
  shares: number;
  average_price: number;
  current_price: number;
  market_value: number;
  unrealized_pl: number;
  pl_percent: number;
}

export function ProLayout({ trendData }: { trendData: any[] }) {
  const [portfolio, setPortfolio] = useState<{holdings: Holding[], summary: any} | null>(null);
  const [tickerData, setTickerData] = useState<any[]>([]);
  const [activeTicker, setActiveTicker] = useState<string>('SPY');
  const [isLoading, setIsLoading] = useState(true);
  const { width: containerWidth, containerRef } = useContainerWidth();

  useEffect(() => {
    getPortfolio().then((data) => {
      setPortfolio(data);
      setIsLoading(false);
      
      const defaultTicker = data?.holdings?.length > 0 ? data.holdings[0].ticker : 'SPY';
      setActiveTicker(defaultTicker);
      getTickerHistory(defaultTicker).then(res => setTickerData(res.data)).catch(console.error);
    }).catch((err) => {
      console.error(err);
      setIsLoading(false);
    });
    const interval = setInterval(() => {
      getPortfolio().then(setPortfolio).catch(console.error);
    }, 10000); // Live tick every 10s
    return () => clearInterval(interval);
  }, []);

  const layout = [
    { i: "cashflow", x: 0, y: 0, w: 8, h: 4 },
    { i: "portfolio", x: 8, y: 0, w: 4, h: 4 },
    { i: "ticker", x: 0, y: 4, w: 12, h: 3 }
  ];

  return (
    <div className="bg-[#003049] min-h-screen text-[#669bbc] font-mono p-4" ref={containerRef}>
      <ResponsiveGridLayout
        className="layout"
        width={containerWidth}
        layouts={{ lg: layout, md: layout, sm: layout }}
        breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }}
        cols={{ lg: 12, md: 12, sm: 12, xs: 12, xxs: 12 }}
        rowHeight={80}
        isDraggable={true}
        isResizable={true}
      >
        <div key="cashflow" className="border border-[#669bbc] bg-[#001f30] p-4 overflow-hidden flex flex-col">
          <div className="text-white text-xs uppercase tracking-widest font-bold mb-2 flex items-center gap-2 border-b border-[#669bbc]/30 pb-2">
            <Activity size={14} className="text-[#c1121f]" /> {activeTicker} PERFORMANCE (1Y)
          </div>
          <div className="flex-1 w-full h-full">
            <ResponsiveContainer width="100%" height="100%">
              {/* Using a simple LineChart for ticker representation. */}
              <AreaChart data={tickerData}>
                <XAxis dataKey="date" stroke="#669bbc" fontSize={10} tickLine={false} axisLine={false} />
                <YAxis domain={['auto', 'auto']} stroke="#669bbc" fontSize={10} tickLine={false} axisLine={false} width={40} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#003049', border: '1px solid #669bbc', borderRadius: 0 }}
                  itemStyle={{ color: '#00ff00', fontWeight: 'bold' }}
                />
                <Area type="monotone" dataKey="amount" stroke="#00ff00" fill="url(#colorTicker)" strokeWidth={2} />
                <defs>
                  <linearGradient id="colorTicker" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00ff00" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#00ff00" stopOpacity={0}/>
                  </linearGradient>
                </defs>
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div key="portfolio" className="border border-[#669bbc] bg-[#001f30] p-4 overflow-hidden flex flex-col">
          <div className="text-white text-xs uppercase tracking-widest font-bold mb-2 flex items-center gap-2 border-b border-[#669bbc]/30 pb-2">
            <DollarSign size={14} className="text-green-500" /> PORTFOLIO
          </div>
          <div className="flex-1 overflow-auto">
            <table className="w-full text-left text-xs min-w-[260px]">
              <thead>
                <tr className="text-[#669bbc] border-b border-[#669bbc]/30">
                  <th className="pb-2 pr-3 font-semibold whitespace-nowrap">Ticker</th>
                  <th className="pb-2 px-2 text-right font-semibold whitespace-nowrap">Shares</th>
                  <th className="pb-2 px-2 text-right font-semibold whitespace-nowrap">Price</th>
                  <th className="pb-2 pl-2 text-right font-semibold whitespace-nowrap">P&L</th>
                </tr>
              </thead>
              <tbody>
                {portfolio?.holdings?.map((h, i) => (
                  <tr 
                    key={i} 
                    className="border-b border-[#669bbc]/20 hover:bg-[#003049] cursor-pointer transition-colors"
                    onClick={() => {
                      setActiveTicker(h.ticker);
                      getTickerHistory(h.ticker).then(res => setTickerData(res.data)).catch(console.error);
                    }}
                  >
                    <td className="py-2 pr-3 text-white font-bold whitespace-nowrap">{h.ticker}</td>
                    <td className="py-2 px-2 text-right text-[#669bbc] whitespace-nowrap">{h.shares}</td>
                    <td className="py-2 px-2 text-right whitespace-nowrap">${h.current_price.toFixed(2)}</td>
                    <td className={`py-2 pl-2 text-right font-bold whitespace-nowrap ${h.unrealized_pl >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                      {h.unrealized_pl >= 0 ? '+' : ''}${h.unrealized_pl.toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div key="ticker" className="border border-[#669bbc] bg-[#001f30] p-4 overflow-hidden flex flex-col">
          <div className="text-white text-xs uppercase tracking-widest font-bold mb-2 flex items-center gap-2 border-b border-[#669bbc]/30 pb-2">
            <Terminal size={14} className="text-[#c1121f]" /> SYSTEM LOGS & TICKER
          </div>
          <div className="flex-1 font-mono text-[11px] leading-tight flex flex-col justify-end">
             {portfolio?.holdings?.map((h, i) => (
                <div key={i} className="flex gap-4 items-center">
                  <span className="text-[#669bbc]">[SYSTEM]</span>
                  <span className="text-white">MARKET_DATA_RECV</span>
                  <span className="text-yellow-500 font-bold">{h.ticker}</span>
                  <span>VOL: {h.shares * 100}</span>
                  <span className={h.unrealized_pl >= 0 ? 'text-green-500 animate-pulse' : 'text-red-500 animate-pulse'}>
                    PX: {h.current_price} ({h.pl_percent.toFixed(2)}%)
                  </span>
                </div>
             ))}
             {isLoading && <div className="text-yellow-500 animate-pulse">[SYSTEM] LOADING MARKET DATA (55 TICKERS)...</div>}
             {!isLoading && !portfolio?.holdings?.length && <div className="text-[#669bbc]">[SYSTEM] IDLE. AWAITING MARKET OPEN.</div>}
          </div>
        </div>
      </ResponsiveGridLayout>
    </div>
  );
}
