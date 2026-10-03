import { useEffect, useMemo, useState } from "react";
import { Search, SlidersHorizontal } from "lucide-react";
import ProductCard from "../components/ProductCard";
import { Input } from "../components/ui/input";
import { getProducts } from "../services/products";

export default function Products() {
  const [products, setProducts] = useState([]);
  const [query, setQuery] = useState("");
  const [stockFilter, setStockFilter] = useState("all");
  const [sort, setSort] = useState("default");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    const loadProducts = async (showLoading = false) => {
      if (showLoading) setLoading(true);
      setError("");

      try {
        const latestProducts = await getProducts();
        if (active) setProducts(latestProducts);
      } catch (err) {
        if (active) setError(err.response?.data?.detail || "Unable to load products.");
      } finally {
        if (active && showLoading) setLoading(false);
      }
    };

    const refreshProducts = () => loadProducts();
    const handleVisibilityChange = () => {
      if (document.visibilityState === "visible") refreshProducts();
    };

    loadProducts(true);
    window.addEventListener("focus", refreshProducts);
    document.addEventListener("visibilitychange", handleVisibilityChange);

    return () => {
      active = false;
      window.removeEventListener("focus", refreshProducts);
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, []);

  const filtered = useMemo(() => {
    const result = products.filter((product) => {
      const text = `${product.name} ${product.description || ""}`.toLowerCase();
      const matchesSearch = text.includes(query.toLowerCase());
      const matchesStock =
        stockFilter === "all" ||
        (stockFilter === "available" && product.stock > 0) ||
        (stockFilter === "out" && product.stock === 0);
      return matchesSearch && matchesStock;
    });

    return [...result].sort((a, b) => {
      if (sort === "price-low") return a.price - b.price;
      if (sort === "price-high") return b.price - a.price;
      if (sort === "name") return a.name.localeCompare(b.name);
      return 0;
    });
  }, [products, query, stockFilter, sort]);

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      <section className="mb-8 rounded-2xl bg-slate-900 px-6 py-10 text-white sm:px-10">
        <p className="mb-2 text-sm font-medium text-slate-300">DAY 13 E-COMMERCE</p>
        <h1 className="text-3xl font-bold sm:text-4xl">Find your next product from Shophub!</h1>
      </section>

      <div className="mb-8 grid gap-3 md:grid-cols-[1fr_180px_200px]">
        <div className="relative">
          <Search className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
          <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search products..." className="pl-9" />
        </div>
        <select value={stockFilter} onChange={(e) => setStockFilter(e.target.value)} className="h-10 rounded-lg border border-slate-300 bg-white px-3 text-sm">
          <option value="all">All stock</option>
          <option value="available">In stock</option>
          <option value="out">Out of stock</option>
        </select>
        <select value={sort} onChange={(e) => setSort(e.target.value)} className="h-10 rounded-lg border border-slate-300 bg-white px-3 text-sm">
          <option value="default">Sort: Default</option>
          <option value="price-low">Price: Low to high</option>
          <option value="price-high">Price: High to low</option>
          <option value="name">Name: A to Z</option>
        </select>
      </div>

      <div className="mb-4 flex items-center gap-2 text-sm text-slate-500">
        <SlidersHorizontal className="h-4 w-4" /> {filtered.length} product{filtered.length !== 1 ? "s" : ""} found
      </div>

      {loading && <div className="py-16 text-center text-slate-500">Loading products...</div>}
      {error && <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">{error}</div>}

      {!loading && !error && filtered.length === 0 && (
        <div className="rounded-xl border bg-white p-12 text-center text-slate-500">No products match your search.</div>
      )}

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {filtered.map((product) => <ProductCard key={product.id} product={product} />)}
      </div>
    </div>
  );
}