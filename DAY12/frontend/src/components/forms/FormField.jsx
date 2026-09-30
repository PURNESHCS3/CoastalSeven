function FormField({ id, label, error, required = false, children, description }) {
  return (
    <div className="space-y-1">
      <label htmlFor={id} className="block text-sm font-medium text-gray-700 dark:text-gray-200">
        {label}{required && <span className="ml-1 text-red-600" aria-hidden="true">*</span>}
      </label>
      {description && <p id={`${id}-description`} className="text-xs text-gray-500">{description}</p>}
      {children}
      {error && <p id={`${id}-error`} className="text-sm text-red-600" role="alert">{error}</p>}
    </div>
  );
}

export default FormField;
