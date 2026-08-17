import { useCallback, useState } from "react";

interface FileDropzoneProps {
  file: File | null;
  onFileChange: (file: File | null) => void;
}

export function FileDropzone({ file, onFileChange }: FileDropzoneProps) {
  const [isDragging, setIsDragging] = useState(false);

  const handleFiles = useCallback(
    (files: FileList | null) => {
      const next = files?.[0];
      if (!next) return;
      onFileChange(next);
    },
    [onFileChange],
  );

  return (
    <label
      className={`flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed px-6 py-12 text-center transition ${
        isDragging ? "border-teal-600 bg-teal-50" : "border-slate-300 bg-white hover:border-teal-500"
      }`}
      onDragOver={(event) => {
        event.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={(event) => {
        event.preventDefault();
        setIsDragging(false);
        handleFiles(event.dataTransfer.files);
      }}
    >
      <input
        type="file"
        accept="application/pdf,.pdf"
        className="hidden"
        onChange={(event) => handleFiles(event.target.files)}
      />
      <p className="text-sm font-medium text-slate-800">
        {file ? file.name : "Arraste um PDF ou clique para selecionar"}
      </p>
      <p className="mt-1 text-xs text-slate-500">Somente arquivos PDF</p>
    </label>
  );
}
