import React, { useState } from 'react';
import { ChefHat, Send, User, RefreshCw, HelpCircle } from 'lucide-react';
import { Recipe, UserPreferences, RecipeAiChatMessage } from '../types';

interface RecipeAiAssistantProps {
  recipe: Recipe;
  preferences: UserPreferences;
}

const QUICK_ACTIONS = [
  { label: '🥛 Dairy-Free Swap', query: 'How can I make this recipe completely dairy-free?' },
  { label: '💪 Increase Protein', query: 'How can I add extra protein to this dish?' },
  { label: '🌶 Make It Less Spicy', query: 'How do I tone down the spice level for sensitive palates?' },
  { label: '🔥 No Oven', query: 'How can I cook this on a stovetop or pan without an oven?' },
  { label: '💰 Make It Cheaper', query: 'What budget-friendly ingredient swaps can reduce missing cost?' },
];

export const RecipeAiAssistant: React.FC<RecipeAiAssistantProps> = ({ recipe, preferences }) => {
  const [messages, setMessages] = useState<RecipeAiChatMessage[]>([
    {
      id: 'welcome',
      role: 'assistant',
      text: `Hello! I'm your AI Sous-Chef for "${recipe.title}". Ask me about ingredient swaps, cooking techniques, or dietary tweaks!`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);

  const [inputQuery, setInputQuery] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const handleSendMessage = async (queryText?: string) => {
    const textToSend = queryText || inputQuery;
    if (!textToSend.trim() || isLoading) return;

    const userMsg: RecipeAiChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      text: textToSend.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputQuery('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/recipe-assistant', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          recipe,
          preferences,
          userQuestion: textToSend.trim(),
        }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Failed to get answer.');

      const botMsg: RecipeAiChatMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        text: data.answer || 'Adjust cooking time and seasoning to your preference.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (error: any) {
      console.error('Error in RecipeAiAssistant:', error);
      const errorMsg: RecipeAiChatMessage = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        text: `Sorry, I couldn't process that question right now: ${error.message || 'Please try again.'}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-slate-900 rounded-3xl border border-slate-800 p-6 sm:p-8 shadow-xl space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold border border-emerald-500/30">
            <ChefHat className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-black text-white">👨‍🍳 Ask Your Sous-Chef</h3>
            <p className="text-slate-400 text-xs">"Your recipe-aware cooking assistant."</p>
          </div>
        </div>

        <span className="text-[10px] font-extrabold bg-emerald-950 text-emerald-400 px-2.5 py-1 rounded-full border border-emerald-500/30">
          Recipe Context Active
        </span>
      </div>

      {/* Quick Actions */}
      <div className="space-y-2">
        <span className="text-xs font-bold text-slate-400 flex items-center gap-1">
          <HelpCircle className="w-3.5 h-3.5 text-emerald-400" />
          Quick Cooking Tweaks:
        </span>
        <div className="flex flex-wrap gap-2">
          {QUICK_ACTIONS.map((action, idx) => (
            <button
              key={idx}
              onClick={() => handleSendMessage(action.query)}
              disabled={isLoading}
              className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 hover:border-emerald-500/50 px-3 py-1.5 rounded-xl font-bold transition-all text-left"
            >
              {action.label}
            </button>
          ))}
        </div>
      </div>

      {/* Chat Messages */}
      <div className="space-y-3 max-h-80 overflow-y-auto p-4 bg-slate-950 rounded-2xl border border-slate-800">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex items-start gap-3 text-xs ${
              msg.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            {msg.role === 'assistant' && (
              <div className="w-7 h-7 rounded-lg bg-emerald-600 text-white flex items-center justify-center font-bold flex-shrink-0 mt-0.5">
                <ChefHat className="w-4 h-4" />
              </div>
            )}

            <div
              className={`p-3.5 rounded-2xl max-w-xl space-y-1 ${
                msg.role === 'user'
                  ? 'bg-emerald-600 text-white rounded-tr-none font-medium'
                  : 'bg-slate-900 text-slate-200 border border-slate-800 rounded-tl-none shadow-md'
              }`}
            >
              <p className="whitespace-pre-line leading-relaxed">{msg.text}</p>
              <span className="block text-[10px] opacity-60 text-right">{msg.timestamp}</span>
            </div>

            {msg.role === 'user' && (
              <div className="w-7 h-7 rounded-lg bg-slate-800 text-slate-300 flex items-center justify-center font-bold flex-shrink-0 mt-0.5">
                <User className="w-4 h-4" />
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="flex items-center gap-2 text-xs text-emerald-400 italic p-2">
            <RefreshCw className="w-3.5 h-3.5 animate-spin" />
            <span>Sous-Chef is thinking...</span>
          </div>
        )}
      </div>

      {/* Input Box */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSendMessage();
        }}
        className="flex items-center gap-2"
      >
        <input
          type="text"
          placeholder="Ask anything about this recipe..."
          value={inputQuery}
          onChange={(e) => setInputQuery(e.target.value)}
          disabled={isLoading}
          className="flex-1 bg-slate-800 border border-slate-700 text-white text-xs rounded-xl px-4 py-3 placeholder-slate-400 focus:outline-none focus:border-emerald-500"
        />
        <button
          type="submit"
          disabled={isLoading || !inputQuery.trim()}
          className="px-4 py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-xs rounded-xl shadow-md disabled:opacity-50 flex items-center gap-1.5"
        >
          <Send className="w-4 h-4" />
          <span>Send</span>
        </button>
      </form>
    </div>
  );
};
