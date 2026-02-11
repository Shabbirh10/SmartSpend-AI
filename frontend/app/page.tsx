'use client';

import { useState, useEffect } from 'react';
import { uploadStatement, getTransactions, getTrends, getSubscriptions, downloadDemoStatement } from '../lib/api';
import { SpendingChart } from '../components/dashboard/spending-chart';
import { ChatBot } from '../components/dashboard/chat-bot';
import { Upload, FileText, AlertCircle, Download, TrendingUp, CreditCard } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

interface Transaction {
  id: number;
  date: string;
  description: string;
  amount: number;
  category: string;
  is_anomaly: boolean;
}

export default function Dashboard() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [uploading, setUploading] = useState(false);
  const [chartData, setChartData] = useState<{ name: string; value: number }[]>([]);
  const [trendData, setTrendData] = useState<{ date: string; amount: number }[]>([]);
  const [subscriptions, setSubscriptions] = useState<{ name: string; amount: number; frequency: string }[]>([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const res = await getTransactions();
      setTransactions(res.data);
      processChartData(res.data);

      const trends = await getTrends();
      setTrendData(trends.data);

      const subs = await getSubscriptions();
      setSubscriptions(subs.data);

    } catch (error) {
      console.error("Failed to fetch data", error);
    }
  };

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
    try {
      await uploadStatement(e.target.files[0]);
      await fetchData(); // Refresh data
    } catch (error) {
      console.error("Upload failed", error);
      alert("Upload failed!");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6 md:p-8 font-sans">
      <div className="max-w-7xl mx-auto space-y-6">

        {/* Header */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 tracking-tight">SmartSpend AI</h1>
            <p className="text-gray-500">Intelligent Financial Assistant</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={downloadDemoStatement}
              className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition font-medium"
            >
              <Download size={18} />
              Sample PDF
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
                className={`flex items-center gap-2 px-5 py-2.5 bg-blue-600 text-white rounded-lg cursor-pointer hover:bg-blue-700 transition font-medium shadow-md shadow-blue-200 ${uploading ? 'opacity-50' : ''}`}
              >
                <Upload size={18} />
                {uploading ? 'Analyzing...' : 'Upload Statement'}
              </label>
            </div>
          </div>
        </header>

        {/* Top Section: Charts & Chat */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Spending Distribution */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h2 className="text-lg font-semibold mb-4 text-gray-800">Spending Breakdown</h2>
            <SpendingChart data={chartData} />
          </div>

          {/* AI Chatbot */}
          <div className="lg:col-span-2">
            <ChatBot />
          </div>
        </div>

        {/* Middle Section: Trends & Subscriptions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Trend Chart */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <div className="flex items-center gap-2 mb-6">
              <div className="p-2 bg-purple-100 text-purple-600 rounded-lg">
                <TrendingUp size={20} />
              </div>
              <h2 className="text-lg font-semibold text-gray-800">Spending Trends</h2>
            </div>
            <div className="h-[200px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trendData}>
                  <XAxis dataKey="date" stroke="#9ca3af" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="#9ca3af" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `$${value}`} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                    formatter={(value: number) => [`$${value}`, 'Amount']}
                  />
                  <Line type="monotone" dataKey="amount" stroke="#8b5cf6" strokeWidth={3} dot={{ strokeWidth: 2, r: 4 }} activeDot={{ r: 6 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Subscriptions */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <div className="flex items-center gap-2 mb-6">
              <div className="p-2 bg-green-100 text-green-600 rounded-lg">
                <CreditCard size={20} />
              </div>
              <h2 className="text-lg font-semibold text-gray-800">Recurring Subscriptions</h2>
            </div>
            <div className="space-y-3">
              {subscriptions.map((sub, i) => (
                <div key={i} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <div>
                    <div className="font-medium text-gray-900">{sub.name}</div>
                    <div className="text-xs text-gray-500">{sub.frequency}</div>
                  </div>
                  <div className="font-semibold text-gray-700">${sub.amount.toFixed(2)}</div>
                </div>
              ))}
              {subscriptions.length === 0 && (
                <p className="text-gray-400 text-sm text-center py-4">No subscriptions detected yet.</p>
              )}
            </div>
          </div>
        </div>

        {/* Bottom Section: Transactions Table */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h2 className="text-lg font-semibold mb-6 text-gray-800">Recent Transactions</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left text-gray-500">
              <thead className="text-xs text-gray-700 uppercase bg-gray-50/50">
                <tr>
                  <th className="px-6 py-4 rounded-l-lg">Date</th>
                  <th className="px-6 py-4">Description</th>
                  <th className="px-6 py-4">Category</th>
                  <th className="px-6 py-4 text-right">Amount</th>
                  <th className="px-6 py-4 text-center rounded-r-lg">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {transactions.map((txn) => (
                  <tr key={txn.id} className="bg-white hover:bg-gray-50/50 transition duration-150">
                    <td className="px-6 py-4">{txn.date}</td>
                    <td className="px-6 py-4 font-medium text-gray-900">{txn.description}</td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700">
                        {txn.category}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right font-medium">${txn.amount.toFixed(2)}</td>
                    <td className="px-6 py-4 text-center">
                      {txn.is_anomaly && (
                        <div className="flex justify-center group relative">
                          <AlertCircle size={18} className="text-red-500 cursor-help" />
                          <span className="absolute bottom-full mb-2 bg-gray-800 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition whitespace-nowrap">
                            High Value Transaction
                          </span>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
                {transactions.length === 0 && (
                  <tr>
                    <td colSpan={5} className="text-center py-12">
                      <div className="flex flex-col items-center text-gray-400">
                        <FileText size={48} className="mb-3 opacity-50" />
                        <p className="text-base">No transactions found.</p>
                        <p className="text-sm">Upload a statement or generate demo data to begin.</p>
                      </div>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
