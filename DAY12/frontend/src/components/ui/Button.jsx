import { cn } from "../../lib/utils";

function Button({
  children,
  type = "button",
  variant = "default",
  size = "default",
  disabled = false,
  className = "",
  ...props
}) {
  const variants = {
    default: "bg-blue-600 text-white hover:bg-blue-700",
    secondary: "bg-gray-200 text-gray-900 hover:bg-gray-300",
    destructive: "bg-red-600 text-white hover:bg-red-700",
    outline: "border border-gray-300 bg-white text-gray-900 hover:bg-gray-50",
    ghost: "bg-transparent text-gray-700 hover:bg-gray-100",
  };
  const sizes = {
    default: "px-4 py-2",
    small: "px-3 py-1.5 text-sm",
    large: "px-6 py-3",
  };
  return (
    <button
      type={type}
      disabled={disabled}
      className={cn(
        "inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 disabled:pointer-events-none disabled:opacity-50",
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}

export default Button;
