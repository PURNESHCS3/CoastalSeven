import { z } from "zod";

export const projectSchema = z.object({
  name: z.string().trim().min(1, "Project name is required.").max(100, "Project name cannot exceed 100 characters."),
  description: z.string().trim().max(1000, "Description cannot exceed 1000 characters."),
  priority: z.enum(["low", "medium", "high"]),
});
