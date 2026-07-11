'use client';

import { useState, useEffect, useCallback } from 'react';
import { uploadStatement, getTaskStatus, getTransactions, getTrends, getSubscriptions, downloadDemoStatement, getIndianFinancialNews, getCategories } from '../lib/api';
import { SpendingChart } from '../components/dashboard/spending-chart';
import { ChatBot } from '../components/dashboard/chat-bot';
import { Pagination } from '../components/ui/pagination';
import { Upload, FileText, Download, TrendingUp, CreditCard, Loader2, Sparkles, Smile, ShieldAlert, Newspaper } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';

import { ProLayout } from '../components/dashboard/pro-layout';

interface Transaction {
  id: number;
  date: string;
  description: string;
  amount: number;
  category: string;
  is_anomaly: boolean;
}

interface PaginationMeta {
  page: number;
  per_page: number;
  total: number;
  total_pages: number;
}

const TRANSACTIONS_PER_PAGE = 10;
const SUBSCRIPTIONS_PER_PAGE = 6;
const NEWS_PER_PAGE = 4;

export default function Dashboard() {
  const [proMode, setProMode] = useState(false);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [txnPagination, setTxnPagination] = useState<PaginationMeta>({
    page: 1, per_page: TRANSACTIONS_PER_PAGE, total: 0, total_pages: 1,
  });
  const [txnLoading, setTxnLoading] = useState(false);

  const [subscriptions, setSubscriptions] = useState<{ name: string; amount: number; frequency: string }[]>([]);
  const [subsPagination, setSubsPagination] = useState<PaginationMeta>({
    page: 1, per_page: SUBSCRIPTIONS_PER_PAGE, total: 0, total_pages: 1,
  });
  const [subsLoading, setSubsLoading] = useState(false);

  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("");
  const [chartData, setChartData] = useState<{ name: string; value: number }[]>([]);
  const [trendData, setTrendData] = useState<{ date: string; amount: number }[]>([]);
  const [newsData, setNewsData] = useState<{ title: string; link: string; pubDate: string }[]>([]);
  const [newsPage, setNewsPage] = useState(1);

  const fetchTransactions = useCallback(async (page: number) => {
    setTxnLoading(true);
    try {
      const res = await getTransactions(page, TRANSACTIONS_PER_PAGE);
      setTransactions(res.data);
      if (res.pagination) setTxnPagination(res.pagination);
    } catch (error) {
      console.error("Failed to fetch transactions", error);
    } finally {
      setTxnLoading(false);
    }
  }, []);

  const fetchSubscriptions = useCallback(async (page: number) => {
    setSubsLoading(true);
    try {
      const subs = await getSubscriptions(page, SUBSCRIPTIONS_PER_PAGE);
      setSubscriptions(subs.data);
      if (subs.pagination) setSubsPagination(subs.pagination);
    } catch (error) {
      console.error("Failed to fetch subscriptions", error);
    } finally {
      setSubsLoading(false);
    }
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      await Promise.all([
        fetchTransactions(1),
        fetchSubscriptions(1),
        getTrends().then(trends => setTrendData(trends.data)).catch(console.error),
        getIndianFinancialNews()
          .then(news => {
            if (news.data && news.data.length > 0) {
              setNewsData(news.data);
            } else {
              setNewsData([{ title: "No news available at the moment.", link: "#", pubDate: "" }]);
            }
          })
          .catch(err => {
            console.error(err);
            setNewsData([{ title: "Failed to fetch live news feed. Please try again later.", link: "#", pubDate: "" }]);
          }),
        getCategories().then(cat => setChartData(cat.data || [])).catch(console.error),
      ]);
    };
    fetchData();
  }, [fetchTransactions, fetchSubscriptions]);

  useEffect(() => {
    if (proMode) {
      document.body.classList.add('terminal-mode-body');
      document.documentElement.classList.add('terminal-mode-body');
    } else {
      document.body.classList.remove('terminal-mode-body');
      document.documentElement.classList.remove('terminal-mode-body');
    }
    // Cleanup on unmount
    return () => {
      document.body.classList.remove('terminal-mode-body');
      document.documentElement.classList.remove('terminal-mode-body');
    };
  }, [proMode]);

  const processChartData = (data: Transaction[]) => {
    const categoryMap: Record<string, number> = {};
    data.forEach(t => {
      if (categoryMap[t.category]) {
        categoryMap[t.category] += t.amount;
      } else {
        categoryMap[t.category] = t.amount;
      }
    });
    const processed = Object.keys(categoryMap).map(key => ({
      name: key,
      value: categoryMap[key]
    }));
    setChartData(processed);
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files?.[0]) return;
    setUploading(true);
    setUploadStatus("Uploading...");
    
    try {
      const uploadRes = await uploadStatement(e.target.files[0]);
      const taskId = uploadRes.task_id;
      
      if (!taskId) throw new Error("No task_id returned from API");
      
      setUploadStatus("Processing...");
      
      const pollInterval = setInterval(async () => {
        try {
          const statusRes = await getTaskStatus(taskId);
          
          if (statusRes.state === 'SUCCESS') {
            clearInterval(pollInterval);
            setUploading(false);
            setUploadStatus("");
            
            await Promise.all([
              fetchTransactions(1),
              fetchSubscriptions(1),
              getTrends().then(trends => setTrendData(trends.data)).catch(console.error),
            ]);
          } else if (statusRes.state === 'FAILURE') {
            clearInterval(pollInterval);
            setUploading(false);
            setUploadStatus("");
            alert(`Processing failed: ${statusRes.error || 'Server error'}`);
          } else if (statusRes.status) {
            setUploadStatus(statusRes.status);
          }
        } catch (pollError) {
          clearInterval(pollInterval);
          setUploading(false);
          setUploadStatus("");
          console.error("Polling failed", pollError);
        }
      }, 1500);
      
    } catch (error) {
      console.error("Upload failed", error);
      alert("Upload failed!");
      setUploading(false);
      setUploadStatus("");
    }
  };

  const handleTxnPageChange = (page: number) => {
    fetchTransactions(page);
    document.getElementById('transactions-section')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  const handleSubsPageChange = (page: number) => {
    fetchSubscriptions(page);
  };

  const totalSpend = trendData.reduce((acc, curr) => acc + curr.amount, 0);

  return (
    <div className={`min-h-screen pb-20 selection:bg-[#c1121f] selection:text-white transition-colors duration-300 ${proMode ? 'bg-[#003049]' : 'bg-[#fdf0d5]'}`}>
      
      {/* Brutalist Navigation */}
      <nav className={`border-b-4 sticky top-0 z-40 reveal-1 transition-colors ${proMode ? 'border-[#669bbc] bg-[#001f30] text-[#669bbc]' : 'border-[#003049] bg-[#fdf0d5]'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-8 py-4 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className={`w-10 h-10 flex items-center justify-center border-2 ${proMode ? 'bg-[#c1121f] border-[#669bbc]' : 'bg-[#c1121f] border-[#003049]'}`}>
              <span className="text-white font-serif font-bold text-xl leading-none -mt-1">S</span>
            </div>
            <h1 className={`text-3xl font-serif tracking-tight uppercase ${proMode ? 'text-white' : 'text-[#003049]'}`}>SmartSpend</h1>
          </div>
          <div className="flex flex-wrap items-center gap-3 sm:gap-4 font-mono text-xs sm:text-sm">
            <button
              onClick={() => setProMode(!proMode)}
              className={`flex items-center gap-2 px-3 py-2 sm:px-4 border-2 transition-colors uppercase font-bold ${proMode ? 'border-[#669bbc] bg-[#c1121f] text-white hover:bg-[#780000]' : 'border-[#003049] bg-transparent text-[#003049] hover:bg-[#003049] hover:text-white'}`}
            >
              {proMode ? 'Exit Terminal' : 'Terminal'}
            </button>
            <button
              onClick={downloadDemoStatement}
              className={`flex items-center gap-2 px-3 py-2 sm:px-4 border-2 transition-colors uppercase font-bold ${proMode ? 'border-[#669bbc] text-[#669bbc] hover:bg-[#669bbc] hover:text-[#001f30]' : 'border-[#003049] text-[#003049] hover:bg-[#003049] hover:text-white'}`}
            >
              <Download size={16} />
              <span className="hidden sm:inline">Sample</span>
            </button>
            <div className="relative">
              <input
                type="file"
                id="file-upload"
                className="hidden"
                accept=".pdf"
                onChange={handleFileUpload}
                disabled={uploading}
              />
              <label
                htmlFor="file-upload"
                className={`flex items-center gap-2 px-4 py-2 sm:px-6 border-2 bg-[#c1121f] hover:bg-[#780000] text-white cursor-pointer transition-colors uppercase font-bold active:translate-x-[2px] active:translate-y-[2px] ${proMode ? 'border-[#669bbc] shadow-[4px_4px_0px_0px_#669bbc] active:shadow-[2px_2px_0px_0px_#669bbc]' : 'border-[#003049] shadow-[4px_4px_0px_0px_#003049] active:shadow-[2px_2px_0px_0px_#003049]'} ${uploading ? 'opacity-60 pointer-events-none' : ''}`}
              >
                {uploading ? <Loader2 size={16} className="animate-spin" /> : <Upload size={16} />}
                <span className="hidden sm:inline">{uploading ? (uploadStatus || 'Processing') : 'Upload PDF'}</span>
                <span className="sm:hidden">{uploading ? 'Wait' : 'Upload'}</span>
              </label>
            </div>
          </div>
        </div>
      </nav>

      {proMode ? (
        <ProLayout trendData={trendData} />
      ) : (
      <main className="max-w-7xl mx-auto px-4 sm:px-8 mt-12 space-y-12">
        
        {/* Massive Hero Number */}
        <div className="py-8 reveal-2 border-y-2 border-[#003049] bg-white/50 backdrop-blur-sm px-8 flex flex-col md:flex-row items-center justify-between">
          <div>
            <h2 className="text-[120px] leading-none font-serif text-[#c1121f] tracking-tighter">
              ₹{totalSpend.toFixed(2)}
            </h2>
            <p className="text-[#003049] font-mono font-bold uppercase tracking-widest text-sm mt-2">Total Amount Spent</p>
          </div>
          <div className="hidden md:block text-right font-mono text-[#669bbc] text-sm uppercase">
            <p>System Status: <span className="text-[#c1121f] font-bold">Online</span></p>
            <p>Transactions: <span className="text-[#003049] font-bold">{txnPagination.total}</span></p>
          </div>
        </div>

        {/* Top Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 reveal-3">
          
          <div className="playful-card p-0 lg:col-span-2 flex flex-col overflow-hidden">
            <div className="p-6 border-b-2 border-[#003049] bg-[#003049] text-white flex items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <Newspaper size={20} className="text-[#c1121f]" />
                <h3 className="text-xl font-serif tracking-wide uppercase">Financial Markets News (India)</h3>
              </div>
              <span className="px-3 py-1 bg-[#c1121f] text-[10px] font-bold uppercase tracking-widest text-white border border-[#003049]">Live Feed</span>
            </div>
            
            <div className="flex-1 w-full min-h-[320px] bg-white overflow-y-auto flex flex-col">
              {newsData.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full flex-1 text-[#669bbc] gap-4">
                  <Loader2 size={32} className="animate-spin text-[#c1121f]" />
                  <p className="font-mono text-sm uppercase tracking-widest text-center">Fetching Latest<br/>Financial Headlines</p>
                </div>
              ) : (
                <div className="flex flex-col flex-1">
                  {newsData.slice((newsPage - 1) * NEWS_PER_PAGE, newsPage * NEWS_PER_PAGE).map((news, i) => (
                    <a key={i} href={news.link} target="_blank" rel="noopener noreferrer" className="p-5 border-b border-[#003049]/10 hover:bg-[#fdf0d5] transition-colors group flex flex-col gap-2">
                      <h4 className="font-bold text-[#003049] text-lg font-serif group-hover:text-[#c1121f] transition-colors leading-tight line-clamp-2">{news.title}</h4>
                      <span className="text-[10px] font-bold text-[#669bbc] uppercase tracking-wider font-mono">{news.pubDate}</span>
                    </a>
                  ))}
                </div>
              )}
            </div>

            {newsData.length > 0 && (
              <div className="p-4 bg-[#fdf0d5] border-t-2 border-[#003049]">
                <Pagination
                  currentPage={newsPage}
                  totalPages={Math.ceil(newsData.length / NEWS_PER_PAGE)}
                  totalItems={newsData.length}
                  perPage={NEWS_PER_PAGE}
                  onPageChange={setNewsPage}
                />
              </div>
            )}
          </div>

          <div className="playful-card flex flex-col overflow-hidden">
            <div className="p-6 border-b-2 border-[#003049] bg-[#003049] text-white">
              <h3 className="text-xl font-serif tracking-wide uppercase">Allocation</h3>
            </div>
            <div className="flex-1 min-h-[300px] p-6 bg-white">
              <SpendingChart data={chartData} />
            </div>
          </div>
        </div>

        {/* Middle Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 reveal-4">
          
          <div className="playful-card h-[500px] overflow-hidden flex flex-col">
            <div className="p-6 border-b-2 border-[#003049] bg-[#c1121f] text-white">
              <h3 className="text-xl font-serif tracking-wide uppercase">Ask SmartSpend AI</h3>
            </div>
            <div className="flex-1 overflow-hidden bg-white">
              <ChatBot />
            </div>
          </div>

          <div className="playful-card flex flex-col overflow-hidden bg-white">
            <div className="p-6 border-b-2 border-[#003049] bg-[#003049] text-white flex items-center gap-3">
              <CreditCard size={20} className="text-[#669bbc]" />
              <h3 className="text-xl font-serif tracking-wide uppercase">Active Subscriptions</h3>
            </div>
            
            <div className="relative flex-1">
              {subsLoading && (
                <div className="absolute inset-0 bg-[#fdf0d5]/80 flex items-center justify-center z-10 backdrop-blur-sm">
                  <Loader2 size={32} className="animate-spin text-[#c1121f]" />
                </div>
              )}
              {subscriptions.length > 0 && (
                <div className="w-full">
                  {/* Column Headers */}
                  <div className="grid grid-cols-[1fr_auto_auto] gap-4 px-5 py-2 bg-[#fdf0d5] border-b border-[#003049]/20 text-[10px] font-bold uppercase tracking-widest text-[#669bbc] font-mono">
                    <span>Service</span>
                    <span className="text-center">Billing</span>
                    <span className="text-right">Amount</span>
                  </div>
                  {subscriptions.map((sub, i) => (
                    <div key={i} className="grid grid-cols-[1fr_auto_auto] gap-4 items-center px-5 py-4 border-b border-[#003049]/10 hover:bg-[#fdf0d5] transition-colors group">
                      <div className="font-bold text-[#003049] text-base font-serif truncate">{sub.name}</div>
                      <div className="text-[10px] font-bold text-[#c1121f] uppercase tracking-wider font-mono border border-[#c1121f]/30 px-2 py-0.5 rounded-sm whitespace-nowrap">{sub.frequency}</div>
                      <div className="font-bold text-base text-[#003049] font-mono text-right group-hover:text-[#c1121f] transition-colors">₹{sub.amount.toFixed(2)}</div>
                    </div>
                  ))}
                </div>
              )}
              {subscriptions.length === 0 && !subsLoading && (
                <div className="flex flex-col h-full items-center justify-center text-[#669bbc] gap-3 p-8">
                  <FileText size={40} className="opacity-50" />
                  <p className="font-mono text-sm uppercase tracking-widest text-center">No Subscriptions<br/>Detected</p>
                </div>
              )}
            </div>
            
            <div className="p-4 bg-[#fdf0d5] border-t-2 border-[#003049]">
              <Pagination
                currentPage={subsPagination.page}
                totalPages={subsPagination.total_pages}
                totalItems={subsPagination.total}
                perPage={subsPagination.per_page}
                onPageChange={handleSubsPageChange}
              />
            </div>

          </div>
        </div>

        {/* Bottom Section */}
        <div id="transactions-section" className="playful-card overflow-hidden bg-white reveal-4" style={{ animationDelay: '0.9s' }}>
          <div className="p-6 border-b-2 border-[#003049] bg-[#003049] text-white flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <FileText size={20} className="text-[#fdf0d5]" />
              <h3 className="text-xl font-serif tracking-wide uppercase">General Ledger</h3>
            </div>
            {txnPagination.total > 0 && (
              <span className="px-3 py-1 bg-[#c1121f] border border-white text-white font-mono font-bold text-xs uppercase tracking-widest">
                {txnPagination.total} records
              </span>
            )}
          </div>
          
          <div className="overflow-x-auto relative">
            {txnLoading && (
              <div className="absolute inset-0 bg-[#fdf0d5]/80 flex items-center justify-center z-10 backdrop-blur-sm">
                <Loader2 size={32} className="animate-spin text-[#c1121f]" />
              </div>
            )}
            <table className="w-full text-left friendly-table font-mono text-sm">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Merchant</th>
                  <th>Classification</th>
                  <th className="text-right">Amount</th>
                  <th className="text-center">Flags</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((txn) => (
                  <tr key={txn.id} className="transition-colors group">
                    <td className="text-[#669bbc]">{txn.date}</td>
                    <td className="font-bold text-[#003049] font-serif text-lg">{txn.description}</td>
                    <td>
                      <span className="inline-flex items-center px-2 py-0.5 border border-[#003049] text-[10px] font-bold bg-[#fdf0d5] text-[#003049] uppercase tracking-widest">
                        {txn.category}
                      </span>
                    </td>
                    <td className="text-right font-bold text-[#003049] text-base group-hover:text-[#c1121f] transition-colors">
                      ₹{txn.amount.toFixed(2)}
                    </td>
                    <td className="text-center">
                      {txn.is_anomaly && (
                        <div className="flex justify-center">
                          <div className="bg-[#c1121f] p-1 text-white animate-pulse">
                            <ShieldAlert size={16} />
                          </div>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
                {transactions.length === 0 && !txnLoading && (
                  <tr>
                    <td colSpan={5} className="text-center py-20">
                      <div className="flex flex-col items-center text-[#669bbc]">
                        <FileText size={48} className="mb-4 opacity-40" />
                        <p className="text-lg font-bold font-serif text-[#003049]">Ledger Empty</p>
                        <p className="mt-1 text-xs uppercase tracking-widest">Awaiting PDF Ingestion</p>
                      </div>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          
          <div className="p-4 bg-[#fdf0d5] border-t-2 border-[#003049]">
            <Pagination
              currentPage={txnPagination.page}
              totalPages={txnPagination.total_pages}
              totalItems={txnPagination.total}
              perPage={txnPagination.per_page}
              onPageChange={handleTxnPageChange}
            />
          </div>
        </div>
      </main>
      )}
    </div>
  );
}
