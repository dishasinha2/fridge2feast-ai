import React, { useState, useRef } from 'react';
import { Camera, Upload, RefreshCw, Sparkles, AlertCircle, Video, Image as ImageIcon } from 'lucide-react';
import { SAMPLE_FRIDGE_PRESETS, PresetFridge } from '../data/sampleData';

interface FridgeScannerProps {
  onAnalyzeImage: (base64Image: string, mimeType: string) => Promise<void>;
  onSelectPreset: (preset: PresetFridge) => void;
  isAnalyzing: boolean;
  error: string | null;
}

export const FridgeScanner: React.FC<FridgeScannerProps> = ({
  onAnalyzeImage,
  onSelectPreset,
  isAnalyzing,
  error,
}) => {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [mimeType, setMimeType] = useState<string>('image/jpeg');
  const [isCameraActive, setIsCameraActive] = useState<boolean>(false);
  const [isDragOver, setIsDragOver] = useState<boolean>(false);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  const processFile = (file: File) => {
    if (!file.type.startsWith('image/')) {
      alert('Please upload a valid image file (JPG, PNG, WEBP).');
      return;
    }
    setMimeType(file.type);
    const reader = new FileReader();
    reader.onload = (event) => {
      if (event.target?.result) {
        setSelectedImage(event.target.result as string);
        stopCamera();
      }
    };
    reader.readAsDataURL(file);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      processFile(file);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) {
      processFile(file);
    }
  };

  const startCamera = async () => {
    setSelectedImage(null);
    setIsCameraActive(true);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } },
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }
    } catch (err) {
      console.error('Camera access denied or unequipped:', err);
      setIsCameraActive(false);
      alert('Could not access device camera. Please upload an image file instead.');
    }
  };

  const captureCameraPhoto = () => {
    if (!videoRef.current) return;
    const canvas = document.createElement('canvas');
    canvas.width = videoRef.current.videoWidth || 1280;
    canvas.height = videoRef.current.videoHeight || 720;
    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
      const dataUrl = canvas.toDataURL('image/jpeg', 0.9);
      setSelectedImage(dataUrl);
      setMimeType('image/jpeg');
      stopCamera();
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach((track) => track.stop());
      videoRef.current.srcObject = null;
    }
    setIsCameraActive(false);
  };

  const handleRemoveImage = () => {
    setSelectedImage(null);
    stopCamera();
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleTriggerAnalyze = () => {
    if (selectedImage) {
      onAnalyzeImage(selectedImage, mimeType);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 py-4">
      {/* SECTION TITLE & SUBTITLE */}
      <div className="text-center space-y-2">
        <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-xs font-extrabold rounded-full">
          <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
          ✨ Gemini Vision
        </span>
        <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
          📸 Scan Your Fridge
        </h1>
        <p className="text-slate-300 text-sm max-w-xl mx-auto">
          "Show us what's available. We'll discover what's possible."
        </p>
      </div>

      {/* SCANNER CONTAINER CARD */}
      <div className="bg-slate-900 rounded-3xl border border-slate-800 p-6 sm:p-8 shadow-xl space-y-6">
        {isCameraActive ? (
          <div className="relative rounded-2xl overflow-hidden bg-slate-950 aspect-video max-h-[500px] flex items-center justify-center border-2 border-emerald-500 shadow-2xl">
            <video ref={videoRef} className="w-full h-full object-cover" autoPlay playsInline muted />

            <div className="absolute top-4 right-4 z-10">
              <button
                onClick={stopCamera}
                className="p-2 bg-slate-900/80 hover:bg-slate-900 text-white rounded-full backdrop-blur-md"
                title="Close camera"
              >
                ✕
              </button>
            </div>

            <div className="absolute bottom-6 inset-x-0 flex justify-center">
              <button
                onClick={captureCameraPhoto}
                className="px-8 py-3.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black rounded-2xl shadow-xl flex items-center gap-2"
              >
                <Camera className="w-5 h-5" />
                <span>Capture Fridge Photo</span>
              </button>
            </div>
          </div>
        ) : selectedImage ? (
          /* IMAGE PREVIEW & ACTIONS */
          <div className="space-y-6">
            <div className="relative rounded-2xl overflow-hidden bg-slate-950 aspect-video max-h-[440px] flex items-center justify-center border border-slate-800">
              <img
                src={selectedImage}
                alt="Selected fridge"
                className="w-full h-full object-contain"
              />
              <button
                onClick={handleRemoveImage}
                disabled={isAnalyzing}
                className="absolute top-3 right-3 p-2 bg-slate-900/80 hover:bg-rose-900/80 text-slate-300 hover:text-rose-200 rounded-xl backdrop-blur-md transition-colors"
                title="Remove photo"
              >
                ✕
              </button>
            </div>

            {/* POLISHED AI STATUS IF ANALYZING */}
            {isAnalyzing && (
              <div className="p-5 bg-slate-800/90 rounded-2xl border border-emerald-500/40 space-y-3">
                <div className="flex items-center gap-2 text-emerald-400 font-extrabold text-sm">
                  <RefreshCw className="w-4 h-4 animate-spin text-emerald-400" />
                  <span>✨ Gemini Vision • Analyzing your ingredients...</span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-slate-300 pt-1">
                  <div className="flex items-center gap-1.5 text-emerald-300 font-semibold">
                    <span>✓</span> Processing image in-memory
                  </div>
                  <div className="flex items-center gap-1.5 text-emerald-300 font-semibold">
                    <span>✓</span> Identifying vegetables, dairy & pantry
                  </div>
                  <div className="flex items-center gap-1.5 text-emerald-300 font-semibold">
                    <span>✓</span> Estimating portions & confidence
                  </div>
                  <div className="flex items-center gap-1.5 text-emerald-300 font-semibold">
                    <span>✓</span> Validating zero-waste potential
                  </div>
                </div>
              </div>
            )}

            {/* GRACEFUL ERROR CARD FOR 503 / 429 / TRANSIENT FAILURES */}
            {error && (
              <div className="p-5 rounded-2xl bg-rose-950/40 border border-rose-500/40 text-rose-200 space-y-3">
                <div className="flex items-center gap-2.5">
                  <Sparkles className="w-5 h-5 text-rose-400 flex-shrink-0" />
                  <p className="font-extrabold text-white text-base">Gemini Vision temporarily unavailable</p>
                </div>
                <p className="text-slate-300 text-sm leading-relaxed">
                  {error}
                </p>
              </div>
            )}

            {/* ACTION BUTTONS */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <button
                onClick={handleTriggerAnalyze}
                disabled={isAnalyzing}
                id="analyze-fridge-btn"
                className={`w-full sm:w-auto px-8 py-4 rounded-2xl font-black text-base flex items-center justify-center gap-3 shadow-xl transition-all ${
                  isAnalyzing
                    ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700'
                    : error
                    ? 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-950/50 hover:scale-[1.02] active:scale-[0.98]'
                    : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-950/50 hover:scale-[1.02] active:scale-[0.98]'
                }`}
              >
                {error ? (
                  <>
                    <RefreshCw className="w-5 h-5" />
                    <span>🔄 Try Again</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    <span>🔍 Analyze My Fridge</span>
                  </>
                )}
              </button>

              <button
                onClick={() => {
                  if (fileInputRef.current) fileInputRef.current.click();
                }}
                disabled={isAnalyzing}
                id="retake-image-btn"
                className="w-full sm:w-auto px-6 py-4 bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-sm rounded-2xl border border-slate-700 flex items-center justify-center gap-2 transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
                <span>Upload Different Photo</span>
              </button>
            </div>
          </div>
        ) : (
          /* DROPZONE / INPUT SELECTOR */
          <div className="space-y-6">
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-3xl p-10 sm:p-14 text-center cursor-pointer transition-all duration-300 flex flex-col items-center justify-center gap-4 ${
                isDragOver
                  ? 'border-emerald-500 bg-emerald-950/20'
                  : 'border-slate-700 hover:border-emerald-500/60 bg-slate-800/40 hover:bg-slate-800/70'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/jpg,image/png,image/webp"
                onChange={handleFileChange}
                className="hidden"
                id="file-upload-input"
              />

              <div className="w-16 h-16 rounded-2xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center border border-emerald-500/20">
                <Upload className="w-8 h-8" />
              </div>

              <div className="space-y-1">
                <p className="text-white font-extrabold text-base sm:text-lg">
                  Drag and drop your fridge photo here
                </p>
                <p className="text-slate-400 text-xs sm:text-sm">
                  Supports JPG, JPEG, PNG, WEBP
                </p>
              </div>

              <div className="pt-2 flex flex-wrap items-center justify-center gap-3">
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    startCamera();
                  }}
                  className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-xs rounded-xl shadow-md flex items-center gap-2"
                >
                  <Video className="w-4 h-4 text-white" />
                  <span>📷 Open Camera</span>
                </button>

                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    fileInputRef.current?.click();
                  }}
                  className="px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 font-extrabold text-xs rounded-xl border border-slate-700 flex items-center gap-2"
                >
                  <ImageIcon className="w-4 h-4 text-emerald-400" />
                  <span>📁 Upload Photo</span>
                </button>
              </div>
            </div>

            {/* PRESET SAMPLER BAR */}
            <div className="pt-4 border-t border-slate-800 space-y-3">
              <div className="flex items-center justify-between text-xs text-slate-400 font-bold">
                <span>Or test with a pre-loaded sample:</span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {SAMPLE_FRIDGE_PRESETS.map((preset) => (
                  <button
                    key={preset.id}
                    onClick={() => onSelectPreset(preset)}
                    className="p-2.5 rounded-xl border border-slate-800 hover:border-emerald-500/50 bg-slate-800/40 hover:bg-slate-800/80 flex items-center gap-3 text-left transition-all group"
                  >
                    <img
                      src={preset.imageUrl}
                      alt={preset.title}
                      className="w-12 h-12 rounded-lg object-cover flex-shrink-0"
                    />
                    <div className="min-w-0">
                      <p className="font-extrabold text-white text-xs group-hover:text-emerald-400 truncate">
                        {preset.title}
                      </p>
                      <p className="text-[10px] text-slate-400 truncate">{preset.badge}</p>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
