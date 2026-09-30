import { cn } from "../../lib/utils";

function Table({ className, ...props }) {
  return (
    <div className="relative w-full overflow-x-auto">
      <table className={cn("w-full caption-bottom text-sm", className)} {...props} />
    </div>
  );
}

function TableHeader({ className, ...props }) {
  return <thead className={cn("[&_tr]:border-b [&_tr]:border-[var(--border-color)]", className)} {...props} />;
}

function TableBody({ className, ...props }) {
  return <tbody className={cn("[&_tr:last-child]:border-0", className)} {...props} />;
}

function TableFooter({ className, ...props }) {
  return <tfoot className={cn("border-t border-[var(--border-color)] bg-[var(--surface-muted)] font-medium [&>tr]:last:border-b-0", className)} {...props} />;
}

function TableRow({ className, ...props }) {
  return <tr className={cn("border-b border-[var(--border-color)] transition-colors hover:bg-[var(--surface-muted)] data-[state=selected]:bg-[var(--surface-muted)]", className)} {...props} />;
}

function TableHead({ className, ...props }) {
  return <th className={cn("h-12 px-4 text-left align-middle font-medium text-[var(--text-secondary)] [&:has([role=checkbox])]:pr-0", className)} {...props} />;
}

function TableCell({ className, ...props }) {
  return <td className={cn("p-4 align-middle [&:has([role=checkbox])]:pr-0", className)} {...props} />;
}

function TableCaption({ className, ...props }) {
  return <caption className={cn("mt-4 text-sm text-[var(--text-secondary)]", className)} {...props} />;
}

export {
  Table,
  TableHeader,
  TableBody,
  TableFooter,
  TableHead,
  TableRow,
  TableCell,
  TableCaption,
};
