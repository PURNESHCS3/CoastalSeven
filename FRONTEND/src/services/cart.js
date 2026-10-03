import api from "./api";

export const getCart = async () => {
  const { data } = await api.get("/cart/");
  return data;
};

export const addToCart = async (productId, quantity = 1) => {
  const { data } = await api.post("/cart/add", {
    product_id: productId,
    quantity,
  });
  return data;
};

export const removeFromCart = async (productId) => {
  const { data } = await api.delete(`/cart/${productId}`);
  return data;
};