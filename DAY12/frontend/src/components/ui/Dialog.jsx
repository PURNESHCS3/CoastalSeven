import { useEffect } from "react";
import { X } from "lucide-react";

function Dialog({ open, onClose, title, children }) {
  useEffect(() => {
    if (!open) return undefined;
    const handleEscape = (event) => {
      if (event.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="dialog-title"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <div className="w-full max-w-lg rounded-xl bg-white p-6 shadow-xl dark:bg-gray-900">
        <div className="mb-4 flex items-center justify-between">
          <h2 id="dialog-title" className="text-xl font-semibold text-gray-900 dark:text-white">{title}</h2>
          <button type="button" onClick={onClose} aria-label="Close dialog" className="rounded-md p-2 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800">
            <X size={20} />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}

export default Dialog;
