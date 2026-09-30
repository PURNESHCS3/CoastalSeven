import { Moon, Sun } from "lucide-react";
import { useEffect, useState } from "react";

function ThemeToggle() {
  const [dark, setDark] = useState(() => localStorage.getItem("theme") === "dark");

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    localStorage.setItem("theme", dark ? "dark" : "light");
  }, [dark]);

  return (
    <button type="button" onClick={() => setDark((value) => !value)} aria-label={dark ? "Switch to light mode" : "Switch to dark mode"} className="rounded-md border border-gray-300 bg-white p-2 text-gray-700 hover:bg-gray-100 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:hover:bg-gray-700">
      {dark ? <Sun size={18} /> : <Moon size={18} />}
    </button>
  );
}

export default ThemeToggle;
