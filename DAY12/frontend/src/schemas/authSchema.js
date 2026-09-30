import { z } from "zod";

export const loginSchema = z.object({
  email: z.string().trim().email("Please enter a valid email address."),
  password: z.string().min(6, "Password must contain at least 6 characters."),
});

export const registerSchema = z.object({
  username: z.string().trim().min(3, "Username must contain at least 3 characters.").max(50, "Username cannot exceed 50 characters."),
  email: z.string().trim().email("Please enter a valid email address."),
  password: z.string().min(6, "Password must contain at least 6 characters.").max(100, "Password cannot exceed 100 characters."),
});
