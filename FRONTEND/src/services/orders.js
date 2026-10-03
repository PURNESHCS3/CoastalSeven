import api from "./api";

export const createOrder = async (deliveryAddress) => {
  const { data } = await api.post("/orders/", {
    delivery_address: deliveryAddress,
  });
  return data;
};

export const getOrders = async () => {
  const { data } = await api.get("/orders/");
  return data;
};

export const getOrder = async (orderId) => {
  const { data } = await api.get(`/orders/${orderId}`);
  return data;
};

export const cancelOrder = async (orderId) => {
  const { data } = await api.post(`/orders/${orderId}/cancel`);
  return data;
};