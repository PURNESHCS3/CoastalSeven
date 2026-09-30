import { useState } from "react";
import { ChevronDown } from "lucide-react";

function Dropdown({ label, options = [], value, onChange }) {
  const [open, setOpen] = useState(false);
  const selectedOption = options.find((option) => option.value === value);
  return (
    <div className="relative">
      <button type="button" onClick={() => setOpen((current) => !current)} aria-haspopup="listbox" aria-expanded={open} className="flex w-full items-center justify-between rounded-md border border-gray-300 bg-white px-3 py-2 text-left text-sm shadow-sm hover:bg-gray-50">
        <span>{selectedOption?.label || label}</span><ChevronDown size={18} />
      </button>
      {open && (
        <div className="absolute z-30 mt-1 w-full rounded-md border border-gray-200 bg-white py-1 shadow-lg" role="listbox">
          {options.map((option) => (
            <button key={option.value} type="button" role="option" aria-selected={value === option.value} onClick={() => { onChange(option.value); setOpen(false); }} className="block w-full px-3 py-2 text-left text-sm hover:bg-gray-100">
              {option.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default Dropdown;
