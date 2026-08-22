import React, { useState } from 'react';
import {
  ChefHat,
  Camera,
  ListCheck,
  UtensilsCrossed,
  BookMarked,
  BarChart3,
  Sparkles,
  ArrowRight,
  CheckCircle2,
  Search,
  Menu,
  X,
  Clock,
  Leaf,
  ShieldCheck,
  HelpCircle,
  Heart
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

interface PublicLandingPageProps {
  onGoToFeature?: (featureTab: 'scan' | 'review' | 'recipes' | 'feastbook' | 'analytics') => void;
}

export const PublicLandingPage: React.FC<PublicLandingPageProps> = ({ onGoToFeature }) => {
  const { setCurrentAuthView, continueAsGuest } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState<boolean>(false);

  const handleFeatureClick = (tab: 'scan' | 'review' | 'recipes' | 'feastbook' | 'analytics') => {
    // Continue as guest and navigate directly to feature
    continueAsGuest();
    if (onGoToFeature) {
      onGoToFeature(tab);
    }
  };

  const scrollToSection = (id: string) => {
    setMobileMenuOpen(false);
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-emerald-500 selection:text-white">
      {/* 4. LANDING PAGE NAVBAR */}
      <header className="sticky top-0 z-50 bg-slate-900/90 backdrop-blur-md border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center text-slate-950 font-black shadow-lg shadow-emerald-950/50">
                <ChefHat className="w-6 h-6 text-slate-950" />
              </div>
              <span className="font-extrabold text-xl tracking-tight text-white">
                🍳 Fridge2Feast
              </span>
            </div>

            {/* Nav links */}
            <nav className="hidden md:flex items-center gap-8 text-xs font-bold text-slate-300">
              <button
                onClick={() => scrollToSection('how-it-works')}
                className="hover:text-emerald-400 transition-colors"
              >
                How It Works
              </button>
              <button
                onClick={() => scrollToSection('features')}
                className="hover:text-emerald-400 transition-colors"
              >
                Features
              </button>
              <button
                onClick={() => scrollToSection('sustainability')}
                className="hover:text-emerald-400 transition-colors"
              >
                About & Sustainability
              </button>
            </nav>

            {/* Right side Auth CTAs */}
            <div className="hidden md:flex items-center gap-3">
              <button
                onClick={() => setCurrentAuthView('login')}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-extrabold rounded-xl transition-all"
              >
                Log In
              </button>
              <button
                onClick={() => setCurrentAuthView('signup')}
                className="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-extrabold rounded-xl shadow-md shadow-emerald-950/40 transition-all hover:scale-[1.02]"
              >
                ✨ Get Started
              </button>
            </div>

            {/* Mobile Hamburger toggle */}
            <div className="md:hidden">
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="p-2 text-slate-300 hover:text-white"
              >
                {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Dropdown Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-slate-900 border-b border-slate-800 px-4 py-4 space-y-3 animate-fadeIn">
            <button
              onClick={() => scrollToSection('how-it-works')}
              className="block w-full text-left py-2 text-xs font-bold text-slate-300 hover:text-emerald-400"
            >
              How It Works
            </button>
            <button
              onClick={() => scrollToSection('features')}
              className="block w-full text-left py-2 text-xs font-bold text-slate-300 hover:text-emerald-400"
            >
              Features
            </button>
            <button
              onClick={() => scrollToSection('sustainability')}
              className="block w-full text-left py-2 text-xs font-bold text-slate-300 hover:text-emerald-400"
            >
              About & Sustainability
            </button>
            <div className="pt-2 border-t border-slate-800 flex flex-col gap-2">
              <button
                onClick={() => {
                  setMobileMenuOpen(false);
                  setCurrentAuthView('signup');
                }}
                className="w-full py-2.5 bg-emerald-600 text-white font-extrabold text-xs rounded-xl text-center"
              >
                ✨ Get Started
              </button>
              <button
                onClick={() => {
                  setMobileMenuOpen(false);
                  setCurrentAuthView('login');
                }}
                className="w-full py-2.5 bg-slate-800 text-slate-200 border border-slate-700 font-extrabold text-xs rounded-xl text-center"
              >
                Log In
              </button>
              <button
                onClick={() => {
                  setMobileMenuOpen(false);
                  continueAsGuest();
                }}
                className="w-full py-2.5 bg-slate-900 text-slate-400 border border-slate-800 font-bold text-xs rounded-xl text-center"
              >
                Continue as Guest
              </button>
            </div>
          </div>
        )}
      </header>

      {/* 3. & 5. HERO SECTION */}
      <section className="relative overflow-hidden py-16 sm:py-24 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-emerald-500/10 rounded-full blur-[120px] pointer-events-none"></div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center relative z-10">
          {/* LEFT: Headline & Actions */}
          <div className="lg:col-span-7 space-y-6 text-center lg:text-left">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 text-xs font-extrabold uppercase tracking-wider">
              <span>♻️ AI-POWERED ZERO-WASTE COOKING</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight text-white leading-[1.1]">
              Turn What's Left <br />
              <span className="text-emerald-400">
                Into What's Next.
              </span>
            </h1>

            <p className="text-slate-300 text-base sm:text-lg font-normal leading-relaxed max-w-2xl mx-auto lg:mx-0">
              "Transform the ingredients already in your kitchen into personalized meals with AI — while helping reduce food waste."
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-3 pt-2">
              <button
                onClick={() => setCurrentAuthView('signup')}
                className="w-full sm:w-auto px-8 py-4 bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-base rounded-2xl shadow-xl shadow-emerald-950/50 flex items-center justify-center gap-2.5 transition-all hover:scale-[1.02] active:scale-[0.98]"
              >
                <Sparkles className="w-5 h-5 text-white" />
                <span>✨ Get Started</span>
              </button>

              <button
                onClick={() => setCurrentAuthView('login')}
                className="w-full sm:w-auto px-7 py-4 bg-slate-800 hover:bg-slate-700/80 border border-slate-700 text-slate-200 font-bold text-base rounded-2xl transition-all"
              >
                <span>Log In</span>
              </button>

              <button
                onClick={continueAsGuest}
                className="w-full sm:w-auto px-6 py-4 bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-400 hover:text-slate-200 font-semibold text-xs sm:text-sm rounded-2xl transition-all"
              >
                <span>Continue as Guest</span>
              </button>
            </div>
          </div>

          {/* RIGHT: Product Showcase Panel */}
          <div className="lg:col-span-5">
            <div className="bg-slate-900/90 rounded-3xl border border-slate-800 p-6 shadow-2xl space-y-5 relative">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800 text-xs font-extrabold text-slate-400">
                <span className="flex items-center gap-1.5 text-emerald-400">
                  <Camera className="w-4 h-4" />
                  AI Kitchen Showcase
                </span>
                <span className="bg-emerald-950 text-emerald-300 border border-emerald-500/30 px-2.5 py-0.5 rounded-full text-[10px]">
                  Visual Product Demo
                </span>
              </div>

              {/* Detected items */}
              <div className="space-y-2">
                <p className="text-[11px] font-black uppercase tracking-wider text-slate-400">
                  🥕 Ingredients Detected
                </p>
                <div className="flex flex-wrap gap-2">
                  <span className="px-3 py-1.5 bg-slate-800 border border-slate-700 text-xs font-bold text-slate-200 rounded-xl flex items-center gap-1.5">
                    🍅 Tomato
                  </span>
                  <span className="px-3 py-1.5 bg-slate-800 border border-slate-700 text-xs font-bold text-slate-200 rounded-xl flex items-center gap-1.5">
                    🥚 Eggs
                  </span>
                  <span className="px-3 py-1.5 bg-slate-800 border border-slate-700 text-xs font-bold text-slate-200 rounded-xl flex items-center gap-1.5">
                    🥬 Spinach
                  </span>
                </div>
              </div>

              {/* Arrow */}
              <div className="flex justify-center text-emerald-400 py-1">
                <ArrowRight className="w-5 h-5 rotate-90" />
              </div>

              {/* AI Recommendation Output Card */}
              <div className="p-4 bg-slate-950 rounded-2xl border border-emerald-500/30 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-black text-emerald-400 flex items-center gap-1">
                    <Sparkles className="w-3.5 h-3.5" />
                    AI Recommendation
                  </span>
                  <span className="text-[10px] font-extrabold bg-emerald-600 text-white px-2 py-0.5 rounded-md">
                    Best Match
                  </span>
                </div>

                <h3 className="font-extrabold text-white text-base">
                  Spinach Masala Omelette
                </h3>

                <div className="flex items-center gap-4 text-xs font-bold text-slate-300 pt-1">
                  <span className="flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5 text-emerald-400" />
                    15 min
                  </span>
                  <span className="flex items-center gap-1 text-emerald-400">
                    <Leaf className="w-3.5 h-3.5" />
                    91% ingredients used
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 6. TRUST / VALUE SECTION */}
      <section className="py-12 bg-slate-900/60 border-y border-slate-800/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-6 bg-slate-900 rounded-2xl border border-slate-800 space-y-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center font-bold">
                <Search className="w-5 h-5" />
              </div>
              <h3 className="font-black text-white text-lg">🔍 AI Ingredient Detection</h3>
              <p className="text-slate-300 text-xs sm:text-sm leading-relaxed">
                "Identify available ingredients instantly from a simple fridge photo."
              </p>
            </div>

            <div className="p-6 bg-slate-900 rounded-2xl border border-slate-800 space-y-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center font-bold">
                <ChefHat className="w-5 h-5" />
              </div>
              <h3 className="font-black text-white text-lg">🍳 Personalized Recipes</h3>
              <p className="text-slate-300 text-xs sm:text-sm leading-relaxed">
                "Recipes adapt to your diet, cuisine preference, preparation time and budget."
              </p>
            </div>

            <div className="p-6 bg-slate-900 rounded-2xl border border-slate-800 space-y-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center font-bold">
                <Leaf className="w-5 h-5" />
              </div>
              <h3 className="font-black text-white text-lg">♻️ Waste-Smart Cooking</h3>
              <p className="text-slate-300 text-xs sm:text-sm leading-relaxed">
                "Prioritize ingredients you already have to maximize utilization and cut food waste."
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 7. HOW IT WORKS */}
      <section id="how-it-works" className="py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-12">
        <div className="text-center space-y-3 max-w-2xl mx-auto">
          <span className="text-xs font-black uppercase tracking-widest text-emerald-400">
            Simple 4-Step Process
          </span>
          <h2 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
            How Fridge2Feast Works
          </h2>
          <p className="text-slate-400 text-sm">
            From fridge shelf to delicious meal in under 20 minutes.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="p-6 bg-slate-900 rounded-3xl border border-slate-800 space-y-3 relative">
            <span className="text-2xl font-black text-emerald-400">01</span>
            <h3 className="font-extrabold text-white text-lg">SCAN</h3>
            <p className="text-slate-300 text-xs leading-relaxed">
              "Capture what's inside your fridge."
            </p>
          </div>

          <div className="p-6 bg-slate-900 rounded-3xl border border-slate-800 space-y-3 relative">
            <span className="text-2xl font-black text-emerald-400">02</span>
            <h3 className="font-extrabold text-white text-lg">VERIFY</h3>
            <p className="text-slate-300 text-xs leading-relaxed">
              "Confirm what the AI detected."
            </p>
          </div>

          <div className="p-6 bg-slate-900 rounded-3xl border border-slate-800 space-y-3 relative">
            <span className="text-2xl font-black text-emerald-400">03</span>
            <h3 className="font-extrabold text-white text-lg">PERSONALIZE</h3>
            <p className="text-slate-300 text-xs leading-relaxed">
              "Choose your preferences."
            </p>
          </div>

          <div className="p-6 bg-slate-900 rounded-3xl border border-slate-800 space-y-3 relative">
            <span className="text-2xl font-black text-emerald-400">04</span>
            <h3 className="font-extrabold text-white text-lg">COOK</h3>
            <p className="text-slate-300 text-xs leading-relaxed">
              "Follow your personalized recipe."
            </p>
          </div>
        </div>
      </section>

      {/* 8. FEATURE SHOWCASE */}
      <section id="features" className="py-16 bg-slate-900/40 border-y border-slate-800/80 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto space-y-12">
          <div className="text-center space-y-3 max-w-2xl mx-auto">
            <span className="text-xs font-black uppercase tracking-widest text-emerald-400">
              Complete Culinary Toolkit
            </span>
            <h2 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
              Everything Your Kitchen Needs
            </h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            <div
              onClick={() => handleFeatureClick('scan')}
              className="p-6 bg-slate-900 hover:bg-slate-850 rounded-3xl border border-slate-800 hover:border-emerald-500/50 cursor-pointer transition-all space-y-3 group"
            >
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center font-bold">
                <Camera className="w-5 h-5" />
              </div>
              <h3 className="font-extrabold text-white text-lg group-hover:text-emerald-400 transition-colors">
                📸 Smart Fridge Scanner
              </h3>
              <p className="text-slate-300 text-xs leading-relaxed">
                AI-powered ingredient detection from photo upload or live camera scan.
              </p>
            </div>

            <div
              onClick={() => handleFeatureClick('review')}
              className="p-6 bg-slate-900 hover:bg-slate-850 rounded-3xl border border-slate-800 hover:border-emerald-500/50 cursor-pointer transition-all space-y-3 group"
            >
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center font-bold">
                <ListCheck className="w-5 h-5" />
              </div>
              <h3 className="font-extrabold text-white text-lg group-hover:text-emerald-400 transition-colors">
                🥕 Intelligent Inventory
              </h3>
              <p className="text-slate-300 text-xs leading-relaxed">
                Review and manage detected ingredients with category breakdowns and freshness confidence.
              </p>
            </div>

            <div
              onClick={() => handleFeatureClick('recipes')}
              className="p-6 bg-slate-900 hover:bg-slate-850 rounded-3xl border border-slate-800 hover:border-emerald-500/50 cursor-pointer transition-all space-y-3 group"
            >
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center font-bold">
                <UtensilsCrossed className="w-5 h-5" />
              </div>
              <h3 className="font-extrabold text-white text-lg group-hover:text-emerald-400 transition-colors">
                🍝 Recipe Studio
              </h3>
              <p className="text-slate-300 text-xs leading-relaxed">
                Generate personalized recipes tailored to your exact dietary and budget constraints.
              </p>
            </div>

            <div
              onClick={() => handleFeatureClick('analytics')}
              className="p-6 bg-slate-900 hover:bg-slate-850 rounded-3xl border border-slate-800 hover:border-emerald-500/50 cursor-pointer transition-all space-y-3 group"
            >
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center font-bold">
                <Leaf className="w-5 h-5" />
              </div>
              <h3 className="font-extrabold text-white text-lg group-hover:text-emerald-400 transition-colors">
                ♻️ Waste Score
              </h3>
              <p className="text-slate-300 text-xs leading-relaxed">
                See how efficiently your ingredients are used and track overall kitchen utilization score.
              </p>
            </div>

            <div
              onClick={() => handleFeatureClick('recipes')}
              className="p-6 bg-slate-900 hover:bg-slate-850 rounded-3xl border border-slate-800 hover:border-emerald-500/50 cursor-pointer transition-all space-y-3 group"
            >
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center font-bold">
                <ChefHat className="w-5 h-5" />
              </div>
              <h3 className="font-extrabold text-white text-lg group-hover:text-emerald-400 transition-colors">
                👨‍🍳 AI Sous-Chef
              </h3>
              <p className="text-slate-300 text-xs leading-relaxed">
                Get recipe-specific cooking help, substitution ideas, and instant step tweaks.
              </p>
            </div>

            <div
              onClick={() => handleFeatureClick('feastbook')}
              className="p-6 bg-slate-900 hover:bg-slate-850 rounded-3xl border border-slate-800 hover:border-emerald-500/50 cursor-pointer transition-all space-y-3 group"
            >
              <div className="w-10 h-10 rounded-xl bg-amber-500/10 text-amber-400 flex items-center justify-center font-bold">
                <Heart className="w-5 h-5 fill-current" />
              </div>
              <h3 className="font-extrabold text-white text-lg group-hover:text-amber-400 transition-colors">
                ❤️ Feastbook
              </h3>
              <p className="text-slate-300 text-xs leading-relaxed">
                Save your favorite recipes and keep track of your kitchen history for easy re-cooking.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 9. SUSTAINABILITY SECTION */}
      <section id="sustainability" className="py-20 px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto text-center space-y-6">
        <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-emerald-500/20 text-emerald-300 text-xs font-black uppercase tracking-wider border border-emerald-500/30">
          🌱 Zero-Waste Vision
        </div>

        <h2 className="text-3xl sm:text-5xl font-black text-white tracking-tight leading-tight">
          Cook What You Have.
        </h2>

        <p className="text-slate-300 text-base sm:text-lg leading-relaxed max-w-3xl mx-auto">
          "Fridge2Feast helps you make better use of ingredients that are already available instead of starting every meal from a shopping list."
        </p>

        <div className="pt-4 flex justify-center gap-4">
          <button
            onClick={() => setCurrentAuthView('signup')}
            className="px-8 py-3.5 bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-sm rounded-2xl shadow-xl shadow-emerald-950/50 transition-all"
          >
            Join Fridge2Feast AI Today
          </button>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="border-t border-slate-800 bg-slate-900 py-10 text-xs text-slate-400">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <ChefHat className="w-5 h-5 text-emerald-400" />
            <span className="font-black text-white">Fridge2Feast AI</span>
            <span>— Turn What's Left Into What's Next.</span>
          </div>

          <div className="flex items-center gap-6">
            <button onClick={() => setCurrentAuthView('login')} className="hover:text-white font-bold">
              Log In
            </button>
            <button onClick={() => setCurrentAuthView('signup')} className="hover:text-white font-bold">
              Sign Up
            </button>
            <button onClick={continueAsGuest} className="hover:text-white font-bold">
              Guest Mode
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
};
