import React, { useState } from 'react';
import { ChefHat, Eye, EyeOff, ArrowRight, Sparkles, AlertCircle, ShieldCheck, KeyRound } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

interface LoginPageProps {
  onSwitchToSignup: () => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onSwitchToSignup }) => {
  const { login, continueAsGuest, setCurrentAuthView } = useAuth();

  const [email, setEmail] = useState<string>('disha.sinha2612@gmail.com');
  const [password, setPassword] = useState<string>('');
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [showForgotNotice, setShowForgotNotice] = useState<boolean>(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setShowForgotNotice(false);

    if (!email.trim()) {
      setErrorMsg('Please enter a valid email address.');
      return;
    }
    if (!password) {
      setErrorMsg('Password is required.');
      return;
    }

    setIsSubmitting(true);
    try {
      const res = await login(email, password);
      if (!res.success) {
        setErrorMsg(res.error || 'We couldn\'t sign you in. Please check your credentials.');
      }
    } catch (err: any) {
      setErrorMsg('An unexpected error occurred. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center py-10 px-4 sm:px-6">
      <div className="w-full max-w-md space-y-8 bg-slate-900 border border-slate-800 p-8 sm:p-10 rounded-3xl shadow-2xl relative overflow-hidden">
        {/* Background ambient light */}
        <div className="absolute -top-20 -right-20 w-48 h-48 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>

        {/* Back to Home Header */}
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
          <button
            onClick={() => setCurrentAuthView('landing')}
            className="flex items-center gap-2 text-xs font-bold text-slate-400 hover:text-white transition-colors"
          >
            ← Back to Landing
          </button>
          <span className="text-[10px] font-black uppercase tracking-wider px-2.5 py-1 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-500/30">
            ♻️ Zero-Waste Kitchen
          </span>
        </div>

        {/* Brand Header */}
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-emerald-600 flex items-center justify-center text-slate-950 font-black mx-auto shadow-lg shadow-emerald-950/50">
            <ChefHat className="w-7 h-7 text-slate-950" />
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
            Welcome Back 👋
          </h1>
          <p className="text-slate-400 text-xs sm:text-sm font-medium">
            "Your kitchen has more possibilities waiting."
          </p>
        </div>

        {/* Validation error message */}
        {errorMsg && (
          <div className="p-3.5 rounded-2xl bg-rose-950/80 border border-rose-800/80 text-rose-200 text-xs font-bold flex items-start gap-2.5 animate-fadeIn">
            <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0 mt-0.5" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Forgot Password Notice */}
        {showForgotNotice && (
          <div className="p-3.5 rounded-2xl bg-amber-950/80 border border-amber-800/80 text-amber-200 text-xs font-bold flex items-start gap-2.5">
            <KeyRound className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-extrabold">Password Reset (Coming Soon)</p>
              <p className="text-[11px] font-normal text-amber-300/90 mt-0.5">
                Password recovery service is coming soon. You can enter any demo password or continue as guest below.
              </p>
            </div>
          </div>
        )}

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="space-y-1.5">
            <label className="text-xs font-extrabold text-slate-300 uppercase tracking-wider">
              Email Address
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="disha.sinha2612@gmail.com"
              required
              className="w-full bg-slate-800 border border-slate-700/80 rounded-2xl px-4 py-3 text-xs sm:text-sm font-semibold text-white placeholder-slate-500 outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all shadow-inner"
            />
          </div>

          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="text-xs font-extrabold text-slate-300 uppercase tracking-wider">
                Password
              </label>
              <button
                type="button"
                onClick={() => setShowForgotNotice(true)}
                className="text-xs font-bold text-emerald-400 hover:text-emerald-300 transition-colors"
              >
                Forgot password?
              </button>
            </div>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                required
                className="w-full bg-slate-800 border border-slate-700/80 rounded-2xl pl-4 pr-11 py-3 text-xs sm:text-sm font-semibold text-white placeholder-slate-500 outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all shadow-inner"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200 p-1"
                title={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Primary Action Button */}
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-3.5 bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-sm rounded-2xl shadow-xl shadow-emerald-950/40 flex items-center justify-center gap-2 transition-all hover:scale-[1.01] active:scale-[0.99] disabled:opacity-50"
          >
            <span>{isSubmitting ? 'Signing in...' : 'Log In'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        {/* Divider */}
        <div className="relative my-6 text-center">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-slate-800"></div>
          </div>
          <span className="relative bg-slate-900 px-3 text-[11px] font-extrabold uppercase text-slate-500">
            OR
          </span>
        </div>

        {/* Guest Mode Action */}
        <button
          type="button"
          onClick={continueAsGuest}
          className="w-full py-3 bg-slate-800 hover:bg-slate-700/80 border border-slate-700 text-slate-200 font-bold text-xs rounded-2xl flex items-center justify-center gap-2 transition-all"
        >
          <Sparkles className="w-4 h-4 text-emerald-400" />
          <span>Continue as Guest</span>
        </button>

        {/* Footer switch to Signup */}
        <p className="text-center text-xs font-semibold text-slate-400 pt-2">
          Don't have an account?{' '}
          <button
            onClick={onSwitchToSignup}
            className="text-emerald-400 hover:text-emerald-300 font-extrabold transition-colors underline underline-offset-4"
          >
            Create Account
          </button>
        </p>

        {/* Demo Notice */}
        <div className="pt-2 text-center border-t border-slate-800/60">
          <p className="text-[10px] text-slate-500 flex items-center justify-center gap-1 font-medium">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
            <span>Secure Capstone Demo Session • No credentials saved in plaintext</span>
          </p>
        </div>
      </div>
    </div>
  );
};
