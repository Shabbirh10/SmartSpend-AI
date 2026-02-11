'use client';

import { useState } from 'react';
import { chatWithAI } from '@/lib/api';
import { Send, Bot, User } from 'lucide-react';
import clsx from 'clsx';

interface Message {
    role: 'user' | 'assistant';
    content: string;
}

export function ChatBot() {
    const [messages, setMessages] = useState<Message[]>([
        { role: 'assistant', content: 'Hello! I am your AI Financial Assistant. Ask me about your spending!' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMsg = { role: 'user' as const, content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        try {
            const res = await chatWithAI(input);
            setMessages(prev => [...prev, { role: 'assistant', content: res.response }]);
        } catch (error) {
            setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encounted an error. Make sure Ollama is running!' }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-[400px] bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            <div className="bg-blue-600 text-white p-4 font-semibold flex items-center gap-2">
                <Bot size={20} />
                Financial Assistant
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((m, i) => (
                    <div key={i} className={clsx(
                        "flex gap-3 max-w-[80%]",
                        m.role === 'user' ? "ml-auto flex-row-reverse" : ""
                    )}>
                        <div className={clsx(
                            "w-8 h-8 rounded-full flex items-center justify-center shrink-0",
                            m.role === 'user' ? "bg-gray-200" : "bg-blue-100 text-blue-600"
                        )}>
                            {m.role === 'user' ? <User size={16} /> : <Bot size={16} />}
                        </div>
                        <div className={clsx(
                            "p-3 rounded-lg text-sm",
                            m.role === 'user' ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-800"
                        )}>
                            {m.content}
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="flex gap-3">
                        <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center">
                            <Bot size={16} />
                        </div>
                        <div className="text-gray-400 text-sm flex items-center">Thinking...</div>
                    </div>
                )}
            </div>

            <div className="p-4 border-t flex gap-2">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                    placeholder="Ask a question..."
                    className="flex-1 border rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                    onClick={handleSend}
                    disabled={loading}
                    className="bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                    <Send size={18} />
                </button>
            </div>
        </div>
    );
}
