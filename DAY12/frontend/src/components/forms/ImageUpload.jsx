import { useCallback, useEffect, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, X } from "lucide-react";

function ImageUpload({ value, onChange, error }) {
  const [preview, setPreview] = useState("");

  useEffect(() => {
    if (!value) {
      setPreview("");
      return undefined;
    }
    const url = typeof value === "string" ? value : URL.createObjectURL(value);
    setPreview(url);
    return () => {
      if (typeof value !== "string") URL.revokeObjectURL(url);
    };
  }, [value]);

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) onChange(file);
  }, [onChange]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "image/jpeg": [".jpg", ".jpeg"], "image/png": [".png"], "image/webp": [".webp"] },
    maxFiles: 1,
    maxSize: 5 * 1024 * 1024,
  });

  return (
    <div className="space-y-3">
      <div {...getRootProps()} className={`cursor-pointer rounded-xl border-2 border-dashed p-8 text-center transition ${isDragActive ? "border-blue-500 bg-blue-50" : "border-gray-300 bg-gray-50 hover:border-blue-400"}`}>
        <input {...getInputProps()} aria-label="Upload project image" />
        <Upload className="mx-auto mb-3 text-gray-500" size={32} />
        <p className="font-medium text-gray-700">{isDragActive ? "Drop the image here..." : "Drag & drop an image here"}</p>
        <p className="mt-1 text-sm text-gray-500">or click to select an image</p>
        <p className="mt-2 text-xs text-gray-400">PNG, JPG or WEBP — maximum 5 MB</p>
      </div>
      {preview && (
        <div className="relative overflow-hidden rounded-xl border bg-white p-2">
          <img src={preview} alt="Selected project image preview" className="mx-auto max-h-64 rounded-lg object-contain" />
          <button type="button" onClick={() => onChange(null)} aria-label="Remove selected image" className="absolute right-3 top-3 rounded-full bg-red-600 p-2 text-white hover:bg-red-700"><X size={16} /></button>
        </div>
      )}
      {error && <p className="text-sm text-red-600" role="alert">{error}</p>}
    </div>
  );
}

export default ImageUpload;
