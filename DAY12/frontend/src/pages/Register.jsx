import { Link, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { registerUser } from "../services/authService";
import { registerSchema } from "../schemas/authSchema";
import FormField from "../components/forms/FormField";
import Button from "../components/ui/Button";
import ThemeToggle from "../components/ui/ThemeToggle";

function Register() {
  const navigate = useNavigate();
  const [serverError, setServerError] = useState("");
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm({ resolver: zodResolver(registerSchema), defaultValues: { username: "", email: "", password: "" } });

  const onSubmit = async (formData) => {
    setServerError("");
    try {
      await registerUser(formData);
      navigate("/login");
    } catch (error) {
      setServerError(error.response?.data?.detail || "Registration failed.");
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4 dark:from-gray-950 dark:to-gray-900">
      <div className="fixed right-4 top-4 z-10"><ThemeToggle /></div>
      <section className="w-full max-w-md rounded-2xl bg-white p-8 shadow-xl dark:bg-gray-900" aria-labelledby="register-heading">
        <div className="mb-8 text-center"><h1 id="register-heading" className="text-3xl font-bold text-gray-900 dark:text-white">Task Manager</h1><p className="mt-2 text-gray-500">Create your account.</p></div>
        {serverError && <div className="mb-4 rounded-md bg-red-50 p-3 text-sm text-red-700" role="alert">{serverError}</div>}
        <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-5">
          <FormField id="username" label="Username" error={errors.username?.message} required><input id="username" type="text" autoComplete="username" aria-invalid={Boolean(errors.username)} {...register("username")} className="w-full rounded-md border border-gray-300 bg-white px-3 py-2.5 shadow-sm dark:bg-gray-800 dark:text-white" /></FormField>
          <FormField id="email" label="Email" error={errors.email?.message} required><input id="email" type="email" autoComplete="email" aria-invalid={Boolean(errors.email)} {...register("email")} className="w-full rounded-md border border-gray-300 bg-white px-3 py-2.5 shadow-sm dark:bg-gray-800 dark:text-white" /></FormField>
          <FormField id="password" label="Password" error={errors.password?.message} required><input id="password" type="password" autoComplete="new-password" aria-invalid={Boolean(errors.password)} {...register("password")} className="w-full rounded-md border border-gray-300 bg-white px-3 py-2.5 shadow-sm dark:bg-gray-800 dark:text-white" /></FormField>
          <Button type="submit" size="large" disabled={isSubmitting} className="w-full">{isSubmitting ? "Creating Account..." : "Register"}</Button>
        </form>
        <p className="mt-6 text-center text-sm text-gray-600 dark:text-gray-300">Already have an account? <Link to="/login" className="font-medium text-blue-600 hover:underline">Login</Link></p>
      </section>
    </main>
  );
}

export default Register;
