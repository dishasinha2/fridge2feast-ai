import React, { useState } from 'react';
import { FileCode, Download, Copy, Check, Terminal, ExternalLink, Sparkles } from 'lucide-react';

export const StreamlitCodeViewer: React.FC = () => {
  const [activeFile, setActiveFile] = useState<'app.py' | 'utils_pandas.py' | 'requirements.txt' | 'README.md'>('app.py');
  const [copied, setCopied] = useState<boolean>(false);

  const filesContent: Record<string, string> = {
    'app.py': `import os
import pandas as pd
import streamlit as st
from PIL import Image
from utils_pandas import process_ingredients_dataframe, export_recipe_markdown

st.set_page_config(page_title="Fridge2Feast AI 🥗", page_icon="🥗", layout="wide")

st.sidebar.title("🥗 Fridge2Feast AI")
st.sidebar.caption("Streamlit + Python + Pandas Engine")

nav = st.sidebar.radio("Navigation", ["📷 Fridge Scanner", "📋 Ingredient Pandas Table", "🍳 Recipe Generator"])

if "ingredients_df" not in st.session_state:
    st.session_state.ingredients_df = pd.DataFrame()

if nav == "📷 Fridge Scanner":
    st.title("📷 Streamlit Fridge Vision Scanner")
    camera_photo = st.camera_input("Capture Fridge Photo")
    uploaded_file = st.file_uploader("Or Upload Image", type=["jpg", "png"])
    
    if camera_photo or uploaded_file:
        st.success("Photo received! Running Gemini AI analysis into Pandas DataFrame...")

elif nav == "📋 Ingredient Pandas Table":
    st.title("📋 Pandas Dataframe Editor")
    df = st.session_state.ingredients_df
    if not df.empty:
        edited_df = st.data_editor(df, use_container_width=True)
        st.session_state.ingredients_df = edited_df
        st.bar_chart(edited_df["category"].value_counts())

elif nav == "🍳 Recipe Generator":
    st.title("🍳 Gemini Zero-Waste Recipes")
    if st.button("Generate Recipes"):
        st.success("Generating 3 zero-waste recipes using Pandas inventory...")
`,
    'utils_pandas.py': `import pandas as pd

def process_ingredients_dataframe(raw_items):
    df = pd.DataFrame(raw_items)
    df["confidence_pct"] = (df["confidence"] * 100).astype(int)
    return df

def calculate_waste_score(df, utilization_pct):
    if df.empty: return 0
    return int((len(df[df['included'] == True]) / len(df)) * 40 + utilization_pct * 0.6)
`,
    'requirements.txt': `streamlit>=1.35.0
pandas>=2.2.0
google-genai>=0.1.1
pillow>=10.0.0
plotly>=5.20.0
`,
    'README.md': `# 🥗 Fridge2Feast AI - Streamlit + Python + Pandas App

## Local Quickstart
1. Install dependencies: \`pip install -r requirements.txt\`
2. Set API key: \`export GEMINI_API_KEY="your_api_key"\`
3. Launch Streamlit: \`streamlit run app.py\`
`,
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(filesContent[activeFile]);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([filesContent[activeFile]], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = activeFile;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6 py-4">
      {/* Header */}
      <div className="text-center space-y-2">
        <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-rose-100 text-rose-800 text-xs font-bold rounded-full border border-rose-200">
          <FileCode className="w-3.5 h-3.5 text-rose-600" />
          Streamlit + Python Codebase Inspector
        </span>
        <h1 className="text-3xl font-extrabold text-stone-900 tracking-tight">
          📄 Source Code & Streamlit App Architecture
        </h1>
        <p className="text-stone-600 text-sm max-w-xl mx-auto">
          Inspect, copy, and download the native Python, Pandas, and Streamlit code files.
        </p>
      </div>

      {/* Main Code Box */}
      <div className="bg-stone-900 text-stone-100 rounded-3xl border border-stone-800 p-6 shadow-xl space-y-4">
        {/* File Tabs & Actions */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-stone-800">
          <div className="flex flex-wrap items-center gap-2">
            {(['app.py', 'utils_pandas.py', 'requirements.txt', 'README.md'] as const).map((file) => (
              <button
                key={file}
                onClick={() => setActiveFile(file)}
                className={`px-3.5 py-2 rounded-xl text-xs font-mono font-bold transition-all ${
                  activeFile === file
                    ? 'bg-rose-600 text-white shadow-md'
                    : 'bg-stone-800 text-stone-400 hover:bg-stone-700 hover:text-stone-200'
                }`}
              >
                {file}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              className="px-3.5 py-2 bg-stone-800 hover:bg-stone-700 text-stone-300 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-colors"
            >
              {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
              <span>{copied ? 'Copied!' : 'Copy Code'}</span>
            </button>

            <button
              onClick={handleDownload}
              className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-xl text-xs font-bold flex items-center gap-1.5 shadow-md transition-all"
            >
              <Download className="w-4 h-4" />
              <span>Download {activeFile}</span>
            </button>
          </div>
        </div>

        {/* Code Content */}
        <pre className="bg-stone-950 text-emerald-400 font-mono text-xs p-5 rounded-2xl border border-stone-800 overflow-x-auto leading-relaxed shadow-inner max-h-[500px]">
          {filesContent[activeFile]}
        </pre>
      </div>
    </div>
  );
};
