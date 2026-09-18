import React, { useRef, useState } from 'react';

export default function FileUpload({ label, sublabel, accept, multiple, files, onFilesChange, icon }) {
  const inputRef = useRef(null);
  const [dragOver, setDragOver] = useState(false);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const dropped = Array.from(e.dataTransfer.files);
    if (dropped.length) {
      onFilesChange(multiple ? [...files, ...dropped] : [dropped[0]]);
    }
  };

  const handleSelect = (e) => {
    const selected = Array.from(e.target.files);
    if (selected.length) {
      onFilesChange(multiple ? [...files, ...selected] : [selected[0]]);
    }
    e.target.value = '';
  };

  const removeFile = (index) => {
    onFilesChange(files.filter((_, i) => i !== index));
  };

  const formatSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
  };

  return (
    <div className="w-full">
      <label className="block text-sm font-semibold text-navy mb-1.5 uppercase tracking-wider">
        {label}
      </label>
      {sublabel && (
        <p className="text-xs text-gray-400 mb-3">{sublabel}</p>
      )}

      <div
        onClick={() => inputRef.current?.click()}
        onDrop={handleDrop}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        className={`relative border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all ${
          dragOver
            ? 'border-primary bg-primary/5 scale-[1.01]'
            : files.length > 0
              ? 'border-green-300 bg-green-50/50'
              : 'border-gray-200 hover:border-primary/40 hover:bg-primary/[0.02]'
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept={accept || '.pdf'}
          multiple={multiple}
          onChange={handleSelect}
          className="hidden"
        />

        <div className="flex flex-col items-center gap-3">
          {icon || (
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
              files.length > 0 ? 'bg-green-100' : 'bg-gray-100'
            }`}>
              {files.length > 0 ? (
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#22c55e" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
              ) : (
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                  <polyline points="17 8 12 3 7 8"/>
                  <line x1="12" y1="3" x2="12" y2="15"/>
                </svg>
              )}
            </div>
          )}

          {files.length === 0 ? (
            <>
              <p className="text-gray-600 font-medium">
                Drop your file here or <span className="text-primary font-semibold">browse</span>
              </p>
              <p className="text-xs text-gray-400">PDF files supported</p>
            </>
          ) : (
            <p className="text-green-600 font-medium">
              {files.length} file{files.length > 1 ? 's' : ''} selected
            </p>
          )}
        </div>
      </div>

      {/* File list */}
      {files.length > 0 && (
        <div className="mt-3 space-y-2">
          {files.map((file, i) => (
            <div key={i} className="flex items-center justify-between bg-gray-50 rounded-xl px-4 py-3 group">
              <div className="flex items-center gap-3 min-w-0">
                <div className="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center flex-shrink-0">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#FF8400" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                  </svg>
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-medium text-gray-700 truncate">{file.name}</p>
                  <p className="text-xs text-gray-400">{formatSize(file.size)}</p>
                </div>
              </div>
              <button
                onClick={(e) => { e.stopPropagation(); removeFile(i); }}
                className="p-1.5 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors opacity-0 group-hover:opacity-100"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18"/>
                  <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
