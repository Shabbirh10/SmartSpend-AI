'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Bot, SquareTerminal } from 'lucide-react';
import clsx from 'clsx';

interface Message {
    role: 'user' | 'assistant';
    content: string;
}

export function ChatBot() {
    const [messages, setMessages] = useState<Message[]>([
        { role: 'assistant', content: "Hi there! How can I help you with your finances today?" }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const chatEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, loading]);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMsg = { role: 'user' as const, content: input };
        setMessages(prev => [...prev, userMsg]);
        const currentQuery = input;
        setInput('');
        setLoading(true);

        try {
            const apiBase = process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:8000/api';
            const response = await fetch(`${apiBase}/chat/stream`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: currentQuery }),
            });

            if (!response.body) throw new Error("No response body stream found.");

            setLoading(false);
            setMessages(prev => [...prev, { role: 'assistant', content: '' }]);
            
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let accumulated = "";

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                const textChunk = decoder.decode(value);
                const lines = textChunk.split('\n');
                
                for (const line of lines) {
                    const trimmed = line.trim();
                    if (trimmed.startsWith('data: ')) {
                        try {
                            const dataObj = JSON.parse(trimmed.slice(6));
                            if (dataObj.chunk) {
                                accumulated += dataObj.chunk;
                                setMessages(prev => {
                                    const updated = [...prev];
                                    updated[updated.length - 1] = { role: 'assistant', content: accumulated };
                                    return updated;
                                });
                            } else if (dataObj.error) {
                                accumulated += `\n[ERR: ${dataObj.error}]`;
                                setMessages(prev => {
                                    const updated = [...prev];
                                    updated[updated.length - 1] = { role: 'assistant', content: accumulated };
                                    return updated;
                                });
                            }
                        } catch (e) {
                            // Suppress parse errors
                        }
                    }
                }
            }
        } catch (error: any) {
            setLoading(false);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: `ERR_CONN: ${error.message}`
            }]);
        }
    };

    return (
        <div className="flex flex-col h-full overflow-hidden bg-[#fdf0d5]">
            <div className="flex-1 overflow-y-auto p-6 space-y-6 font-mono text-sm bg-white">
                {messages.map((m, i) => (
                    <div key={i} className={clsx(
                        "flex gap-3 max-w-[90%]",
                        m.role === 'user' ? "ml-auto flex-row-reverse" : ""
                    )}>
                        <div className={clsx(
                            "px-4 py-3 whitespace-pre-wrap leading-relaxed border-2 border-[#003049] shadow-[4px_4px_0px_0px_#003049]",
                            m.role === 'user' 
                                ? "bg-[#c1121f] text-white" 
                                : "bg-[#fdf0d5] text-[#003049]"
                        )}>
                            {m.role === 'assistant' && <div className="text-[10px] uppercase font-bold tracking-widest text-[#669bbc] mb-1">SmartSpend AI</div>}
                            {m.role === 'user' && <div className="text-[10px] uppercase font-bold tracking-widest text-white/70 mb-1 text-right">You</div>}
                            {m.content || '...'}
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="flex gap-3 max-w-[90%]">
                        <div className="px-4 py-3 bg-[#fdf0d5] border-2 border-[#003049] shadow-[4px_4px_0px_0px_#003049] flex items-center gap-2 text-[#003049] uppercase font-bold text-xs tracking-widest">
                            <SquareTerminal size={14} className="animate-pulse" />
                            Thinking...
                        </div>
                    </div>
                )}
                <div ref={chatEndRef} />
            </div>

            <div className="p-4 bg-[#fdf0d5] border-t-2 border-[#003049]">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                        placeholder="Type your question here..."
                        disabled={loading}
                        className="flex-1 bg-white border-2 border-[#003049] px-4 py-3 text-sm font-mono text-[#003049] placeholder-[#669bbc] focus:outline-none focus:bg-[#fcf6eb] disabled:opacity-50 shadow-[4px_4px_0px_0px_#003049]"
                    />
                    <button
                        onClick={handleSend}
                        disabled={loading || !input.trim()}
                        className="bg-[#c1121f] hover:bg-[#780000] active:translate-x-[2px] active:translate-y-[2px] active:shadow-[2px_2px_0px_0px_#003049] text-white px-6 border-2 border-[#003049] disabled:opacity-50 transition-all flex items-center justify-center shadow-[4px_4px_0px_0px_#003049] shrink-0"
                    >
                        <Send size={18} />
                    </button>
                </div>
            </div>
        </div>
    );
}
