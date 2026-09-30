import { CheckCircle, XCircle, X } from "lucide-react";

function Toast({ message, type = "success", onClose }) {
  if (!message) return null;
  const success = type === "success";
  return (
    <div className={`fixed right-5 top-5 z-[100] flex min-w-[300px] items-start gap-3 rounded-lg border bg-white p-4 shadow-lg ${success ? "border-green-200" : "border-red-200"}`} role="alert" aria-live="polite">
      {success ? <CheckCircle className="mt-0.5 text-green-600" size={20} /> : <XCircle className="mt-0.5 text-red-600" size={20} />}
      <p className={`flex-1 text-sm ${success ? "text-green-800" : "text-red-800"}`}>{message}</p>
      <button type="button" onClick={onClose} aria-label="Close notification" className="text-gray-400 hover:text-gray-700"><X size={18} /></button>
    </div>
  );
}

export default Toast;
