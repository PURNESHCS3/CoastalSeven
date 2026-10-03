import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { Card, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { getProduct } from "../services/products";
import { addToCart } from "../services/cart";
import { API_URL } from "../services/api";
import { useAuth } from "../context/AuthContext";

function imageSrc(url) {
  if (!url) return null;
  return url.startsWith("http") ? url : `${API_URL.replace("/api", "")}${url}`;
}

export default function ProductDetails() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [error, setError] = useState("");
  const [cartMessage, setCartMessage] = useState("");
  const [adding, setAdding] = useState(false);

  useEffect(() => {
    getProduct(id).then(setProduct).catch((err) => setError(err.response?.data?.detail || "Product not found."));
  }, [id]);

  if (error) return <div className="mx-auto max-w-4xl px-4 py-16 text-center text-red-600">{error}</div>;
  if (!product) return <div className="py-16 text-center text-slate-500">Loading product...</div>;

  const src = imageSrc(product.image_url);

  const handleAddToCart = async () => {
    if (!user) {
      navigate("/login", { state: { from: `/products/${id}` } });
      return;
    }

    setAdding(true);
    setCartMessage("");
    try {
      await addToCart(product.id, 1);
      setCartMessage("Added to cart.");
    } catch (err) {
      setCartMessage(err.response?.data?.detail || "Could not add this product to your cart.");
    } finally {
      setAdding(false);
    }
  };

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6">
      <Link to="/" className="mb-6 inline-flex items-center gap-2 text-sm text-slate-600 hover:text-slate-900">
        <ArrowLeft className="h-4 w-4" /> Back to products
      </Link>

      <Card className="overflow-hidden">
        <div className="grid md:grid-cols-2">
          <div className="min-h-[360px] bg-slate-100">
            {src ? <img src={src} alt={product.name} className="h-full w-full object-cover" /> : <div className="flex h-full items-center justify-center text-slate-400">No image</div>}
          </div>
          <CardContent className="flex flex-col justify-center p-8">
            <p className="mb-2 text-sm uppercase tracking-wide text-slate-400">Product #{product.id}</p>
            <h1 className="text-3xl font-bold">{product.name}</h1>
            <p className="mt-5 leading-7 text-slate-600">{product.description || "No description available."}</p>
            <div className="mt-8 text-3xl font-bold">₹{Number(product.price).toFixed(2)}</div>
            <p className="mt-2 text-sm text-slate-500">
              {product.stock > 0 ? `${product.stock} units available` : "Currently out of stock"}
            </p>
            {user?.role === "admin" ? (
              <Link to={`/admin/products?edit=${product.id}`} className="mt-6 block">
                <Button className="w-full">Edit product</Button>
              </Link>
            ) : (
              <>
                <Button className="mt-6 w-full" onClick={handleAddToCart} disabled={product.stock === 0 || adding}>
                  {adding ? "Adding..." : product.stock === 0 ? "Out of stock" : "Add to cart"}
                </Button>
                {cartMessage && <p role="status" className="mt-3 text-center text-sm text-slate-600">{cartMessage}</p>}
              </>
            )}
          </CardContent>
        </div>
      </Card>
    </div>
  );
}