'use client';

import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

// Coolors Palette
const COLORS = ['#003049', '#c1121f', '#669bbc', '#780000', '#fdf0d5'];

interface SpendingChartProps {
    data: { name: string; value: number }[];
}

export function SpendingChart({ data }: SpendingChartProps) {
    if (!data || data.length === 0) {
        return (
            <div className="h-full w-full flex flex-col items-center justify-center text-[#669bbc]">
                <p className="font-bold text-[15px]">No Allocation Data</p>
            </div>
        );
    }
    return (
        <ResponsiveContainer width="100%" height="100%">
            <PieChart>
                <Pie
                    data={data}
                    cx="50%"
                    cy="50%"
                    innerRadius={65}
                    outerRadius={100}
                    paddingAngle={4}
                    dataKey="value"
                    stroke="#ffffff"
                    strokeWidth={2}
                    cornerRadius={8}
                >
                    {data.map((entry, index) => (
                        <Cell 
                          key={`cell-${index}`} 
                          fill={COLORS[index % COLORS.length]} 
                        />
                    ))}
                </Pie>
                <Tooltip 
                    contentStyle={{ 
                        backgroundColor: '#003049', 
                        borderRadius: '16px', 
                        border: 'none', 
                        boxShadow: '0 10px 25px -5px rgba(0, 48, 73, 0.3)',
                        padding: '12px 16px'
                    }}
                    itemStyle={{ color: '#fff', fontWeight: 'bold', fontSize: '15px' }}
                    formatter={(value) => [`₹${Number(value ?? 0).toFixed(2)}`, 'Allocated']}
                />
                <Legend 
                    verticalAlign="bottom" 
                    height={48} 
                    iconType="circle"
                    iconSize={10}
                    wrapperStyle={{ paddingTop: '20px' }}
                    formatter={(value) => <span style={{ color: '#003049', fontSize: '14px', fontWeight: '700', paddingLeft: '4px' }}>{value}</span>}
                />
            </PieChart>
        </ResponsiveContainer>
    );
}
